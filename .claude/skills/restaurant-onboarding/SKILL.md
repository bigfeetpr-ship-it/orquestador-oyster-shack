---
name: restaurant-onboarding
description: Use when setting up a new restaurant client: walk the owner through the intake questionnaire and produce their business-profile.md for the Project.
---

# Restaurant Onboarding → business-profile.md

Objetivo: dejar el Project del cliente listo para que los demás skills (menu-engineering-fase1, menu-engineering) trabajen sin adivinar. Ejemplo llenado: `cerebros/oyster-shack/business-profile.md`.

## Pasos

1. **Revisa lo que ya existe.** Busca en el Project: menú, reportes del POS, recipe cost cards, un business-profile.md previo. Si hay un conector de POS, haz una llamada ligera (listar categorías e items) para precargar respuestas.
2. **Precarga desde el POS** todo lo que puedas inferir: categorías del POS, botones que parecen duplicados del mismo plato, items que no son menú (gratuity, gift card, custom item, merch, "Sale"), items ocultos o 86. Marca estas respuestas como *propuestas*, no como hechos.
3. **Pregunta solo lo que falta**, en bloques cortos (máx. 4 preguntas por mensaje), en este orden: identidad → POS y fuente de precios → convenciones del POS → categorías analíticas → costos → operación → reglas propias → aprobaciones. Usa AskUserQuestion cuando las opciones sean cerradas.
4. **Propón las categorías analíticas** (ej. Raw Bar, Hot Starters, Ceviches, Mains, Sides, Kids, Desserts, Cocktails, Beer, Wine, Spirits, Non-Alcoholic) y el mapeo desde las categorías del POS. El dueño confirma.
5. **Escribe business-profile.md** siguiendo exactamente la plantilla de secciones 1–9 (Identidad, POS y datos, Convenciones del POS, Categorías analíticas, Costos, Operación, Reglas específicas, Aprobaciones, Historial de análisis). Deja en blanco, con "PENDIENTE", lo que no se respondió. Guárdalo en el Project.
6. **Cierra con la lista de faltantes** que bloquean análisis: típicamente recipe cost cards, pour cost, y ventas de más de 90 días.

## Reglas
- Nunca guardes tokens, contraseñas ni números de cuenta en el perfil.
- No inventes datos del negocio. Lo inferido del POS se confirma antes de escribirse como hecho.
- Usa los nombres de roles y el vocabulario que use el negocio.
- Un perfil por negocio. Si el cliente tiene varias ubicaciones con POS distintos, un perfil por ubicación.
