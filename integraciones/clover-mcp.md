# Conector Clover MCP · `OYSTER_SHACK_CLOVER`

- **Código:** repo `bigfeetpr-ship-it/Oyster-shack-clover-mcp.zip` (se renombró con "O" mayúscula; si Vercel deja de desplegar, revisar la conexión del repo ahí).
- **Despliegue:** Vercel (auto-deploy desde `main`).
- **Clon para Casa Lucca:** `bigfeetpr-ship-it/csa-lucca-clover-mcp` (conector `Casa_Lucca_MCP`). Aplicarle los mismos arreglos.
- El código del conector **no se copia aquí** para no romper el despliegue de Vercel; este repo solo lo documenta.

## Herramientas
| Lectura | Escritura (solo con confirmación de Joseph) |
|---|---|
| `sales_by_item`, `daily_sales_tips`, `daily_closeout` (cierre por tender, marcas de tarjeta, cash esperado, IVU, batch), `search_orders`, `get_order`, `menu_audit`, `search_items`, `get_item`, `list_categories`, `list_modifier_groups`, `list_tax_rates`, `list_devices` | `create_item`, `update_item`, `set_items_hidden`, `delete_hidden_items`, `set_item_categories`, `set_item_modifier_groups`, `create_category`, `update_category`, `delete_category`, `create_modifier_group`, `update_modifier_group`, `delete_modifier_group`, `add_modifiers_to_groups`, `remove_modifier_from_groups`, `update_modifier`, `set_modifier_availability` |

## Arreglos hechos (11–12 nov 2026)
1. **Órdenes abiertas:** el conector confiaba en `paymentState`, que se queda en OPEN aunque la orden esté pagada (decía 49 abiertas; había 1). Ahora compara cada orden con sus pagos (un pago después de medianoche cuenta). Separa: sin pagar · pago parcial con balance · vacías en $0, con hora, empleado y mesa.
2. **Historial >90 días:** Clover deja de *listar* órdenes de más de ~90 días aunque pidas un solo día; los pagos sí siguen. `sales_by_item`, `search_orders` y `menu_audit` ahora recuperan las órdenes viejas desde sus pagos y las piden una por una.
   - Solo recupera órdenes **cobradas**.
   - Más lento: un día fuerte puede necesitar 2 llamadas (`next_offset`).
   - Máximo 85 días por llamada.

## Cambios
- 17 nov 2026: nueva herramienta `daily_closeout` para el cierre diario; el reporte diario la usa en la sección 4.

## Trampas conocidas
- `open_unpaid` de `daily_sales_tips` sigue dando un conteo incorrecto: no usar; las abiertas salen de `search_orders`.
- Respuestas paginadas: si `complete=false`, repetir con `offset=next_offset`.
