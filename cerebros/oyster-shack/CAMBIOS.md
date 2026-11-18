# Cambios del cerebro

## 2026-11-17 · v1
- Se crea el orquestador consolidando todo lo trabajado en el Project "The Oyster Shack Analysis" y los chats desde nov 2026:
  conector de Clover (documentado), reporte diario (skill), ingesta de OpenClaw, reglas de inventario v0.1, bot de WhatsApp,
  tiers de ostras, menu engineering Fase 1 (CSV + resumen + 3 skills), Recipe Hub gaps, labor vs mesas, training, menús,
  guía de voz y agente de reviews de Google.
- 5 agentes: operaciones, ventas-menu, personal, marketing, reputacion. El Gerente es CLAUDE.md.

## 2026-11-17 · reviews
- Agente de reviews probado en la MacBook Air: SerpApi (data_id 0x8c036fbdf13cbd33:0x58ffa3eba15e4e6a), Claude y email desde info@ funcionando.
- `agentes/reviews-google/examples.md`: 96 respuestas publicadas → patrones, ejemplos por tipo y 4 respuestas que NO se imitan.
- Resuelto desde el historial: canal de quejas = info@theoystershackpr.com; dueño = Jaime.
- System prompt: canal de quejas, Jaime, no citar precios ni "free valet"; revisión para reviews sospechosas y cobros.

## 2026-11-17 · sincronización de la tarde
- Reporte diario: 4ª sección de cierre de caja con la herramienta nueva `daily_closeout` (skill y tarea programada al día).
- Nuevo `conocimiento/clover/margaritas-modificadores.md` (plan en stand by).
- Nuevos `conocimiento/personal/guest-recognition.md` y `propinas.md`.
- Ostras: proveedores Pangea y Red's Best; FIFO y one-pager de shuckers en pendientes.
- Guest Recognition y propinas completados con las decisiones de los chats del 17 nov (tarifas por tier, pools y CreciPay).
- Agente de reviews instalado en el Mac mini (`~/orquestador-oyster-shack/agentes/reviews-google`), launchd activo y probado. La Air queda solo para pruebas, sin launchd.

## 2026-11-17 · noche
- Agente de reviews: cuenta empleados mencionados para el Guest Recognition (`empleados.csv`, `menciones.csv`, sección 👏 en el email, `--backfill-mentions`, `--mentions-report`) y avisa por WhatsApp con OpenClaw (`openclaw message send --channel whatsapp`).
- Inventario: procesador `agentes/inventario/inventario.py` (lista de compra por proveedor desde el conteo de WhatsApp), pensado para que Juniorkilla lo corra cuando Joseph le reenvía el conteo.
- OpenClaw: número de la oficina aprobado para reenviar conteos de inventario (solo inventario); dueño corregido a Joseph.
- Shack Staff Hub (Lovable) para centralizar días libres, cambios de turno, ponches y reportes diarios; clasificador `agentes/comunicaciones/procesar.py` que corre Juniorkilla.

## 2026-11-18 · cash log
- Conector Clover: nueva herramienta `cash_log` (cash removido/añadido, aperturas sin venta, conteos; empleado, hora y nota). Ver `integraciones/clover-mcp.md`.
