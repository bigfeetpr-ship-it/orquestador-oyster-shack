---
name: menu-engineering-fase1
description: Use for Phase 1 of restaurant menu engineering: pull item sales from the POS, clean and merge them into a validated sales file and a first report, before cost data exists.
---

# Menu Engineering — Fase 1 (ventas del POS)

Fase 1 = popularidad, ventas y Pareto con datos del POS. No requiere costos. La Fase 2 (skill menu-engineering) añade costos, CM y la matriz completa.

## 0. Antes de empezar
- Lee **business-profile.md** (en este repo: `cerebros/oyster-shack/business-profile.md`). Si no existe, corre primero restaurant-onboarding (o pregunta lo mínimo: POS, período, fuente de precios, items no-menú, categorías).
- Confirma el período. Ideal: 6 meses. Si el conector tiene límite por llamada (Clover: 90 días en Orders/Payments), pide los datos en ventanas consecutivas usando filtros de fecha y únelos. Si el conector no puede, dilo, analiza lo que haya y pide un export de Item Sales del POS para completar.

## 1. Extraer
- Ventas por item (unidades, ventas netas) del período, más la lista actual de items con precio de lista, categoría y disponibilidad (86/oculto).
- Guarda los datos crudos en archivos y calcula en código. No pagines resultados grandes por el chat ni estimes en prosa.

## 2. Limpiar (documenta cada decisión)
- **Excluir no-menú**: propinas/gratuity, gift cards, merch, custom/open items, "Sale", cargos manuales. Reporta el total excluido.
- **Unir botones duplicados** del mismo plato (ej. "App X" y "X"; variantes de ortografía; tamaños del mismo producto cuando el perfil lo indique). Guarda la lista de botones unidos con sus unidades en la columna pos_buttons_merged.
- **Mapear a categorías analíticas** según el perfil. Comida y bebida se analizan por separado.
- **Detectar precios que cambiaron** en el período: compara precio promedio realizado (ventas netas ÷ unidades) vs. precio de lista actual. Diferencias >5% se reportan.
- **Items de cortesía** (precio $0) se mantienen en unidades pero se señalan; no distorsionan revenue.
- **Items actualmente 86** se señalan: sus ventas históricas son revenue en riesgo.
- Nunca corrijas en silencio un dato dudoso: señálalo.

## 3. Archivo limpio
Un CSV con estas columnas:
category, item, units_sold, net_sales, avg_realized_price, current_list_price, menu_mix_pct_in_category, popularity_70pct_rule, pos_buttons_merged
- menu_mix_pct_in_category = unidades ÷ unidades de la categoría.
- popularity_70pct_rule = High si mix ≥ (100% ÷ n items de la categoría) × 70%; si no, Low. Indica el umbral por categoría.
Nómbralo data/<pos>_item_sales_<inicio>_to_<fin>.csv.

## 4. Análisis Fase 1
- Totales: unidades, ventas de menú (comida / bebida), órdenes si están disponibles; reconcilia con el total del POS.
- Pareto A (unidades) y Pareto B (ventas $), separados para comida y bebida: cuántos items hacen el 80%.
- Popularidad por categoría con el umbral 70%.
- Cola larga: items con muy pocas unidades en el período (candidatos a revisar en Fase 2, no a eliminar todavía).
- Hallazgos: concentración de ventas, categorías infladas, 86 con mucho revenue histórico, precios que subieron.
- Etiqueta cada afirmación: HECHO / CÁLCULO / INTERPRETACIÓN / RECOMENDACIÓN / SUPUESTO.

## 5. Entregar
- Reporte publicado (artifact) con resumen ejecutivo, calidad de datos, Pareto, popularidad por categoría y la lista de faltantes para la Fase 2.
- Un resumen corto (fase1-<pos>-resumen.md) en el Project y en `conocimiento/menu-engineering/` con: período, totales, decisiones de limpieza, link al reporte, faltantes.
- Actualiza la sección "Historial de análisis" del business-profile.md.

## Faltantes típicos para Fase 2
Recipe cost cards por plato, pour cost por trago, costo de items de mercado, template de menu engineering si el cliente tiene uno, menú impreso actual, ventas de 6 meses.
