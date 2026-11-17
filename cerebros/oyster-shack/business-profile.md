# Business Profile — The Oyster Shack

> Plantilla del wrapper de restaurantes, llenada con el cliente #1. Los skills de menu engineering la leen primero.
> Nunca pongas tokens, contraseñas ni números de cuenta aquí.

## 1. Identidad
- Nombre comercial: The Oyster Shack
- Entidad legal: New Capital Venture LLC
- Ubicación: Condado, San Juan, PR
- Concepto: seafood restaurant y oyster bar con una de las selecciones de ostras más amplias de PR
- Días/horario de operación: [FALTA]
- Idioma de los reportes: Español
- Tono de marca: cálido, profesional, seguro

## 2. POS y datos
- POS: Clover · conector `OYSTER_SHACK_CLOVER`
- Merchant ID: (no se guarda aquí)
- Historial en el POS: más de 1 año
- Período analizado en Fase 1: 2026-08-01 a 2026-11-03 (95 días)
- Fuente de verdad de precios: Clover
- Límites del conector: Orders no lista órdenes de >90 días; el conector las recupera desde Payments (solo pagadas); máx. 85 días por llamada; respuestas paginadas con `next_offset`

## 3. Convenciones del POS
- "App X" = mismo plato y precio que "X", servido como entrada. Pares conocidos: App Charboiled/Charbroiled Oysters, App Rockefeller/Rockefeller, App Award Wining/Award Wining, App Seafood Medley/Seafood Medley, App Mahi Ceviche/Mahi Mahi Ceviche Plate, App Octopus Ceviche/Octopus Ceviche Plate, App Shrimp Ceviche, App Guacamole, App Clam Chowder, App Scallops, App Churrasco.
- Tamaños que se unen: Whole Snapper, Whole Branzino, Whole Lobster Thermidor (Local/Maine), Stone Crabs.
- No-menú (se excluye): Gratuity, Beers For The Kitchen, gift cards, custom/open items, "Sale", merch.
- Cortesía: "Agua De La Casa" ($0).
- Ortografía conocida: "Charboiled", "Award Wining", "Hamashi", "Wine Champienon", "Clams Caserole", "Loaded Lobster. Bisque".
- Promos: Margaritas 2x1 Endless Summer, Endless Summer Oyster Shooter $5, Happy Hour Medalla Bucket.
- No usar `open_unpaid` de `daily_sales_tips` (conteo incorrecto); las órdenes abiertas salen de `search_orders`.

## 4. Categorías analíticas
| Categoría | Comida/bebida |
|---|---|
| Raw Bar | Comida |
| Hot Starters, Soups & Shellfish | Comida |
| Ceviches, Crudos & Cold Starters | Comida |
| Signature Mains | Comida |
| Mofongos, Tacos & Rice | Comida |
| Sides | Comida |
| Kids | Comida |
| Desserts | Comida |
| Cocktails | Bebida |
| Beer | Bebida |
| Wine & Bubbles | Bebida |
| Spirits & Shots | Bebida |
| Non-Alcoholic | Bebida |

## 5. Costos
- Recipe cost cards: no existen todavía [FALTA]
- Pour cost: [FALTA]
- Precio de mercado: whole fish, langosta entera, stone crabs [FALTA: cómo se costean]
- Proveedores: Sam's, Costco, Amazon, Denarius, José Santiago, Seaword, DC Produce, Dockside, Janes Pastry, Doña Lola, Méndez, Reds, Ballester, Pangeas, Pepín, Hidropónicos; ostras: Everglades Oysters entre otros
- Food cost % / pour cost % objetivo: [FALTA]

## 6. Operación
- Roles: Oyster Bar, Shuckers, Servers, Captains, Hosts, cocina
- Platos estratégicos: ostras (identidad), Seafood Tower (nuevo, exclusivo)
- Ingredientes de mercado: ostras por temporada, pescado entero, snow crab, langosta

## 7. Reglas específicas
- Tiers de ostras: ver `cerebro.md §2` y skill `clasificar-ostras`.
- Ostras fuera del pizarrón → 86, nunca borrar.

## 8. Aprobaciones
- Cambios de precio o menú: gerencia, propuestos por Joseph.
- Cambios en Clover: Joseph confirma en el chat cada vez.

## 9. Historial de análisis
| Fecha | Fase | Link | Hallazgos clave |
|---|---|---|---|
| 2026-11-04 | Fase 1 (ventas) | https://claude.ai/artifact/Y6wXB3yn6taxMLUcVRoSR4 | 31 de 101 platos = 80% de comida; 86 de Snow Crab, mofongos, Lobster Bisque y Lemon Shark (~$1,800/semana) |
| 2026-11-13 | Labor vs mesas | https://claude.ai/artifact/Ay8hkvR5hQnqmjiFC6QhWp | ~1,300 h de server por encima de 4 mesas/server; cena plana todos los días |
| 2026-11-16 | Recipe Hub vs Clover | `conocimiento/menu-engineering/recipe-hub-gaps.md` | Snow Crab, Arroz Mariscos, Prawns y otros sin receta |
