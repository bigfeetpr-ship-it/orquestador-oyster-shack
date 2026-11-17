---
name: menu-engineering
description: Use for full restaurant menu engineering (Phase 2): contribution margin, Star/Plowhorse/Puzzle/Dog matrix, Pareto, pricing scenarios and item-level recommendations from POS sales plus recipe costs.
---

# Menu Engineering — análisis profesional

Actúa como consultor senior de menu engineering, food cost y pricing. El objetivo no es clasificar: es decir qué hacer con cada item y por qué. (Versión completa en inglés de estas instrucciones: Project doc `claude/menu-engineering-instructions.md`.)

## 0. Contexto
- Lee **business-profile.md** (categorías, convenciones, platos estratégicos, aprobaciones, idioma).
- Usa el CSV limpio de Fase 1 si existe (`data/`); si no, corre menu-engineering-fase1 primero.
- Los archivos del cliente son la fuente de verdad. Nunca inventes ventas, costos, recetas, precios ni márgenes. Si falta algo, di exactamente qué falta y qué análisis no se puede completar.
- Si el cliente sube un **template**: respeta su metodología, fórmulas, tabs y formato; distingue celdas input vs. fórmula; si una fórmula parece incorrecta, señálala antes de tocarla.

## 1. Validación de datos
Duplicados, precios/costos/unidades faltantes, ceros o negativos, nombres inconsistentes, items en ventas sin costo y viceversa, food cost % anómalos, períodos inconsistentes, modificadores o tamaños que distorsionan. Reporta antes de analizar.

## 2. Cálculos por item
- Revenue = unidades × precio
- Food Cost % = costo ÷ precio
- CM = precio − costo
- CM total = CM × unidades
- Menu Mix % = unidades ÷ unidades de la categoría
Muestra suficiente detalle para auditar. Reconcilia totales.

## 3. Umbrales (por categoría, salvo que el template diga otra cosa)
- Popularidad: (100% ÷ n items) × 70%.
- CM: promedio ponderado = CM total de la categoría ÷ unidades de la categoría.
Siempre indica los umbrales usados. No compares categorías distintas sin explicar la limitación.

## 4. Matriz
- **STAR** (alta pop., alto CM): proteger, consistencia, visibilidad; subir precio solo con cuidado.
- **PLOWHORSE** (alta pop., bajo CM): revisar porción, receta, compras, guarniciones, eficiencia, aumento pequeño. No eliminar por default.
- **PUZZLE** (baja pop., alto CM): ubicación, nombre, descripción, foto, recomendación del server, percepción de precio. Intentar subir demanda antes de quitar.
- **DOG** (baja pop., bajo CM): quitar, reemplazar, reformular, reprecio, reposicionar; considerar ingredientes compartidos y razones operativas, dietéticas o de marca. No eliminar por default.

## 5. Pareto
Tres rankings: unidades, ventas $ y CM total $. Para cada uno: %, % acumulado, items que hacen ~80%. Compara: alto volumen ≠ alto revenue ≠ alta contribución.

## 6. Food cost vs. CM
Nunca decidas solo por food cost %. Food cost % = eficiencia; CM $ = dólares para cubrir labor, gastos y ganancia. Explica cuándo un item con food cost alto es atractivo por CM y volumen.

## 7. Pricing y escenarios
Para cada precio propuesto: CM nuevo y food cost % nuevo, lado a lado con los actuales, considerando arquitectura de precios de la categoría. Nunca asumas volumen constante: modela escenarios (volumen igual, −5%, −10%) y etiquétalos como SUPUESTO. Para reducción de costo: food cost % y CM resultantes. Para eliminar un item: CM en riesgo, aclarando que parte de la demanda migra a otros items y hay que probarlo.

## 8. Ingredientes y operación (si hay recetas)
Ingredientes usados por muchos platos vs. uno solo, ingredientes caros de un solo uso, cross-utilization, complejidad de inventario, merma, preparación excesiva, equipos especiales, tiempos de ticket. Separa hechos de supuestos a validar con cocina.

## 9. Recomendaciones
Por item: KEEP, FEATURE, REPRICE, REENGINEER, REPOSITION, PROMOTE, REDUCE COST, MODIFY PORTION, REFORMULATE, INVESTIGATE o CONSIDER REMOVAL. No mecánico desde la matriz. En las importantes: qué muestran los datos, por qué importa, acción, efecto esperado, riesgo. Agrupa en Protect / Improve / Test / Consider Removing. Respeta los platos estratégicos del perfil.

## 10. Diseño de menú
Visibilidad para Stars y Puzzles prometedores; ubicación, jerarquía visual, número de opciones, descripciones, presentación de precios. No destacar algo solo por ser caro.

## 11. Reporte final
A. Resumen ejecutivo · B. Calidad de datos · C. Desempeño del menú (unidades, revenue, food cost total, CM total, food cost % ponderado, CM ponderado) · D. Matriz (Item | Unidades | Precio | Costo | FC % | CM $ | Mix % | Clasificación) · E. Pareto (unidades, $, CM $) · F. Análisis por categoría · G. Recomendaciones por item (Item | Clasificación | Problema | Acción | Prioridad) · H. Oportunidades de precio · I. Optimización · J. Diseño de menú · K. Impacto financiero · L. Plan de acción (Inmediato / Probar / Estratégico).
Etiqueta HECHO / CÁLCULO / INTERPRETACIÓN / RECOMENDACIÓN / SUPUESTO. Publica el reporte como artifact y actualiza el historial del business-profile.md.

## Reglas críticas
Nunca: inventar números, cambiar fórmulas sin justificar, usar food cost % como única medida, eliminar Dogs o subir Stars automáticamente, asumir volumen constante, confundir revenue con ganancia o CM con ganancia neta, afirmar causalidad con correlación. Nunca cambiar el POS sin confirmación explícita.
Siempre: validar primero, mostrar fórmulas, reconciliar, cuantificar, explicar limitaciones, pensar como operador y consultor financiero.
