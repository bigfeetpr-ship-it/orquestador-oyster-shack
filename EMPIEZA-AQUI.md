# Empieza aquí

Este es el cerebro operativo de The Oyster Shack en Claude Code.

## Usarlo
1. Clona el repo en el Mac mini (o donde trabajes):
   `git clone https://github.com/bigfeetpr-ship-it/orquestador-oyster-shack.git ~/orquestador-oyster-shack`
2. Ábrelo en Claude Code (app de escritorio → Abrir carpeta, o `claude` en la terminal dentro de la carpeta).
3. Escribe lo que necesites. Ejemplos:
   - "¿Cómo nos fue ayer?" → `ventas-menu` con el skill `reporte-diario`
   - *pegas el conteo de Bryan* → `operaciones` con `inventario-whatsapp`
   - *foto del pizarrón* → `clasificar-ostras`
   - "Contéstame estas 3 reviews" → `reputacion`
   - "Arranquemos la Fase 2 de menu engineering" → `menu-engineering`

## Mantenerlo vivo
- Cuando se decide algo nuevo, va al `cerebro.md` o a `conocimiento/` y se anota en `cerebros/oyster-shack/CAMBIOS.md`.
- Lo que está abierto vive en `pendientes/PRIMERAS-MISIONES.md`.
- El Project de claude.ai "The Oyster Shack Analysis" es el espejo para los chats: si cambia algo importante aquí, súbelo allá también.

## Lo que NO va a git
`.env`, keys, contraseñas, conversaciones de WhatsApp crudas (`fuentes/`), salidas (`salidas/`), `state.json` y logs del agente de reviews.
