# Agente de Google Reviews · The Oyster Shack

Todos los días a las 6:00am: trae los reviews nuevos de Google, redacta las respuestas con la voz de la marca y manda un email desde info@ a Joseph con:
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
| `state.json` | Reviews ya procesados, para no repetir |
| `agent.log` | Log de cada corrida |
