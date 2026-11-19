# Generador del Recipe & Training Manual (PDF)

Arma el PDF de recetas para staff con el mismo formato del manual de junio 2026, con la foto de cada plato.
Documentación y estado: `conocimiento/training/recipe-training-manual.md`.

## Pasos
1. `parse.py <manual-junio.pdf>`: lee las recetas del PDF anterior → `parsed.json`.
2. Extraer las fotos del Recipe Hub (`unzip hub.xlsx` → `xl/media`), recortarlas cuadradas a 900 px y guardarlas en `img/imageN.jpg`.
   El mapa hoja → imagen sale de `xl/worksheets/_rels` y `xl/drawings/_rels`.
3. `prep.py`: une recetas, precios de Clover (diccionario `PRICE`, actualizarlo con `menu_audit` antes de cada versión),
   fotos (`IMG`) y recetas nuevas del Hub → `final.json`. Ajustar la ruta del Hub (`/home/claude/hub/hub.xlsx`).
4. `build.py`: genera el PDF (ReportLab) en la ruta `out` de `final.json`.

Requisitos: `pdfplumber`, `openpyxl`, `reportlab`, `Pillow`.
El PDF y las fotos no se suben al repo (pesan); el PDF va a Dropbox.
