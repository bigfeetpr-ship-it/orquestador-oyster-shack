# Procesador de inventario · The Oyster Shack

Le reenvías a Juniorkilla (OpenClaw) el mensaje de inventario de WhatsApp (GRUPO 1 … GRUPO 10) y te contesta con la lista de compra por proveedor.

Es un cálculo fijo en Python: no usa API, no cuesta, no inventa. Reglas: `conocimiento/inventario/reglas.md`.

## Qué devuelve
- 🛒 **COMPRAR (hasta el par)** agrupado por proveedor: 🔴 agotado · 🟠 bajo mínimo · 🟡 bajo par. Pedir = par − conteo.
- Los lunes añade a Sam's la lista fija (cherries, centerpull, alcohol, blueberries, bolsas Power Flex 33).
- ⚠️ **REVISAR CON QUIEN CONTÓ**: conteo vacío, unidad distinta al par (ej. "3 box" con par 37), códigos de proveedor fuera de la leyenda, falta mínimo o par, 🚨 que no cuadra. Esos no entran a la lista de compra; se dice cuánto sería si el número está bien.
- 🔕 Productos bajo mínimo que nadie marcó con 🚨 (para entrenar a quien cuenta).
- 🚫 Lo que está bajo pero dice "no comprar".

## Uso
```bash
python3 inventario.py conteo.txt                 # mensaje para WhatsApp + guarda en registros/
pbpaste | python3 inventario.py -                # desde el portapapeles
python3 inventario.py conteo.txt --md inbox.md   # además, resumen para el buzón OysterShack-Brain
python3 inventario.py conteo.txt --no-guardar    # prueba
```
Formato de cada línea: `Producto — PROV — (MÍNIMO) (PAR) — CONTEO [unidad] [notas] [🚨]` (confirmado por Joseph el 17 nov).

## Catálogo (opcional, recomendado)
Si existe `catalogo/productos.csv`, manda sobre el mensaje en mínimo, par, unidad y proveedor, y avisa si el mensaje trae otro número. Columnas:
`id, nombre_oficial, aliases, grupo, proveedor_principal, proveedor_alterno, unidad_conteo, minimo, par, no_comprar, categoria, notas`
(El de la prueba del 16 nov con 113 productos está en `inventario-oystershack.zip` → `catalogo/productos.csv`; falta llenar `unidad_conteo`.)

## Registros
`registros/` (local, no va a git): el mensaje original, el JSON, el pedido en CSV y el mensaje enviado, por fecha y hora.
