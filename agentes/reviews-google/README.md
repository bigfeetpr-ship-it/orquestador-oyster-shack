# Agente de Google Reviews · The Oyster Shack

Todos los días a las 6:00am: trae los reviews nuevos de Google, redacta las respuestas con la voz de la marca, cuenta los empleados mencionados, manda un email desde info@ a Joseph y avisa por WhatsApp. El email trae:
- 🚩 **REVISAR**: 1-2★, temas de salud/legal, acusaciones a empleados (trae borrador, pero míralo antes de publicar)
- ✅ **LISTOS PARA PEGAR**: el resto

## Instalación en el Mac mini (una sola vez, ~15 min)

```bash
# 1. Entra a la carpeta del agente dentro del repo
cd ~/orquestador-oyster-shack/agentes/reviews-google

# 2. Entorno de Python
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Configuración
cp .env.example .env
open -e .env          # pega SERPAPI_KEY, ANTHROPIC_API_KEY, SMTP_APP_PASSWORD

# 4. Encuentra el ID del restaurante y pégalo en GOOGLE_DATA_ID
./venv/bin/python agent.py --find-place "The Oyster Shack Condado San Juan"

# 5. Prueba sin enviar email (abre preview.html)
./venv/bin/python agent.py --no-email && open preview.html

# 6. Prueba real con email
./venv/bin/python agent.py

# 7. Prográmalo a las 6:00am
cp com.oystershack.reviews.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.oystershack.reviews.plist
```

Si el Mac está dormido a las 6:00, launchd lo corre cuando despierte.

## Menciones de empleados (Guest Recognition)

Cada review nueva (contestada o no) pasa por Claude para detectar a qué empleados nombra y con qué tono.
- Lista de empleados y apodos: `empleados.csv` (`cuenta_programa=no` para quien no participa, ej. el dueño).
- Registro: `menciones.csv` (local, no va a git). Una línea por empleado mencionado.
- **Pagan solo las positivas**; las neutrales y negativas se cuentan por empleado (👎 en el email y el WhatsApp) pero no pagan. Nombres que no están en la lista salen como ❓ para añadirlos.
- El email trae la sección **👏 GUEST RECOGNITION** con el conteo del mes y el estimado de pago (tarifa del tier × reviews + bono más alto). La gerencia verifica.

```bash
./venv/bin/python agent.py --backfill-mentions 2026-11   # cuenta lo que ya pasó en el mes
./venv/bin/python agent.py --mentions-report             # conteo del mes en curso
```

## Aviso por WhatsApp (OpenClaw)

Al terminar, manda un resumen corto por WhatsApp con `openclaw message send --channel whatsapp`.
En `.env`: `WHATSAPP_TO` (tu número, +1787...) y `OPENCLAW_BIN` (salida de `which openclaw`). Probar:
```bash
./venv/bin/python agent.py --test-whatsapp
```
Si OpenClaw falla, el email sale igual y el error queda en `agent.log`.

## Ejemplos reales (recomendado)

```bash
./venv/bin/python agent.py --export-history 10
```
Baja las respuestas que ya están publicadas en Google a `history.jsonl`. Escoge las mejores (mezcla de 5★, 3★ y negativas) y ponlas en `examples.md`; el agente las usa automáticamente como referencia.

## Contraseña de aplicación para info@

Cuenta de Google de info@theoystershackpr.com → Seguridad → Verificación en 2 pasos (activar) → Contraseñas de aplicaciones → crear "Oyster Reviews". Pega las 16 letras en `SMTP_APP_PASSWORD`.

## Archivos

| Archivo | Qué es |
|---|---|
| `agent.py` | El agente |
| `system_prompt.md` | Reglas duras y criterios de 🚩 |
| `voice_guide.md` | Enlace a `conocimiento/reviews/guia-voz.md` (edita allá) |
| `examples.md` | (opcional) respuestas reales que quieres que imite |
| `empleados.csv` | Empleados y apodos para contar menciones |
| `menciones.csv` | Registro de menciones (local) |
| `state.json` | Reviews ya procesados, para no repetir |
| `agent.log` | Log de cada corrida |
