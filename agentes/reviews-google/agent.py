#!/usr/bin/env python3
"""
The Oyster Shack - Agente de Google Reviews.

Cada mañana: trae los reviews nuevos (SerpApi), redacta respuestas con Claude
usando la guía de voz, cuenta los empleados mencionados (Guest Recognition
Program), manda un reporte por email y avisa por WhatsApp con OpenClaw.

Uso:
  python3 agent.py                          # corrida normal (lo que corre launchd)
  python3 agent.py --no-email               # genera preview.html en vez de enviar (no avisa por WhatsApp)
  python3 agent.py --find-place "The Oyster Shack Condado San Juan"
  python3 agent.py --export-history 10      # respuestas ya publicadas -> history.jsonl
  python3 agent.py --backfill-mentions 2026-11   # cuenta menciones de un mes ya pasado/en curso
  python3 agent.py --mentions-report [2026-11]   # imprime el conteo del mes
  python3 agent.py --test-whatsapp          # manda un mensaje de prueba por OpenClaw
  python3 agent.py --mock sample_reviews.json --no-email --no-claude   # prueba sin keys
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import smtplib
import subprocess
import sys
import unicodedata
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
STATE_FILE = BASE / "state.json"
HISTORY_FILE = BASE / "history.jsonl"
EXAMPLES_FILE = BASE / "examples.md"
ROSTER_FILE = BASE / "empleados.csv"
MENTIONS_FILE = BASE / "menciones.csv"
TZ = ZoneInfo("America/Puerto_Rico")
SERPAPI_URL = "https://serpapi.com/search.json"

# Guest Recognition Program (conocimiento/personal/guest-recognition.md)
TIERS = [(30, 8.75), (20, 7.50), (11, 6.25), (1, 5.00)]          # desde N reviews -> pago por review
BONUSES = [(40, 50), (30, 40), (20, 30), (10, 20)]               # al completar N -> bono (solo el más alto)
MENTION_FIELDS = ["mes", "fecha_review", "review_id", "cliente", "estrellas", "empleado",
                  "como_lo_llamo", "tono", "cuenta", "link"]


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


def log(msg):
    print(f"[{dt.datetime.now(TZ):%Y-%m-%d %H:%M}] {msg}", flush=True)


# ---------------------------------------------------------------- estado

def load_state():
    if STATE_FILE.exists():
        st = json.loads(STATE_FILE.read_text())
    else:
        st = {}
    st.setdefault("seen", [])
    st.setdefault("mention_seen", [])
    return st


def save_state(state):
    state["seen"] = state["seen"][-2000:]
    state["mention_seen"] = state["mention_seen"][-5000:]
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


def customer(r):
    return (r.get("user") or {}).get("name", "Anónimo")


# ---------------------------------------------------------------- empleados

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def load_roster():
    if not ROSTER_FILE.exists():
        return []
    with ROSTER_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["aliases"] = [a.strip() for a in (r.get("alias") or "").split(";") if a.strip()] or [r["nombre"]]
        r["cuenta_programa"] = (r.get("cuenta_programa") or "si").strip().lower() in ("si", "sí", "yes", "1")
    return rows


def roster_text(roster):
    return "\n".join(f"- {r['nombre']} ({r.get('rol', '')}); también: {', '.join(r['aliases'])}" for r in roster)


def match_roster(name, roster):
    """Devuelve la fila del roster cuyo nombre o alias coincide (sin acentos ni mayúsculas)."""
    n = norm(name)
    for r in roster:
        if n == norm(r["nombre"]) or n in (norm(a) for a in r["aliases"]):
            return r
    return None


def regex_mentions(text, roster):
    """Solo para pruebas sin Claude: busca alias como palabra completa."""
    out, t = [], norm(text)
    for r in roster:
        for a in r["aliases"]:
            if re.search(rf"\b{re.escape(norm(a))}\b", t):
                out.append({"nombre": r["nombre"], "como_lo_llamo": a, "tono": "positivo"})
                break
    return out


def clean_mentions(raw, roster):
    """Valida lo que devolvió el modelo contra el roster."""
    out = []
    for m in raw or []:
        if not isinstance(m, dict):
            continue
        called = (m.get("como_lo_llamo") or m.get("nombre") or "").strip()
        tone = (m.get("tono") or "neutral").lower()
        if tone not in ("positivo", "neutral", "negativo"):
            tone = "neutral"
        row = match_roster(m.get("nombre", ""), roster) or match_roster(called, roster)
        out.append({
            "empleado": row["nombre"] if row else "?",
            "como_lo_llamo": called,
            "tono": tone,
            "cuenta": bool(row and row["cuenta_programa"] and tone == "positivo"),
        })
    return out


# ---------------------------------------------------------------- Claude

def build_system_prompt():
    parts = [(BASE / "system_prompt.md").read_text(),
             "\n\n# GUÍA DE VOZ\n\n" + (BASE / "voice_guide.md").read_text()]
    if EXAMPLES_FILE.exists():
        parts.append("\n\n# EJEMPLOS REALES PUBLICADOS\n\n" + EXAMPLES_FILE.read_text())
    return "".join(parts)


def review_payload(r):
    return {
        "nombre_cliente": customer(r),
        "estrellas": r.get("rating"),
        "subpuntuaciones": r.get("details") or {},
        "fecha": r.get("date"),
        "texto": review_text(r) or "(sin texto, solo calificación)",
        "tiene_fotos": bool(r.get("images")),
    }


def call_claude(client, system, user, max_tokens=900):
    msg = client.messages.create(
        model=env("CLAUDE_MODEL", "claude-sonnet-5-5"),
        max_tokens=max_tokens,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    raw = "".join(b.text for b in msg.content if b.type == "text").strip()
    raw = re.sub(r"^```(json)?|```$", "", raw).strip()
    return raw


def draft_reply(client, system_prompt, r, roster):
    user = ("Redacta la respuesta a esta reseña de Google:\n\n"
            + json.dumps(review_payload(r), ensure_ascii=False, indent=2)
            + "\n\nLISTA DE EMPLEADOS:\n" + roster_text(roster))
    raw = call_claude(client, system_prompt, user)
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        out = {"flag": True, "flag_reason": "No pude leer la respuesta del modelo, revisar.", "reply": raw, "empleados": []}
    out["reply"] = clean_reply(out.get("reply", ""))
    out["empleados"] = clean_mentions(out.get("empleados"), roster)
    if (r.get("rating") or 5) <= 2:
        out["flag"] = True
        out["flag_reason"] = out.get("flag_reason") or "Reseña de 1-2 estrellas."
    return out


MENTION_ONLY_PROMPT = """Lees reseñas de Google de The Oyster Shack y extraes SOLO los empleados que el cliente nombra.
Usa la LISTA DE EMPLEADOS: si el nombre, un apodo o una mala ortografía obvia corresponde a alguien de la lista, devuelve su nombre exacto; si no está en la lista, usa "?".
"Our waiter" o "the staff" sin nombre no cuentan. tono: "positivo" (lo elogia), "negativo" (se queja de esa persona) o "neutral".
Devuelve SOLO JSON: {"empleados": [{"nombre": "...", "como_lo_llamo": "...", "tono": "positivo|neutral|negativo"}]}"""


def extract_mentions(client, r, roster):
    if not review_text(r):
        return []
    user = (json.dumps({"texto": review_text(r), "estrellas": r.get("rating")}, ensure_ascii=False)
            + "\n\nLISTA DE EMPLEADOS:\n" + roster_text(roster))
    try:
        return clean_mentions(json.loads(call_claude(client, MENTION_ONLY_PROMPT, user, 400)).get("empleados"), roster)
    except (json.JSONDecodeError, AttributeError):
        return []


EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️]")


def clean_reply(text):
    text = EMOJI_RE.sub("", text)
    text = text.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
    return re.sub(r"[ \t]{2,}", " ", text).strip()


# ---------------------------------------------------------------- registro de menciones

def review_month(r, fallback):
    d = parse_date(r)
    return (d.astimezone(TZ) if d else fallback).strftime("%Y-%m")


def append_mentions(r, mentions, now):
    if not mentions:
        return
    new_file = not MENTIONS_FILE.exists()
    d = parse_date(r)
    with MENTIONS_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MENTION_FIELDS)
        if new_file:
            w.writeheader()
        for m in mentions:
            w.writerow({
                "mes": review_month(r, now),
                "fecha_review": d.astimezone(TZ).strftime("%Y-%m-%d") if d else "",
                "review_id": review_id(r),
                "cliente": customer(r),
                "estrellas": r.get("rating"),
                "empleado": m["empleado"],
                "como_lo_llamo": m["como_lo_llamo"],
                "tono": m["tono"],
                "cuenta": "si" if m["cuenta"] else "no",
                "link": r.get("link", ""),
            })


def pay_for(count):
    rate = next((r for n, r in TIERS if count >= n), 0)
    bonus = next((b for n, b in BONUSES if count >= n), 0)
    return rate, bonus, round(count * rate + bonus, 2)


def month_summary(month):
    """Conteo por empleado del mes: positivas (las que pagan), neutrales y negativas.
    Devuelve (tabla, sin_identificar, fuera_del_programa)."""
    per, unknown, outside = {}, [], []
    roster = {r["nombre"]: r for r in load_roster()}
    if MENTIONS_FILE.exists():
        with MENTIONS_FILE.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["mes"] != month:
                    continue
                emp = row["empleado"]
                if emp == "?":
                    unknown.append(row)
                    continue
                if emp in roster and not roster[emp]["cuenta_programa"]:
                    outside.append(row)
                    continue
                c = per.setdefault(emp, {"positivo": 0, "neutral": 0, "negativo": 0})
                c[row["tono"] if row["tono"] in c else "neutral"] += 1
    table = []
    for emp, c in per.items():
        rate, bonus, total = pay_for(c["positivo"])
        table.append({"empleado": emp, "reviews": c["positivo"], "neutrales": c["neutral"], "negativas": c["negativo"],
                      "tarifa": rate, "bono": bonus, "total": total})
    table.sort(key=lambda t: (-t["reviews"], t["negativas"], t["empleado"]))
    return table, unknown, outside


# ---------------------------------------------------------------- reporte

def stars(n):
    n = int(n or 0)
    return "★" * n + "☆" * (5 - n)


def mention_badges(mentions):
    out = []
    for m in mentions:
        icon = "👏" if m["cuenta"] else ("❓" if m["empleado"] == "?" else "·")
        label = m["empleado"] if m["empleado"] != "?" else f'"{m["como_lo_llamo"]}" (¿quién?)'
        out.append(f"{icon} {label} ({m['tono']})")
    return out


def render_html(items, mention_items, run_date, month):
    flagged = [i for i in items if i["draft"].get("flag")]
    ready = [i for i in items if not i["draft"].get("flag")]
    avg = sum((i["review"].get("rating") or 0) for i in items) / len(items) if items else 0

    def card(i, color):
        r, d = i["review"], i["draft"]
        name = html.escape(customer(r))
        text = html.escape(review_text(r) or "(sin texto, solo calificación)")
        reason = f'<div style="color:#b42318;font-size:13px;margin:6px 0">⚠ {html.escape(d.get("flag_reason",""))}</div>' if d.get("flag") else ""
        badges = mention_badges(d.get("empleados", []))
        badge_html = f'<div style="font-size:13px;color:#1a5fb4;margin:6px 0">{html.escape(" · ".join(badges))}</div>' if badges else ""
        link = f' · <a href="{html.escape(r["link"])}" style="color:#555">ver en Google</a>' if r.get("link") else ""
        return f"""
