# Recipe & Training Manual (PDF de recetas para staff)

## Qué es
El formato oficial de recetas para el staff es el **Recipe & Training Manual**: una receta por página, con
encabezado (nombre, ID, precio y porción), alérgenos / GF / prep, descripción, banner amarillo de STAFF,
tabla de ingredientes, preparación paso a paso y plateo & estándares. Los IDs (SP, SU, HD, CV, TN, WF, LC, SPEC, AF, RAW)
son los mismos del Recipe Hub (`The Oyster Shack Recipe Hub.xlsx`).

| Versión | Archivo | Dónde está |
|---|---|---|
| Junio 2026 (sin fotos) | `OysterShack_TrainingManual_2026_1.pdf` (41 págs) | Dropbox › Oyster Shack › Capacitacion de Empleados › Communication Binder › 07 - Manuales y entrenamiento |
| **Noviembre 2026 (con foto por plato)** | `OysterShack_TrainingManual_2026_Nov.pdf` (47 págs, 8.4 MB) | Entregado en el chat el 19 nov 2026. [FALTA] subirlo a la misma carpeta de Dropbox |

## Versión noviembre 2026 (19 nov)
**Fuentes:** el PDF de junio (contenido de las recetas), las fotos del Recipe Hub (versión de octubre, 33 fotos)
y los precios de Clover del 19 nov 2026.

**Cambios**
- 41 recetas (36 de junio + 4 nuevas + Salmon renombrado). 33 con foto de referencia.
- Precios según Clover: Charbroiled $24→$25 · Rockefeller $25→$26 · Steak Tacos $22→$25 · Steamed Clams $28→$32 ·
  Tuna Tartare $29→$28 · Salmon Crudo ("Ver menú") → **Wild Salmon Sashimi $18**.
- Recetas nuevas (método y plateo del Recipe Hub; cantidades **por confirmar con cocina**): Crab Cakes (LC-02, $34),
  Stone Crab Claws (RAW-03, $59), Jonah Crab Claws (RAW-02, $26), Whole Branzino Stuffed (WF-02, $55 / $62).
- Índice con páginas. La referencia rápida de temperaturas y alérgenos se arma desde las recetas (en junio salía cortada).
- Última página: lista de cambios vs junio.

**Pendiente con cocina**
- Fotos que faltan (8): Charbroiled Oysters, Fresh Wild Calamari, Seafood Medley Ceviche, Wild Salmon Sashimi,
  Blue Fin Tuna, Spicy Crab, Jonah Crab Claws, Beans Ceviche.
- Wild Mussels PEI y Clams Casserole usan la misma foto en el Recipe Hub: confirmar cuál es y tomar la otra.
- La foto de "Jonah Crab Claws" en el Hub es del Whole Jonah Crab: no se usó.
- Porciones que no cuadran con Clover: Stone Crab (Hub: Large 3 / Jumbo 2 muelas; Clover: "(2)" en ambos) y
  Jonah Claws (Hub: 4; Clover: "Cocktail Jonah Crab Claws (5)").
- Cantidades de ingredientes de las 4 recetas nuevas.
- Blue Fin Tuna está 86 en Clover; la receta se quedó en el manual.

**No entró todavía**
- Las recetas añadidas al Hub el 16 nov (Shrimp / Mahi / Ceviche Tacos, Whole Jonah Crab, Creamy Garlic Potatoes,
  Pan Seared Albacore, Tuna Tataki, preps de carrucho / mofongo / arroz, salsas de ostras): el Hub que se usó era el de octubre.
- Los platos sin receta en ningún documento: ver `conocimiento/menu-engineering/recipe-hub-gaps.md`.

## Cómo regenerarlo
Scripts en `agentes/manual-recetas/` (ver su README). Necesitan el PDF de junio, el Recipe Hub `.xlsx` y los precios de Clover.
