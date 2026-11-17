#!/usr/bin/env python3
"""
The Oyster Shack - Agente de Google Reviews.

Cada mañana: trae los reviews nuevos (SerpApi), redacta respuestas con Claude
usando la guía de voz y manda un reporte por email listo para copiar y pegar.

Uso:
  python3 agent.py                      # corrida normal (lo que corre el cron)
  python3 agent.py --find-place "The Oyster Shack Condado San Juan"
  python3 agent.py --export-history 10  # baja respuestas ya publicadas -> history.jsonl
  python3 agent.py --no-email           # genera preview.html en vez de enviar
  python3 agent.py --mock sample_reviews.json --no-email --no-claude   # prueba sin keys
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
STATE_FILE = BASE / "state.json"
HISTORY_FILE = BASE / "history.jsonl"
EXAMPLES_FILE = BASE / "examples.md"
TZ = ZoneInfo("America/Puerto_Rico")
SERPAPI_URL = "https://serpapi.com/search.json"


def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE / ".env")
    except ImportError:
        pass


def env(name, default=None, required=False):
    val = os.getenv(name, default)
    if required and not val:
        sys.exit(f"Falta {name} en .env")
    return val


# ---------------------------------------------------------------- estado

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"seen": []}


def save_state(state):
    state["seen"] = state["seen"][-2000:]
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------- SerpApi

def serpapi(params):
    import requests
    params = {**params, "api_key": env("SERPAPI_KEY", required=True)}
    r = requests.get(SERPAPI_URL, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"SerpApi: {data['error']}")
    return data


def find_place(query):
    data = serpapi({"engine": "google_maps", "q": query, "type": "search", "hl": "en"})
    results = [data["place_results"]] if data.get("place_results") else data.get("local_results", [])
    for p in results[:5]:
        print(f"- {p.get('title')} | {p.get('address')}\n  data_id: {p.get('data_id')}\n  place_id: {p.get('place_id')}\n")
    if not results:
        print("No encontré resultados. Prueba con otra búsqueda.")


def fetch_reviews(max_pages=3, stop_before=None):
    """Trae reviews ordenados del más nuevo al más viejo."""
    params = {"engine": "google_maps_reviews", "sort_by": "newestFirst", "hl": "en"}
    if env("GOOGLE_DATA_ID"):
        params["data_id"] = env("GOOGLE_DATA_ID")
    else:
        params["place_id"] = env("GOOGLE_PLACE_ID", required=True)

    reviews, token = [], None
    for _ in range(max_pages):
        p = dict(params)
        if token:
            p["next_page_token"] = token
        data = serpapi(p)
        page = data.get("reviews", [])
        reviews.extend(page)
        token = (data.get("serpapi_pagination") or {}).get("next_page_token")
        if not token or not page:
            break
        if stop_before and parse_date(page[-1]) and parse_date(page[-1]) < stop_before:
            break
    return reviews


def parse_date(r):
    iso = r.get("iso_date")
    if not iso:
        return None
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def review_text(r):
    ext = r.get("extracted_snippet") or {}
    return (ext.get("original") or r.get("snippet") or "").strip()


def review_id(r):
    return r.get("review_id") or f"{(r.get('user') or {}).get('name')}|{r.get('iso_date')}"


# ---------------------------------------------------------------- Claude

def build_system_prompt():
    parts = [(BASE / "system_prompt.md").read_text(),
             "\n\n# GUÍA DE VOZ\n\n" + (BASE / "voice_guide.md").read_text()]
    if EXAMPLES_FILE.exists():
        parts.append("\n\n# EJEMPLOS REALES PUBLICADOS\n\n" + EXAMPLES_FILE.read_text())
    return "".join(parts)


def draft_reply(client, system_prompt, r):
    user = (r.get("user") or {}).get("name", "")
    payload = {
        "nombre_cliente": user,
        "estrellas": r.get("rating"),
        "subpuntuaciones": r.get("details") or {},
        "fecha": r.get("date"),
        "texto": review_text(r) or "(sin texto, solo calificación)",
        "tiene_fotos": bool(r.get("images")),
    }
    msg = client.messages.create(
        model=env("CLAUDE_MODEL", "claude-sonnet-5-5"),
        max_tokens=800,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "Redacta la respuesta a esta reseña de Google:\n\n"
                   + json.dumps(payload, ensure_ascii=False, indent=2)}],
    )
    raw = "".join(b.text for b in msg.content if b.type == "text").strip()
    raw = re.sub(r"^```(json)?|```$", "", raw).strip()
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        out = {"flag": True, "flag_reason": "No pude leer la respuesta del modelo, revisar.", "reply": raw}
    out["reply"] = clean_reply(out.get("reply", ""))
    if (r.get("rating") or 5) <= 2:
        out["flag"] = True
        out["flag_reason"] = out.get("flag_reason") or "Reseña de 1-2 estrellas."
    return out


EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️]")


def clean_reply(text):
    text = EMOJI_RE.sub("", text)
    text = text.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
    return re.sub(r"[ \t]{2,}", " ", text).strip()


# ---------------------------------------------------------------- reporte

def stars(n):
    n = int(n or 0)
    return "★" * n + "☆" * (5 - n)


def render_html(items, run_date):
    flagged = [i for i in items if i["draft"].get("flag")]
    ready = [i for i in items if not i["draft"].get("flag")]
    avg = sum((i["review"].get("rating") or 0) for i in items) / len(items) if items else 0

    def card(i, color):
        r, d = i["review"], i["draft"]
        name = html.escape((r.get("user") or {}).get("name", "Anónimo"))
        text = html.escape(review_text(r) or "(sin texto, solo calificación)")
        reason = f'<div style="color:#b42318;font-size:13px;margin:6px 0">⚠ {html.escape(d.get("flag_reason",""))}</div>' if d.get("flag") else ""
        link = f' · <a href="{html.escape(r["link"])}" style="color:#555">ver en Google</a>' if r.get("link") else ""
        return f"""
