---
name: clasificar-ostras
description: Clasifica las ostras que entran cada semana en los tiers de Clover (East Coast / Premium / Unique) y actualiza la disponibilidad desde la foto del pizarrón del raw bar (86, nunca borrar). Úsala cuando Joseph mande el pedido de ostras de la semana o una foto del chalkboard.
---

# Clasificar ostras y actualizar el raw bar en Clover

## Reglas de tier
- **Unique**: toda ostra XL, Belon y cualquier Washington State (ej. Kumamoto, Oishii). Se vende suelta, una variedad.
- **Premium**: Canada, PEI, Maine, New Hampshire.
- **East Coast**: el resto de las ostras de costa este, salvo que sea XL o Belon.
- ⚠️ Ojo: en ventas de ago–nov "Chef Creek - Deep Bay, BC (Can)" se vendió como Unique. Las de la costa oeste de Canadá: confirmar con Joseph.
- Ante la duda, busca primero si el nombre ya existe en Clover (`search_items`) y usa el tier que tiene. Si es nueva y no encaja, pregunta.

## Estructura en Clover
- East Coast y Premium: 1, 6 o 12 (1 o 6 = una variedad; 12 = hasta dos variedades). Unique: sueltas, una variedad.
- Todas las opciones bajo un solo botón/pestaña "Oysters"; las variedades son modifiers.
- Precios actuales (verificar en Clover antes de afirmar): sueltas EC $4 · Premium $4.50 · Unique $4.75; EC $22/$38 · Premium $26/$46.

## Flujo
1. Lee el pedido o la foto del pizarrón. Lista: variedad, procedencia, tamaño si dice XL.
2. Propón la tabla: variedad → tier → ¿existe en Clover? → acción (activar / crear modifier / 86).
3. Variedades que ya no están en el pizarrón → **86 (no disponible), nunca borrar**: vuelven después.
4. **Espera la confirmación de Joseph** antes de escribir en Clover (`set_modifier_availability`, `add_modifiers_to_groups`, etc.).
5. Después de aplicar, confirma qué quedó activo y qué quedó en 86.
