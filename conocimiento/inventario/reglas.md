# Reglas de inventario — The Oyster Shack (para OpenClaw)

Versión de prueba v0.1, 16 nov 2026, construida sobre el conteo de Bryan (GRUPO 1–10).

## 1. Formato que llega
El conteo llega como un solo mensaje de WhatsApp dividido en `GRUPO 1` … `GRUPO 10`. El nombre que sigue a `GRUPO 1` es quien hizo el conteo.

```
Producto — PROVEEDOR — (MÍNIMO) (PAR) — CONTEO [unidad] [notas] [🚨]
```

| Pieza | Significado |
|---|---|
| (MÍNIMO) | Primer número entre paréntesis: lo mínimo que debe haber a la mano. Si el conteo llega a este número o baja de él, hay que pedir. |
| (PAR) | Segundo número entre paréntesis: el par level, la cantidad a la que se rellena. |
| CONTEO | Lo que hay hoy. Es el número que va después del último guion. |
| 🚨 | Alerta manual de quien contó: 🚨 = bajito, 🚨🚨 = urgente, 🚨🚨🚨 = agotado. |
| "no comprar" | No se pide aunque esté bajo. |

### Códigos de proveedor
S Sam's · C Costco · A Amazon · DE Denarius · JS José Santiago · SW Seaword · DC DC Produce · D Dockside · JP Janes Pastry · DN Doña Lola · M Méndez · R Reds · B Ballester · P Pangeas · PE Pepín · H Hidropónicos.
`S-C` o `DC-S` significa proveedor principal y alterno.

## 2. Cómo se clasifica cada producto
| Estado | Regla |
|---|---|
| agotado | conteo = 0, o conteo vacío con 🚨🚨🚨 |
| bajo_minimo | conteo ≤ mínimo |
| bajo_par | mínimo < conteo < par |
| ok | par ≤ conteo ≤ 1.5 × par |
| sobre_par | conteo > 1.5 × par (posible sobrecompra o error de unidad) |
| sin_datos | falta el par o el conteo |

**Pedido sugerido** = par − conteo, solo para productos agotados, bajo mínimo o bajo par, y nunca si dice "no comprar". Se agrupa por proveedor principal.

## 3. Lo que OpenClaw NO puede asumir (va a `log/…_revisar.csv`)
1. Conteo vacío sin 🚨🚨🚨: no se asume 0. Hay que preguntarle a quien contó.
2. Código de proveedor que no está en la leyenda (en esta prueba: `DL` en Mozzarella y `J` en Malanga chips).
3. Línea sin proveedor o con un solo número entre paréntesis (por ejemplo Queso mixto, Salt, Wasabi, Lobster tail, Esponja, Brillo verdes, Degreaser, Vinagre Arroz, Avocado).
4. **Unidad del conteo distinta a la del par.** Ejemplos: Lobster roll (par 37, conteo "3 box") y Malanga chips (par 70, conteo "2 1/2 box"). Sin la unidad en el catálogo, el pedido sale inflado.
5. Conteo mixto, como Leche de coco "7 de cartón, 6 de latas". Se suma, pero queda marcado.
6. Alerta manual que no coincide con el cálculo, en cualquiera de los dos sentidos. Puede ser un par mal puesto o un error de conteo.
7. Un producto que no está en `catalogo/productos.csv` va a pendientes. No se crea solo.

## 4. Fuente de verdad
- `catalogo/productos.csv` manda sobre el mensaje en mínimo, par, unidad y proveedor. Si el mensaje trae un par distinto al del catálogo, se marca la diferencia y no se sobrescribe el catálogo.
- Todo registro en `parsed/` guarda `linea_original` para que se pueda rastrear.

## 5. Lista fija de administración
Cada lunes en Sam's se compra: 1 cherries, 1 centerpull paper, 1 galón de alcohol, 1 blueberries y bolsas negras Power Flex 33. Se añade al pedido de Sam's de los lunes sin importar el conteo.

## 6. Pendiente de confirmar con Joseph
- [ ] ¿El primer número es el mínimo (punto de pedido)? Así lo interpreta esta versión.
- [ ] La unidad de cada producto: porción, box, bag, pack o unidad.
- [ ] Los códigos `DL` y `J`.
- [ ] Si el pedido debe rellenar hasta el par o pedir en múltiplos de caja del proveedor.