<div style="border-left:4px solid {color};background:#fafafa;padding:14px 16px;margin:14px 0;border-radius:6px">
  <div style="font-size:15px"><b>{name}</b> <span style="color:#d4a017">{stars(r.get('rating'))}</span>
  <span style="color:#888;font-size:12px"> · {html.escape(r.get('date') or '')}{link}</span></div>
  <div style="color:#444;font-size:13px;margin:8px 0;font-style:italic">"{text}"</div>
  {reason}
  <div style="font-size:12px;color:#888;margin-top:10px">RESPUESTA:</div>
  <div style="background:#fff;border:1px solid #ddd;padding:12px;border-radius:4px;font-size:14px;line-height:1.5;white-space:pre-wrap">{html.escape(d.get('reply',''))}</div>
</div>"""

    if not items:
        body = '<p style="font-size:15px">No hay reviews nuevos en Google desde el último reporte.</p>'
    else:
        body = f'<p style="font-size:14px;color:#555">{len(items)} nuevos · promedio {avg:.1f}★</p>'
        if flagged:
            body += f'<h3 style="color:#b42318;margin-top:24px">🚩 REVISAR ANTES DE PUBLICAR ({len(flagged)})</h3>'
            body += "".join(card(i, "#b42318") for i in flagged)
        if ready:
            body += f'<h3 style="color:#1a7f37;margin-top:24px">✅ LISTOS PARA PEGAR ({len(ready)})</h3>'
            body += "".join(card(i, "#1a7f37") for i in ready)

    return f"""<html><body style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:680px;margin:auto;color:#222">
