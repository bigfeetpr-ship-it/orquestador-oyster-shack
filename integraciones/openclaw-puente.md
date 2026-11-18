# Puente OpenClaw → Claude (OysterShack-Brain)

**OpenClaw** corre en el Mac mini como el bot **"Juniorkilla"** (Telegram; canal de WhatsApp enlazado y contestando desde nov 2026; siguiente paso: activar los chats de grupo). Su trabajo: leer lo que pasa en los chats de WhatsApp del restaurante (inventario, reporte diario, faltantes, quejas) y dejarlo para Claude.

## Flujo
1. OpenClaw escribe en Dropbox `/Marketing 2025/OysterShack-Brain/inbox/` un archivo por tema por día: `YYYY-MM-DD_tema.md`.
2. Cada noche a las **11:47pm** la tarea programada "OysterShack-Brain: ingesta nocturna de OpenClaw" lo integra al Project de claude.ai en `claude/openclaw/<tema>.md` y mueve lo procesado a `processed/` (ver `automatizaciones/tareas-programadas.md`).
3. Temas: inventario, reporte-diario, ventas, labor, faltantes, quejas, menu, proveedores, incidencias.

## Formato que escribe OpenClaw (README del buzón)
```
# <Tema> — YYYY-MM-DD
Fuente: <nombre del chat de WhatsApp>
Reportado por: <nombre o rol del empleado>

## Datos
- <item>: <cantidad / precio / estado>

## Decisiones o acciones
- ...

## Notas
- ...
```
- Datos concretos siempre que existan (cantidades, unidades, precios, horas).
- NO incluir números de teléfono, datos de tarjetas ni datos personales de clientes.
- No editar ni borrar archivos en `processed/`.

## Pendiente
- Dropbox instalado en el Mac mini como puente (hay que probarlo en la oficina).
- Estructura para que OpenClaw analice cómo se recibe inventario: prueba inicial para definir reglas (`conocimiento/inventario/reglas.md` v0.1).

## Acceso por WhatsApp (17 nov 2026)
- Dueño de OpenClaw (`commands.ownerAllowFrom`): solo el WhatsApp de Joseph.
- **Número de la oficina:** aprobado con `openclaw pairing approve whatsapp <código>`. Regla fija en `~/clawd/USER.md`: **solo inventario**. Procesa conteos reenviados con `agentes/inventario/inventario.py`, le contesta a la oficina y le manda copia a Joseph; a cualquier otra cosa responde "Este número solo puede enviar conteos de inventario".
- ⚠️ Al aprobar un número con `ownerAllowFrom` vacío, OpenClaw lo hace dueño. Revisar siempre después de aprobar: `grep -n ownerAllowFrom -A2 ~/.openclaw/openclaw.json`.
- La regla de "solo inventario" es una instrucción, no un bloqueo técnico. Si la oficina logra que haga otra cosa, pasar a un agente separado sin Terminal.
- Reiniciar el gateway: `launchctl kickstart -k gui/$UID/ai.openclaw.gateway` (el `openclaw gateway restart` falla desde algunas Terminales).