<div style="border-left:4px solid {color};background:#fafafa;padding:14px 16px;margin:14px 0;border-radius:6px">
  <div style="font-size:15px"><b>{name}</b> <span style="color:#d4a017">{stars(r.get('rating'))}</span>
  <span style="color:#888;font-size:12px"> · {html.escape(r.get('date') or '')}{link}</span></div>
  <div style="color:#444;font-size:13px;margin:8px 0;font-style:italic">"{text}"</div>
  {reason}{badge_html}
  <div style="font-size:12px;color:#888;margin-top:10px">RESPUESTA:</div>
  <div style="background:#fff;border:1px solid #ddd;padding:12px;border-radius:4px;font-size:14px;line-height:1.5;white-space:pre-wrap">{html.escape(d.get('reply',''))}</div>
</div>"""

    if not items:
        body = '<p style="font-size:15px">No hay reviews nuevos sin contestar desde el último reporte.</p>'
    else:
        body = f'<p style="font-size:14px;color:#555">{len(items)} nuevos · promedio {avg:.1f}★</p>'
        if flagged:
            body += f'<h3 style="color:#b42318;margin-top:24px">🚩 REVISAR ANTES DE PUBLICAR ({len(flagged)})</h3>'
            body += "".join(card(i, "#b42318") for i in flagged)
        if ready:
            body += f'<h3 style="color:#1a7f37;margin-top:24px">✅ LISTOS PARA PEGAR ({len(ready)})</h3>'
            body += "".join(card(i, "#1a7f37") for i in ready)

    body += render_mentions_html(mention_items, month)
    return f"""<html><body style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:680px;margin:auto;color:#222">
