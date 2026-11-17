# Bot de WhatsApp para los grupos de trabajo

## Objetivo
Un número de WhatsApp dentro de los chats de trabajo para que el inventario y el reporte diario del restaurante actualicen Trello y creen inventarios automáticamente.

## Decisiones
- El inventario y el reporte diario del grupo llegan cada uno como **un solo mensaje largo de texto**.
- Se construye con **Baileys** (no Kapso / Cloud API), para que el bot viva dentro de los grupos y Claude procese la información.
- Número dedicado del bot: el de OpenClaw/Juniorkilla en el Mac mini (no se guarda aquí).
- Reglas de parseo de inventario: `conocimiento/inventario/reglas.md`.

## Estado
En construcción. OpenClaw ya contesta por WhatsApp; falta habilitar los grupos y conectar la salida con Trello.