<h2 style="margin-bottom:4px">Reviews de Google · The Oyster Shack</h2>
<div style="color:#888;font-size:13px">{run_date}</div>
{body}
<p style="color:#aaa;font-size:11px;margin-top:30px">Borradores generados automáticamente. Revisa antes de publicar.</p>
</body></html>"""


def render_text(items, run_date):
    lines = [f"Reviews de Google · The Oyster Shack · {run_date}", ""]
    if not items:
        lines.append("No hay reviews nuevos.")
    for i in items:
        r, d = i["review"], i["draft"]
        tag = "REVISAR" if d.get("flag") else "LISTO"
        lines += [f"[{tag}] {(r.get('user') or {}).get('name','Anónimo')} {stars(r.get('rating'))}",
                  f'"{review_text(r)}"',
                  *( [f"Motivo: {d.get('flag_reason')}"] if d.get("flag") else [] ),
                  "Respuesta:", d.get("reply", ""), "-" * 40, ""]
    return "\n".join(lines)


def send_email(subject, html_body, text_body):
    sender = env("EMAIL_FROM", required=True)
    to = env("EMAIL_TO", required=True)
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, f"The Oyster Shack <{sender}>", to
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(env("SMTP_HOST", "smtp.gmail.com"), int(env("SMTP_PORT", "465"))) as s:
        s.login(sender, env("SMTP_APP_PASSWORD", required=True))
        s.sendmail(sender, [a.strip() for a in to.split(",")], msg.as_string())


# ---------------------------------------------------------------- comandos

def export_history(pages):
    """Baja reseñas que ya tienen respuesta del restaurante, para sacar ejemplos reales."""
    reviews = fetch_reviews(max_pages=pages)
    n = 0
    with HISTORY_FILE.open("w") as f:
        for r in reviews:
            resp = r.get("response") or {}
            reply = (resp.get("extracted_snippet") or {}).get("original") or resp.get("snippet")
            if reply:
                f.write(json.dumps({"name": (r.get("user") or {}).get("name"), "rating": r.get("rating"),
                                    "date": r.get("date"), "review": review_text(r), "reply": reply},
                                   ensure_ascii=False) + "\n")
                n += 1
    print(f"{n} respuestas publicadas guardadas en {HISTORY_FILE.name} (de {len(reviews)} reseñas).")


def run(args):
    now = dt.datetime.now(TZ)
    state = load_state()
    seen = set(state["seen"])
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=int(env("LOOKBACK_HOURS", "48")))

    if args.mock:
        reviews = json.loads(Path(args.mock).read_text())
    else:
        reviews = fetch_reviews(max_pages=int(env("MAX_PAGES", "3")), stop_before=cutoff)

    new = []
    for r in reviews:
        d = parse_date(r)
        if review_id(r) in seen or r.get("response"):
            continue
        if d and d < cutoff and not args.mock:
            continue
        new.append(r)

    items = []
    if new and not args.no_claude:
        import anthropic
        client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY", required=True))
        system_prompt = build_system_prompt()
        for r in new:
            items.append({"review": r, "draft": draft_reply(client, system_prompt, r)})
    else:
        for r in new:
            items.append({"review": r, "draft": {"flag": (r.get("rating") or 5) <= 2,
                                                  "flag_reason": "Prueba sin Claude" if (r.get("rating") or 5) <= 2 else "",
                                                  "reply": "(borrador de prueba)"}})

    items.sort(key=lambda i: (not i["draft"].get("flag"), i["review"].get("rating") or 5))
    run_date = now.strftime("%a %d %b %Y")
    html_body, text_body = render_html(items, run_date), render_text(items, run_date)
    flagged = sum(1 for i in items if i["draft"].get("flag"))
    subject = f"Reviews Oyster Shack · {now:%d %b} · {len(items)} nuevos" + (f" · {flagged} revisar" if flagged else "")

    if args.no_email:
        (BASE / "preview.html").write_text(html_body)
        print(f"preview.html generado ({len(items)} reviews).")
    elif items or env("SEND_WHEN_EMPTY", "true").lower() == "true":
        send_email(subject, html_body, text_body)
        print(f"Email enviado: {subject}")

    if not args.mock:
        state["seen"].extend(review_id(r) for r in new)
        state["last_run"] = now.isoformat()
        save_state(state)


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--find-place")
    ap.add_argument("--export-history", type=int, metavar="PAGINAS")
    ap.add_argument("--no-email", action="store_true")
    ap.add_argument("--no-claude", action="store_true")
    ap.add_argument("--mock")
    args = ap.parse_args()
    if args.find_place:
        find_place(args.find_place)
    elif args.export_history:
        export_history(args.export_history)
    else:
        run(args)


if __name__ == "__main__":
    main()
