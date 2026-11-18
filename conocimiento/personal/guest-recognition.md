# Guest Recognition Program (incentivo de reviews para empleados)

Fuente: chat "Documento en español y PDF" (17 nov 2026). Maestro: Dropbox `Oyster Shack/Capacitacion de Empleados/Communication Binder/07 - Manuales y entrenamiento/The_Oyster_Shack_Guest_Recognition_Incentive_Program.docx` (reemplazar con la versión revisada). One-pager en inglés con el mismo formato del anterior.

## Pago por review (desde la primera)
| Tier | Reviews verificadas en el mes | Pago por review |
|---|---|---|
| Tier 1 | 1 – 10 | $5.00 |
| Tier 2 | 11 – 19 | $6.25 |
| Tier 3 | 20 – 29 | $7.50 |
| Tier 4 (top) | 30 – 40+ | $8.75 |

## Bonos al completar (solo se paga el más alto)
+$20 a las 10 · +$30 a las 20 · +$40 a las 30 · +$50 a las 40.

## Reglas
- No hace falta completar un tier para cobrar: se paga por review desde la primera.
- Al subir de tier, **todas las reviews del mes se pagan a la tarifa nueva**.
- **Sin tope**: después de la 40, cada review sigue pagando $8.75.
- Ejemplos del maestro: 7 reviews = $35 · 15 = $113.75 · 25 = $217.50 · 45 = $443.75.
- Encabezado del maestro: "Top Rate $8.75 / review + bonus".
- Nota financiera: si 4 empleados llegan a 40 reviews, cuesta $1,600; cada review adicional suma $8.75.

## Pendiente
- [ ] Reemplazar el maestro en Dropbox.
- [ ] El maestro tiene visible el revenue del mes: quitarlo si lo van a ver empleados.
- [ ] Definir si es piloto de 60 días (maestro) o programa permanente (one-pager viejo).
- Relacionado: el agente de reviews (`agentes/reviews-google/`) contesta los reviews que genera este programa.

## Conteo automático (desde el 17 nov 2026)
El agente de reviews detecta empleados nombrados en cada review nueva y lleva `menciones.csv` en el Mac mini. El email diario trae el conteo del mes y el estimado por empleado; el WhatsApp dice quién fue mencionado.
- Cuentan solo menciones **positivas** de empleados con `cuenta_programa=si` en `agentes/reviews-google/empleados.csv`.
- `[VERIFICAR]` con Joseph: si una review que nombra a 2 empleados cuenta para ambos (hoy: sí), si cuenta una mención positiva dentro de una review de 1–3★ (hoy: sí), y si el mes se cuenta por la fecha del review (hoy: sí).
- La gerencia verifica antes de pagar; el estimado no es la nómina.