<h2 style="margin-bottom:4px">Reviews de Google · The Oyster Shack</h2>
<div style="color:#888;font-size:13px">{run_date}</div>
{body}
<p style="color:#aaa;font-size:11px;margin-top:30px">Borradores generados automáticamente. Revisa antes de publicar.</p>
</body></html>"""


def render_mentions_html(mention_items, month):
    table, unknown, outside = month_summary(month)
    today = [(i["review"], m) for i in mention_items for m in i["mentions"]]
    if not today and not table and not unknown:
        return ""
    out = f'<h3 style="color:#1a5fb4;margin-top:28px">👏 GUEST RECOGNITION · {month}</h3>'
    if today:
        out += '<div style="font-size:13px;margin-bottom:8px"><b>Nuevas hoy:</b> ' + html.escape(
            " · ".join(f"{m['empleado'] if m['empleado'] != '?' else '¿' + m['como_lo_llamo'] + '?'} ({m['tono']}, {customer(r)} {int(r.get('rating') or 0)}★)"
                       for r, m in today)) + "</div>"
    if table:
        td = "padding:4px 8px"
        rows = "".join(
            f"<tr><td style='{td}'>{html.escape(t['empleado'])}</td>"
            f"<td style='{td};text-align:center'><b>{t['reviews']}</b></td>"
            f"<td style='{td};text-align:center;color:#888'>{t['neutrales']}</td>"
            f"<td style='{td};text-align:center;color:{'#b42318' if t['negativas'] else '#888'}'>{'<b>' + str(t['negativas']) + '</b>' if t['negativas'] else 0}</td>"
            f"<td style='{td};text-align:right'>${t['tarifa']:.2f}</td><td style='{td};text-align:right'>${t['bono']}</td>"
            f"<td style='{td};text-align:right'><b>${t['total']:.2f}</b></td></tr>" for t in table)
        out += ("<table style='border-collapse:collapse;font-size:13px;border:1px solid #ddd'>"
                f"<tr style='background:#f0f4fa'><th style='{td};text-align:left'>Empleado</th><th style='{td}'>👏 Positivas</th>"
                f"<th style='{td}'>Neutrales</th><th style='{td}'>👎 Negativas</th>"
                f"<th style='{td}'>Tarifa</th><th style='{td}'>Bono</th><th style='{td}'>Estimado</th></tr>"
                f"{rows}</table>")
    if unknown:
        out += '<div style="font-size:13px;color:#b42318;margin-top:8px">❓ Nombres sin identificar (añadirlos a empleados.csv): ' + html.escape(
            ", ".join(sorted({u["como_lo_llamo"] for u in unknown}))) + "</div>"
    if outside:
        out += f'<div style="font-size:12px;color:#888;margin-top:6px">Menciones de personas fuera del programa (ej. el dueño): {len(outside)}</div>'
    out += ('<div style="font-size:11px;color:#888;margin-top:6px">El pago se estima solo con las positivas: tarifa del tier más alto × positivas del mes '
            '+ bono más alto. Neutrales y negativas se registran pero no pagan. Pendiente de verificación de gerencia.</div>')
    return out


def render_text(items, mention_items, run_date, month):
    lines = [f"Reviews de Google · The Oyster Shack · {run_date}", ""]
    if not items:
        lines.append("No hay reviews nuevos sin contestar.")
    for i in items:
        r, d = i["review"], i["draft"]
        tag = "REVISAR" if d.get("flag") else "LISTO"
        lines += [f"[{tag}] {customer(r)} {stars(r.get('rating'))}",
                  f'"{review_text(r)}"',
                  *([f"Motivo: {d.get('flag_reason')}"] if d.get("flag") else []),
                  *(["Empleados: " + " · ".join(mention_badges(d.get("empleados", [])))] if d.get("empleados") else []),
                  "Respuesta:", d.get("reply", ""), "-" * 40, ""]
    table, unknown, _ = month_summary(month)
    if table or unknown:
        lines += [f"GUEST RECOGNITION · {month}"]
        lines += [f"- {t['empleado']}: {t['reviews']} positivas · {t['neutrales']} neutrales · {t['negativas']} negativas · ${t['total']:.2f} estimado" for t in table]
        if unknown:
            lines.append("Sin identificar: " + ", ".join(sorted({u["como_lo_llamo"] for u in unknown})))
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


# ---------------------------------------------------------------- WhatsApp (OpenClaw)

def whatsapp_message(items, mention_items, now):
    flagged = sum(1 for i in items if i["draft"].get("flag"))
    lines = [f"🦪 Reviews Oyster Shack · {now:%d %b}"]
    if items:
        lines.append(f"{len(items)} nuevo{'s' if len(items) != 1 else ''} sin contestar"
                     + (f" · 🚩 {flagged} para revisar" if flagged else "") + ".")
    else:
        lines.append("Sin reviews nuevos sin contestar.")
    counted = {}
    for i in mention_items:
        for m in i["mentions"]:
            if m["cuenta"]:
                counted[m["empleado"]] = counted.get(m["empleado"], 0) + 1
    if counted:
        lines.append("👏 " + ", ".join(f"{k} ×{v}" for k, v in counted.items()))
    negatives = {}
    for i in mention_items:
        for m in i["mentions"]:
            if m["tono"] == "negativo" and m["empleado"] != "?":
                negatives[m["empleado"]] = negatives.get(m["empleado"], 0) + 1
    if negatives:
        lines.append("👎 " + ", ".join(f"{k} ×{v}" for k, v in negatives.items()))
    unknown = {m["como_lo_llamo"] for i in mention_items for m in i["mentions"] if m["empleado"] == "?"}
    if unknown:
        lines.append("❓ Sin identificar: " + ", ".join(sorted(unknown)))
    if items:
        lines.append("Las respuestas están en tu email.")
    return "\n".join(lines)


def send_whatsapp(text):
    to = env("WHATSAPP_TO")
    if not to:
        log("WhatsApp: falta WHATSAPP_TO en .env, no se envió.")
        return False
    cmd = [env("OPENCLAW_BIN", "openclaw"), "message", "send", "--channel", "whatsapp", "--target", to, "--message", text]
    if env("OPENCLAW_ACCOUNT"):
        cmd += ["--account", env("OPENCLAW_ACCOUNT")]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except FileNotFoundError:
        log(f"WhatsApp: no encontré '{cmd[0]}'. Pon la ruta completa en OPENCLAW_BIN (sale con: which openclaw).")
        return False
    except subprocess.TimeoutExpired:
        log("WhatsApp: OpenClaw no respondió en 90 s.")
        return False
    if res.returncode != 0:
        log(f"WhatsApp: OpenClaw falló ({res.returncode}): {(res.stderr or res.stdout).strip()[:300]}")
        return False
    log("WhatsApp enviado.")
    return True


# ---------------------------------------------------------------- comandos

def export_history(pages):
    reviews = fetch_reviews(max_pages=pages)
    n = 0
    with HISTORY_FILE.open("w") as f:
        for r in reviews:
            resp = r.get("response") or {}
            reply = (resp.get("extracted_snippet") or {}).get("original") or resp.get("snippet")
            if reply:
                f.write(json.dumps({"name": customer(r), "rating": r.get("rating"), "date": r.get("date"),
                                    "review": review_text(r), "reply": reply}, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n} respuestas publicadas guardadas en {HISTORY_FILE.name} (de {len(reviews)} reseñas).")


def backfill_mentions(month):
    """Cuenta menciones de todas las reseñas de un mes (contestadas o no) que no estén ya registradas."""
    import anthropic
    start = dt.datetime.strptime(month + "-01", "%Y-%m-%d").replace(tzinfo=TZ)
    end = (start + dt.timedelta(days=32)).replace(day=1)
    roster = load_roster()
    state = load_state()
    seen = set(state["mention_seen"])
    client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY", required=True))
    reviews = fetch_reviews(max_pages=int(env("BACKFILL_PAGES", "15")), stop_before=start.astimezone(dt.timezone.utc))
    n_rev = n_men = 0
    now = dt.datetime.now(TZ)
    for r in reviews:
        d = parse_date(r)
        if not d or not (start <= d.astimezone(TZ) < end) or review_id(r) in seen:
            continue
        mentions = extract_mentions(client, r, roster)
        append_mentions(r, mentions, now)
        state["mention_seen"].append(review_id(r))
        n_rev += 1
        n_men += len(mentions)
    save_state(state)
    print(f"{month}: revisé {n_rev} reseñas nuevas para el registro, {n_men} menciones guardadas.")
    print_mentions(month)


def print_mentions(month):
    table, unknown, outside = month_summary(month)
    print(f"\nGuest Recognition · {month}")
    if not table:
        print("  Sin menciones de empleados.")
    for t in table:
        print(f"  {t['empleado']:<26} 👏 {t['reviews']:>2}  · {t['neutrales']:>2} neutrales  👎 {t['negativas']:>2}"
              f"   ${t['tarifa']:.2f} c/u + bono ${t['bono']} = ${t['total']:.2f}")
    if unknown:
        print("  Sin identificar:", ", ".join(sorted({u['como_lo_llamo'] for u in unknown})))
    if outside:
        print(f"  Fuera del programa: {len(outside)}")


def run(args):
    now = dt.datetime.now(TZ)
    month = now.strftime("%Y-%m")
    state = load_state()
    seen, mseen = set(state["seen"]), set(state["mention_seen"])
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=int(env("LOOKBACK_HOURS", "48")))
    roster = load_roster()

    if args.mock:
        reviews = json.loads(Path(args.mock).read_text())
    else:
        reviews = fetch_reviews(max_pages=int(env("MAX_PAGES", "3")), stop_before=cutoff)

    recent = [r for r in reviews if args.mock or not parse_date(r) or parse_date(r) >= cutoff]
    to_draft = [r for r in recent if review_id(r) not in seen and not r.get("response")]
    to_count = [r for r in recent if review_id(r) not in mseen]

    client = None
    if not args.no_claude and (to_draft or to_count):
        import anthropic
        client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY", required=True))
        system_prompt = build_system_prompt()

    items, mentions_by_id = [], {}
    for r in to_draft:
        if client:
            d = draft_reply(client, system_prompt, r, roster)
        else:
            d = {"flag": (r.get("rating") or 5) <= 2, "flag_reason": "Prueba sin Claude" if (r.get("rating") or 5) <= 2 else "",
                 "reply": "(borrador de prueba)", "empleados": clean_mentions(regex_mentions(review_text(r), roster), roster)}
        items.append({"review": r, "draft": d})
        mentions_by_id[review_id(r)] = d.get("empleados", [])

    mention_items = []
    for r in to_count:
        rid = review_id(r)
        if rid not in mentions_by_id:   # ya contestada en Google: solo contar menciones
            mentions_by_id[rid] = (extract_mentions(client, r, roster) if client
                                   else clean_mentions(regex_mentions(review_text(r), roster), roster))
        if mentions_by_id[rid]:
            mention_items.append({"review": r, "mentions": mentions_by_id[rid]})

    if not args.mock:
        for i in mention_items:
            append_mentions(i["review"], i["mentions"], now)

    items.sort(key=lambda i: (not i["draft"].get("flag"), i["review"].get("rating") or 5))
    run_date = now.strftime("%a %d %b %Y")
    html_body = render_html(items, mention_items, run_date, month)
    text_body = render_text(items, mention_items, run_date, month)
    flagged = sum(1 for i in items if i["draft"].get("flag"))
    subject = f"Reviews Oyster Shack · {now:%d %b} · {len(items)} nuevos" + (f" · {flagged} revisar" if flagged else "")

    if args.no_email:
        (BASE / "preview.html").write_text(html_body)
        print(f"preview.html generado ({len(items)} reviews, {sum(len(i['mentions']) for i in mention_items)} menciones).")
        print("\nWhatsApp (no enviado en modo prueba):\n" + whatsapp_message(items, mention_items, now))
    else:
        if items or env("SEND_WHEN_EMPTY", "true").lower() == "true":
            send_email(subject, html_body, text_body)
            log(f"Email enviado: {subject}")
        if env("WHATSAPP_NOTIFY", "true").lower() == "true" and (
                items or mention_items or env("WHATSAPP_WHEN_EMPTY", "false").lower() == "true"):
            send_whatsapp(whatsapp_message(items, mention_items, now))

    if not args.mock:
        state["seen"].extend(review_id(r) for r in to_draft)
        state["mention_seen"].extend(review_id(r) for r in to_count)
        state["last_run"] = now.isoformat()
        save_state(state)


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--find-place")
    ap.add_argument("--export-history", type=int, metavar="PAGINAS")
    ap.add_argument("--backfill-mentions", metavar="AAAA-MM")
    ap.add_argument("--mentions-report", nargs="?", const="", metavar="AAAA-MM")
    ap.add_argument("--test-whatsapp", action="store_true")
    ap.add_argument("--no-email", action="store_true")
    ap.add_argument("--no-claude", action="store_true")
    ap.add_argument("--mock")
    args = ap.parse_args()
    if args.find_place:
        find_place(args.find_place)
    elif args.export_history:
        export_history(args.export_history)
    elif args.backfill_mentions:
        backfill_mentions(args.backfill_mentions)
    elif args.mentions_report is not None:
        print_mentions(args.mentions_report or dt.datetime.now(TZ).strftime("%Y-%m"))
    elif args.test_whatsapp:
        ok = send_whatsapp("🦪 Prueba del agente de reviews de The Oyster Shack. Si te llegó esto, el aviso por WhatsApp funciona.")
        sys.exit(0 if ok else 1)
    else:
        run(args)


if __name__ == "__main__":
    main()
