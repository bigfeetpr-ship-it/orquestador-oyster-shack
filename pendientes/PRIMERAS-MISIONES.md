# Pendientes · The Oyster Shack (17 nov 2026)

Orden recomendado: lo que ya está casi listo primero. No diseñar más jerarquía antes de lanzar.

## 🔥 Esta semana
- [x] **Agente de reviews probado en la MacBook Air** (17 nov): SerpApi, Claude y email funcionando.
- [x] **Agente de reviews en el Mac mini** (17 nov): instalado, launchd cargado y probado (`launchctl start` → email enviado). Corre diario a las 6:00am.
- [ ] **Reviews → menciones y WhatsApp** (17 nov): en el Mac mini `git pull`, añadir `WHATSAPP_TO` y `OPENCLAW_BIN` al `.env`, `--test-whatsapp`, `--backfill-mentions 2026-11`. Confirmar la lista `empleados.csv` (apodos, quién participa).
- [x] **Ejemplos reales de reviews**: `examples.md` armado con 96 respuestas publicadas (17 nov).
- [ ] **Guía de voz**: se cortó en el Ejemplo 5; faltan ejemplos negativos y la sección 10. Resolver los [VERIFICAR] (canal de quejas, compensaciones, otros idiomas).
- [x] Inventario: formato (mín)(par)—conteo y pedir hasta el par confirmados (17 nov). Procesador en `agentes/inventario/`.
- [ ] Inventario: Juniorkilla procesa los conteos reenviados (instrucción puesta en OpenClaw). Falta: unidades por producto en `catalogo/productos.csv`, códigos `DL` y `J`.
- [ ] **OpenClaw**: probar el puente con Dropbox en la oficina; activar los grupos de WhatsApp.

## Ventas y menú
- [ ] Completar ventas a 6 meses (el conector ya puede; correrlo por ventanas de ≤85 días, mejor como tarea de una noche).
- [ ] Fase 2 de menu engineering: faltan recipe cost cards, costo por ostra, pour cost.
- [ ] Recipe Hub: reemplazar en Dropbox la versión nueva entregada el 16 nov; recetas faltantes (Snow Crab, Arroz Mariscos, Prawns, mofongos, Whole Snapper…); corregir precios del índice.
- [ ] Limpieza de Clover por categoría (empezar por Hot Plates); todas las ostras bajo "Oysters".
- [ ] Award-Winning Oysters: App $24 vs normal $23 en Clover, unificar.
- [ ] **Margaritas en Clover** (stand by): montar bordes, tequila, sabor Premium y HOLD según `conocimiento/clover/margaritas-modificadores.md`, con confirmación de Joseph; después enviar el mensaje al staff y a Jaime.
- [ ] Ostras: protocolo FIFO (Pangea + Red's Best) y one-pager imprimible para shuckers.
- [x] Reporte diario con cierre de caja (`daily_closeout`) desde el 17 nov.

## Personal
- [ ] Training Hub: Server Ops Manual (11 MB) y Shucker Ops Manual (35 MB) — PDF sin fotos o acceso local.
- [ ] Videos de training, empezando por Host Operations Manual.
- [ ] Labor: revisar cena plana Lun–Mié, solape de cambio de turno a las 17:00 y cierre Lun–Jue; aclarar clock-ins faltantes en TipHaus.
- [ ] ADP: definir el export semanal.

- [ ] Guest Recognition: actualizar documento maestro y después el one-pager (tiers, bonos, sin tope).
- [x] One-pagers de propinas: CreciPay, Tip Distribution y FAQ (17 nov). Confirmar si los % se calculan sobre la propina total.

## Marketing
- [ ] Platea: 1 publicación + 1 email blast con foco en el Seafood Tower.
- [ ] Menú completo 2027: arreglar página 5 (Drinks) y 6 (Our Story).
- [ ] Fotos de menú: organizar Master Photos Folder por sección/plato.
- [ ] Oyster Shucking / Tasting Experience: definir formato y precio.

## Operación
- [ ] Flujo de subida de facturas por cocina.
- [ ] Migración de contraseñas a 1Password.
- [ ] Bot de WhatsApp (Baileys) → Trello.

## Producto (Mesa / Restaurant OS)
- [ ] Probar los skills de menu engineering con Casa Lucca (cliente #2) y aplicarle los arreglos del conector.
- [ ] Ponerle precio a la Fase 1 como servicio.
