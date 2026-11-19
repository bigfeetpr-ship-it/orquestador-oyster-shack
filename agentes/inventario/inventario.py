#!/usr/bin/env python3
"""
The Oyster Shack · Procesador del conteo de inventario de WhatsApp.

Lee el mensaje tal cual (GRUPO 1 … GRUPO 10), clasifica cada producto contra su
mínimo y par, y devuelve la lista de compra por proveedor lista para WhatsApp.
Reglas: conocimiento/inventario/reglas.md  ·  Formato:  Producto — PROV — (MÍNIMO) (PAR) — CONTEO [unidad] [notas] [🚨]

Uso:
  python3 inventario.py conteo.txt            # imprime el mensaje para WhatsApp y guarda registros/
  pbpaste | python3 inventario.py -           # desde el portapapeles / stdin
  python3 inventario.py conteo.txt --md out.md   # además escribe un resumen para el buzón de OysterShack-Brain
  python3 inventario.py conteo.txt --no-guardar  # no guarda nada (prueba)
Sin dependencias externas (Python 3.9+).
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
CATALOGO = BASE / "catalogo" / "productos.csv"
REGISTROS = BASE / "registros"
TZ = ZoneInfo("America/Puerto_Rico")

PROVEEDORES = {
    "S": "Sam's", "C": "Costco", "A": "Amazon", "DE": "Denarius", "JS": "José Santiago",
    "SW": "Seaword", "DC": "DC Produce", "D": "Dockside", "JP": "Janes Pastry",
    "DN": "Doña Lola", "M": "Méndez", "R": "Reds", "B": "Ballester", "P": "Pangeas",
    "PE": "Pepín", "H": "Hidropónicos",
    # variantes que se usan en el conteo (confirmadas por Joseph, 17 nov)
    "DL": "Doña Lola", "J": "Janes Pastry",
    # "L" = Lares, indicado en la leyenda del conteo de la oficina (19 nov)
    "L": "Lares",
}
UNIDADES = {
    "box": "box", "bix": "box", "boxes": "box", "caja": "box", "cajas": "box",
    "bag": "bag", "bags": "bag", "bolsa": "bag", "bolsas": "bag",
    "portion": "porción", "portions": "porción", "porción": "porción", "porcion": "porción", "porciones": "porción",
    "pack": "pack", "packs": "pack", "galón": "galón", "galon": "galón", "galones": "galón",
    "lata": "lata", "latas": "lata", "cartón": "cartón", "carton": "cartón", "cartones": "cartón",
    "lb": "lb", "lbs": "lb", "libra": "lb", "libras": "lb", "unidad": "unidad", "unidades": "unidad",
}
# Compra fija de los lunes en Sam's (reglas.md §5)
LISTA_FIJA_LUNES = ["1 cherries", "1 centerpull paper", "1 galón de alcohol", "1 blueberries",
                    "bolsas negras Power Flex 33"]
DASH = r"\s*[—–~-]+\s*"
NUM_RE = r"\d+(?:[.,]\d+)?(?:\s+\d+/\d+)?(?:/\d+)?"
FLAGS_NO_COMPRAR_SOLO = {"posible_unidad_distinta_al_par", "conteo_vacio", "sin_min_ni_par",
                         "solo_un_numero_entre_parentesis", "conteo_muy_alto_revisar_unidad"}


# ---------------------------------------------------------------- parseo

def num(s):
    """'2 1/2' -> 2.5, '1/2' -> 0.5, '10' -> 10, '1,5' -> 1.5"""
    total = Fraction(0)
    for part in s.strip().replace(",", ".").split():
        total += Fraction(part)
    return float(total)


def slug(s):
    s = s.lower()
    for a, b in zip("áéíóúñü", "aeiounu"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def parse_conteo(texto):
    t = texto.strip()
    m = re.match(rf"^({NUM_RE})\s*(.*)$", t)
    if not m:
        return None, None, t
    cant = num(m.group(1))
    resto = m.group(2).strip()
    unidad = None
    w = resto.split()
    if w and w[0].lower().strip(",.") in UNIDADES:
        unidad = UNIDADES[w[0].lower().strip(",.")]
        resto = " ".join(w[1:])
    return cant, unidad, resto.strip(" ,")


def parse_linea(linea, grupo):
    alerta = linea.count("🚨")
    l = linea.replace("🚨", "").strip()
    flags, notas = [], ""
    if "no comprar" in l.lower():
        notas = "no comprar"
        l = re.sub(r"(?i)no comprar", "", l).strip()

    partes = re.split(DASH, l, maxsplit=1)
    nombre = partes[0].strip()
    resto = partes[1] if len(partes) > 1 else ""

    prov = None
    mprov = re.match(r"^([A-Z]{1,2}(?:-[A-Z]{1,2})?)(?:\s*\(([^)]*)\))?\s*(?=[—–~(\-]|$|\s)", resto)
    if mprov:
        prov = mprov.group(1)
        resto = resto[len(prov):]
    else:
        mn = re.match(r"^(.*?)\s+([A-Z]{1,2})$", nombre)
        if mn and mn.group(2) in PROVEEDORES:
            nombre, prov = mn.group(1), mn.group(2)
        else:
            flags.append("sin_proveedor")

    prov_codes = prov.split("-") if prov else []
    for c in prov_codes:
        if c not in PROVEEDORES:
            flags.append(f"codigo_proveedor_desconocido:{c}")

    variantes = re.findall(rf"\b([SML])\s*\((\d+)\)\s*\((\d+)\)\s*({NUM_RE})?", resto)
    if len(variantes) >= 2:
        return [build(f"{nombre} ({t})", prov_codes, int(mn_), int(par), num(cnt) if cnt else None,
                      None, notas, grupo, alerta, flags + ["linea_con_tallas"], linea)
                for t, mn_, par, cnt in variantes]

    nums = [int(x) for x in re.findall(r"\((\d+)\)", resto)]
    tras = re.split(r"\(\d+\)", resto)[-1] if nums else resto
    tras = re.sub(rf"^{DASH}", "", tras.strip()).strip().lstrip("—–~- ").strip()

    if len(nums) >= 2:
        minimo, par = nums[0], nums[1]
    elif len(nums) == 1:
        minimo, par = None, nums[0]
        flags.append("solo_un_numero_entre_parentesis")
    else:
        minimo = par = None
        flags.append("sin_min_ni_par")

    cant, unidad, extra = parse_conteo(tras) if tras else (None, None, "")
    if extra and cant is None and extra.lower() in UNIDADES:
        unidad, extra = UNIDADES[extra.lower()], ""
    if extra:
        mix = re.findall(rf"({NUM_RE})\s*(?:de\s+)?([A-Za-zÁÉÍÓÚáéíóúñÑ]+)", tras)
        if len(mix) >= 2:
            flags.append("conteo_mixto_unidades")
            notas = (notas + " | " if notas else "") + tras
            cant = sum(num(n) for n, _ in mix)
            unidad = None
        else:
            notas = (notas + " | " if notas else "") + extra
    if cant is None:
        flags.append("conteo_vacio")
    return [build(nombre, prov_codes, minimo, par, cant, unidad, notas, grupo, alerta, flags, linea)]


def build(nombre, prov_codes, minimo, par, cant, unidad, notas, grupo, alerta, flags, linea):
    flags = list(flags)
    usado = cant
    if cant is None and alerta >= 3:
        usado = 0.0
        flags.remove("conteo_vacio") if "conteo_vacio" in flags else None
        flags.append("vacio_con_3_alertas_se_asume_0")
    estado = "sin_datos"
    if usado is not None and par is not None:
        if usado == 0:
            estado = "agotado"
        elif minimo is not None and usado <= minimo:
            estado = "bajo_minimo"
        elif usado < par:
            estado = "bajo_par"
        elif usado > par * 1.5:
            estado = "sobre_par"
        else:
            estado = "ok"
    pedir = None
    if usado is not None and par is not None and "no comprar" not in notas:
        pedir = max(0.0, par - usado) if estado in ("agotado", "bajo_minimo", "bajo_par") else 0.0
    if alerta and estado in ("ok", "sobre_par"):
        flags.append("alerta_manual_pero_cantidad_ok")
    if not alerta and estado in ("agotado", "bajo_minimo"):
        flags.append("bajo_minimo_sin_alerta_manual")
    if (unidad in ("box", "bag", "pack") and par and par >= 10
            and usado is not None and 0 < usado < par / 5):
        flags.append("posible_unidad_distinta_al_par")
    if usado is not None and par and usado > par * 3:
        flags.append("conteo_muy_alto_revisar_unidad")
    return dict(
        id=slug(nombre), grupo=grupo, producto=nombre,
        proveedores=[PROVEEDORES.get(c, c) for c in prov_codes], codigos_proveedor=prov_codes,
        minimo=minimo, par=par, conteo=cant, conteo_usado=usado, unidad_conteo=unidad,
        alertas_manual=alerta, estado=estado, pedir=pedir, notas=notas or None,
        flags=flags, linea_original=linea.strip(),
    )


WA_PREFIX = re.compile(r"^\[?\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:[ap]\.?\s?m\.?)?\]?\s*(?:-\s*)?(?:[^:]{1,40}:\s*)?", re.I)


def parse_mensaje(texto):
    grupo, items, extras, contador = None, [], [], None
    for raw in texto.splitlines():
        l = WA_PREFIX.sub("", raw.strip()).strip().strip("*_")
        if not l or l.lower() in ("reenviado", "forwarded", "‎reenviado", "‎forwarded"):
            continue
        mg = re.match(r"(?i)^grupo\s*(\d+)\s*[:\-—]?\s*(.*)$", l)
        if mg:
            grupo = int(mg.group(1))
            if mg.group(2).strip() and contador is None:
                contador = mg.group(2).strip()
            continue
        if l.upper().startswith("LEYENDA") or re.match(r"^[A-Z]{1,2}\s*=", l):
            continue
        if l.lower().startswith(("administracion", "administración")):
            extras.append(l)
            continue
        if grupo is None and not re.search(r"\(\d+\)", l):
            continue   # texto antes del GRUPO 1 que no es un producto
        items.extend(parse_linea(l, grupo))
    return dict(contado_por=contador, items=items, lista_fija_administracion=extras)


# ---------------------------------------------------------------- catálogo (opcional)

def aplicar_catalogo(items):
    """Si existe catalogo/productos.csv, manda en mínimo, par, unidad y proveedor (reglas.md §4)."""
    if not CATALOGO.exists():
        return 0
    with CATALOGO.open(newline="", encoding="utf-8") as f:
        cat = {r["id"]: r for r in csv.DictReader(f)}
        for r in list(cat.values()):
            for a in (r.get("aliases") or "").split(";"):
                if a.strip():
                    cat[slug(a)] = r
    usados = 0
    for i in items:
        c = cat.get(i["id"])
        if not c:
            i["flags"].append("no_esta_en_catalogo")
            continue
        usados += 1
        for campo, key in (("minimo", "minimo"), ("par", "par")):
            v = (c.get(key) or "").strip()
            if v:
                v = float(v)
                if i[campo] is not None and float(i[campo]) != v:
                    i["flags"].append(f"{campo}_distinto_al_catalogo:{i[campo]}→{v:g}")
                i[campo] = v
        if (c.get("unidad_conteo") or "").strip() not in ("", "POR DEFINIR") and not i["unidad_conteo"]:
            i["unidad_conteo"] = c["unidad_conteo"].strip()
        if (c.get("no_comprar") or "").strip().lower() in ("sí", "si", "yes"):
            i["notas"] = ((i["notas"] or "") + " | no comprar").strip(" |")
        # recalcular con los valores del catálogo
        nuevo = build(i["producto"], i["codigos_proveedor"], i["minimo"], i["par"], i["conteo"], i["unidad_conteo"],
                      i["notas"] or "", i["grupo"], i["alertas_manual"],
                      [f for f in i["flags"] if f not in ("alerta_manual_pero_cantidad_ok", "bajo_minimo_sin_alerta_manual",
                                                          "posible_unidad_distinta_al_par", "conteo_muy_alto_revisar_unidad",
                                                          "vacio_con_3_alertas_se_asume_0")]
                      + (["conteo_vacio"] if i["conteo"] is None and "conteo_vacio" not in i["flags"] else []),
                      i["linea_original"])
        i.update({k: nuevo[k] for k in ("estado", "pedir", "conteo_usado", "flags")})
    return usados


# ---------------------------------------------------------------- salida

def fmt(x):
    if x is None:
        return "?"
    return f"{x:g}" if x != int(x) else str(int(x))


MOTIVOS = {
    "conteo_vacio": "sin conteo (¿0 o se les pasó?)",
    "posible_unidad_distinta_al_par": "unidad del conteo distinta al par",
    "conteo_muy_alto_revisar_unidad": "conteo muy alto, ¿unidad?",
    "sin_min_ni_par": "sin mínimo ni par",
    "solo_un_numero_entre_parentesis": "falta el mínimo o el par",
    "sin_proveedor": "sin proveedor",
    "conteo_mixto_unidades": "conteo con unidades mezcladas",
    "alerta_manual_pero_cantidad_ok": "tiene 🚨 pero la cantidad está bien",
    "no_esta_en_catalogo": "no está en el catálogo",
}


def motivo(flag):
    if flag.startswith("codigo_proveedor_desconocido:"):
        return f"código de proveedor «{flag.split(':', 1)[1]}» no está en la leyenda"
    if "_distinto_al_catalogo:" in flag:
        campo, val = flag.split("_distinto_al_catalogo:")
        return f"{campo} en el mensaje distinto al catálogo ({val})"
    return MOTIVOS.get(flag)


def necesita_revision(i):
    return bool(set(i["flags"]) & FLAGS_NO_COMPRAR_SOLO)


def mensaje_whatsapp(data, fecha):
    items = data["items"]
    res = {e: sum(1 for i in items if i["estado"] == e) for e in ("agotado", "bajo_minimo", "bajo_par", "ok", "sobre_par", "sin_datos")}
    dias = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
    cab = f"📦 *Inventario* · {dias[fecha.weekday()]} {fecha:%d/%m}"
    if data["contado_por"]:
        cab += f" · contó {data['contado_por']}"
    out = [cab,
           f"{len(items)} productos: {res['agotado']} agotados · {res['bajo_minimo']} bajo mínimo · {res['bajo_par']} bajo par · {res['ok'] + res['sobre_par']} bien",
           ""]

    comprar = [i for i in items if i["pedir"] and not necesita_revision(i)]
    por_prov = {}
    for i in comprar:
        prov = i["proveedores"][0] if i["proveedores"] else "Proveedor por confirmar"
        if i["codigos_proveedor"] and i["codigos_proveedor"][0] not in PROVEEDORES:
            prov = f"«{prov}» (código por confirmar)"
        por_prov.setdefault(prov, []).append(i)
    lunes = fecha.weekday() == 0
    if lunes:
        por_prov.setdefault("Sam's", [])
    out.append("🛒 *COMPRAR (hasta el par)*")
    if not por_prov:
        out.append("Nada por debajo del par.")
    orden_estado = {"agotado": 0, "bajo_minimo": 1, "bajo_par": 2}
    for prov in sorted(por_prov, key=lambda p: ("confirmar" in p, -len(por_prov[p]), p)):
        lista = sorted(por_prov[prov], key=lambda i: (orden_estado.get(i["estado"], 9), i["producto"]))
        out.append(f"\n*{prov}* ({len(lista)})")
        for i in lista:
            icon = {"agotado": "🔴", "bajo_minimo": "🟠", "bajo_par": "🟡"}.get(i["estado"], "")
            u = f" {i['unidad_conteo']}" if i["unidad_conteo"] else ""
            alt = f" · alterno: {i['proveedores'][1]}" if len(i["proveedores"]) > 1 else ""
            out.append(f"{icon} {i['producto']}: *{fmt(i['pedir'])}*{u} (hay {fmt(i['conteo_usado'])}, par {fmt(i['par'])}){alt}")
        if prov == "Sam's" and lunes:
            out.append("➕ Lista fija de lunes: " + ", ".join(LISTA_FIJA_LUNES))

    revisar = [i for i in items if any(motivo(f) for f in i["flags"])]
    if revisar:
        out += ["", f"⚠️ *REVISAR CON QUIEN CONTÓ* ({len(revisar)})"]
        for i in sorted(revisar, key=lambda i: (not necesita_revision(i), i["producto"])):
            motivos = "; ".join(m for m in (motivo(f) for f in i["flags"]) if m)
            extra = ""
            if necesita_revision(i) and i["pedir"]:
                extra = f" → si el número está bien, pedir {fmt(i['pedir'])}"
            out.append(f"• {i['producto']}: {motivos}{extra}")

    sin_alerta = [i["producto"] for i in items if "bajo_minimo_sin_alerta_manual" in i["flags"]]
    if sin_alerta:
        out += ["", "🔕 Bajo mínimo y sin 🚨 en el conteo: " + ", ".join(sorted(sin_alerta))]
    no_comprar = [i for i in items if i["notas"] and "no comprar" in i["notas"] and i["estado"] in ("agotado", "bajo_minimo", "bajo_par")]
    if no_comprar:
        out += ["", "🚫 Bajos pero marcados «no comprar»: " + ", ".join(i["producto"] for i in no_comprar)]
    if data["lista_fija_administracion"]:
        out += ["", "📝 " + " | ".join(data["lista_fija_administracion"])]
    return "\n".join(out)


def resumen_md(data, fecha, wa):
    return (f"# Inventario — {fecha:%Y-%m-%d}\nFuente: conteo de inventario (WhatsApp, reenviado a Juniorkilla)\n"
            f"Reportado por: {data['contado_por'] or 'sin nombre'}\n\n## Datos\n"
            + "\n".join(f"- {i['producto']}: {fmt(i['conteo_usado'])} (mín {fmt(i['minimo'])}, par {fmt(i['par'])}) · {i['estado']}"
                        for i in data["items"] if i["estado"] in ("agotado", "bajo_minimo", "bajo_par"))
            + "\n\n## Decisiones o acciones\n- Lista de compra sugerida (pendiente de aprobación):\n\n" + wa + "\n")


def guardar(texto, data, wa, fecha, quien):
    REGISTROS.mkdir(exist_ok=True)
    stem = f"{fecha:%Y-%m-%d_%H%M}_conteo_{slug(quien or 'sin-nombre')}"
    (REGISTROS / f"{stem}.txt").write_text(texto, encoding="utf-8")
    (REGISTROS / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(REGISTROS / f"{stem}_pedido.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["proveedor", "producto", "estado", "conteo", "minimo", "par", "pedir", "unidad", "revisar"])
        for i in data["items"]:
            if i["pedir"]:
                w.writerow([" / ".join(i["proveedores"]) or "?", i["producto"], i["estado"], fmt(i["conteo_usado"]),
                            fmt(i["minimo"]), fmt(i["par"]), fmt(i["pedir"]), i["unidad_conteo"] or "",
                            "; ".join(m for m in (motivo(x) for x in i["flags"]) if m)])
    (REGISTROS / f"{stem}_whatsapp.txt").write_text(wa, encoding="utf-8")
    return stem


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo", help="archivo con el mensaje, o - para leer de stdin")
    ap.add_argument("--fecha", help="AAAA-MM-DD (por defecto hoy, hora de PR)")
    ap.add_argument("--md", help="escribe un resumen .md para el buzón de OysterShack-Brain")
    ap.add_argument("--json", action="store_true", help="imprime el JSON en vez del mensaje")
    ap.add_argument("--no-guardar", action="store_true")
    a = ap.parse_args()

    texto = sys.stdin.read() if a.archivo == "-" else Path(a.archivo).read_text(encoding="utf-8")
    fecha = dt.datetime.strptime(a.fecha, "%Y-%m-%d").replace(tzinfo=TZ) if a.fecha else dt.datetime.now(TZ)
    data = parse_mensaje(texto)
    if not data["items"]:
        print("No encontré productos con el formato «Producto — PROV — (mín) (par) — conteo». ¿Es el mensaje de inventario?")
        sys.exit(2)
    data["catalogo_aplicado"] = aplicar_catalogo(data["items"])
    data["resumen"] = {e: sum(1 for i in data["items"] if i["estado"] == e)
                       for e in ("agotado", "bajo_minimo", "bajo_par", "ok", "sobre_par", "sin_datos")}
    wa = mensaje_whatsapp(data, fecha)
    if not a.no_guardar:
        guardar(texto, data, wa, fecha, data["contado_por"])
    if a.md:
        Path(a.md).write_text(resumen_md(data, fecha, wa), encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2) if a.json else wa)


if __name__ == "__main__":
    main()
