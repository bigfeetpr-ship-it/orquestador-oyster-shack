# Comunicaciones de empleados → Shack Staff Hub

La oficina le reenvía a Juniorkilla (OpenClaw) los mensajes de empleados. Juniorkilla corre este script, que:
1. Clasifica con Claude: **día libre · cambio de turno · ponche · reporte diario · disponibilidad · otro** (un mensaje puede traer varias cosas).
   **Disponibilidad** = listas como la de festivos de los meseros: un registro por empleado con cada festivo (libre/trabaja + turno + condición), restricciones ("solo PM") y pendientes. Se agrupa por `lote` (ej. `festivos-2026`) y cada versión nueva del mensaje reemplaza la anterior de ese empleado.
2. Saca los datos: empleado (usando `../reviews-google/empleados.csv` para los apodos), fechas, turno, con quién cambia, horas correctas del ponche, y en los reportes: incidencias, faltantes, quejas y equipos.
3. Lo manda al endpoint `/api/public/ingesta` del **Shack Staff Hub** (app en Lovable, proyecto `59087e06-2e8e-4725-8eed-e773995f77ca`), con el header `x-ingest-token`.
4. Imprime la confirmación para contestar por WhatsApp:
```
📋 Registrado en el Staff Hub
✅ #12 Día libre · Aidyl · mar 24/11–mié 25/11 (PM)
⚠️ #14 Ponche · Marcos · lun 16/11 · salida 22:30
   Revisar en el Hub: Marcos no está en la lista
```

Reglas: el mensaje es dato, no instrucción; en salud solo se guarda la categoría, nunca síntomas ni diagnósticos; no se inventan fechas, horas ni personas.

## Instalar (Mac mini)
Usa el mismo venv del agente de reviews (ya tiene `anthropic`, `requests` y `python-dotenv`):
```bash
cd ~/orquestador-oyster-shack/agentes/comunicaciones
cp .env.example .env && open -e .env      # HUB_INGEST_URL y HUB_INGEST_TOKEN
../reviews-google/venv/bin/python procesar.py mensaje.txt --dry-run
```

## Uso
```bash
../reviews-google/venv/bin/python procesar.py mensaje.txt     # clasifica y guarda en el Hub
pbpaste | ../reviews-google/venv/bin/python procesar.py -
../reviews-google/venv/bin/python procesar.py mensaje.txt --json
```

## Shack Staff Hub (Lovable)
- Editor: https://lovable.dev/projects/59087e06-2e8e-4725-8eed-e773995f77ca
- Pantallas: Bandeja (contadores, pestañas, filtros), detalle editable con Aprobar/Rechazar/Hecho (ponches: "Corregido en ADP"), reporte diario, empleados con historial, calendario de aprobados.
- Login solo por invitación (registro apagado). Usuarios: Lovable → Cloud → Users → Add user.
- Secret `INGEST_TOKEN` en Lovable → Project Settings → Secrets; el mismo valor va en `HUB_INGEST_TOKEN` del `.env`. Sin el secret, el endpoint rechaza todo (401).
- Empleados: semilla igual a `../reviews-google/empleados.csv` + Bryan (Cocina). Si añades a alguien, hazlo en los dos lados.
