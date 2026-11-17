# Menu Engineering Fase 1 — resumen (Clover, 2026-11-04)

Reporte completo: https://claude.ai/artifact/Y6wXB3yn6taxMLUcVRoSR4
Datos limpios: `data/clover_item_sales_2026-08-01_to_2026-11-03.csv`
Método: skill `menu-engineering-fase1`. Fase 2 (costos y CM): skill `menu-engineering`.

- Período analizado: 2026-08-01 a 2026-11-03 (95 días), no 6 meses. El historial completo SÍ existe en Clover (>1 año). El conector ya recupera órdenes de >90 días desde Payments (arreglo del 11-12 nov), así que se puede completar a 6 meses corriéndolo por ventanas de ≤85 días.
- Ventas de menú $415,745 (comida $304,017 / bebida $111,728), 4,396 órdenes. No-menú excluido: $3,244 (gratuity, "Sale", custom items, gift cards, merch).
- 18 platos con botones duplicados unidos ("App" = mismo plato, servido como entrada). 13 categorías analíticas propias.
- Pareto comida: 31 de 101 platos = 80% de ventas. Bebida: 40 de 166.
- Al 2026-11-04 en 86: Snow Crab, todos los mofongos, Lobster Bisque, Lemon Shark (~$1,800/semana históricos).
- Precios de ostras, Arroz Mariscos, kids subieron durante el período (+6% a +31%).
- Falta: costos por plato (recipe cost cards), costo por ostra, costo por trago, template, menú impreso, ventas de 6 meses.
