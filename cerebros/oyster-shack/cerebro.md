# CEREBRO · The Oyster Shack

> Documento central. Todo lo que se produzca lee de aquí. Lo que falta se marca `[FALTA]`, nunca se inventa.
> Estado: v1 · 17-nov-2026 · consolidado de los chats y el Project "The Oyster Shack Analysis".

## 0. Ficha
| Campo | Dato |
|---|---|
| Nombre | The Oyster Shack (Est. 2021) |
| Entidad | New Capital Venture LLC |
| Ubicación | Condado, San Juan, Puerto Rico |
| Concepto | Seafood restaurant / oyster bar: ostras frescas de varias procedencias, mariscos, sabores puertorriqueños y caribeños, ambiente relajado con interior y terraza |
| Posicionamiento | "One of the widest selections of fresh oysters in Puerto Rico" (no decir "the largest" sin documentación) |
| POS | Clover (conector propio `OYSTER_SHACK_CLOVER`) |
| Nómina | ADP Workforce Now |
| Propinas | TipHaus |
| Email operativo | info@theoystershackpr.com |
| Instagram | @theoystershackpr |
| Marketing Manager | Joseph Rodríguez · josephrodz.ai@gmail.com |

## 1. Vocabulario de la casa
- **Oyster Bar** = el equipo de barra. Nunca "bartenders".
- **"App X"** en Clover = el mismo plato y precio que "X", servido como aperitivo (cambia el tiempo de salida, no el plato).
- **86** = no disponible. Se marca, no se borra.
- **Shuckers**: abren ostras en el Oyster Bar.
- **Captain**: rol de piso entre server y gerencia.

## 2. Ostras
**Tiers en Clover** (cada semana se clasifica lo que entra, usando nombres ya usados en Clover como referencia):
- **Unique**: todas las XL, Belon y Washington State (Kumamoto, Oishii, etc.). Se venden sueltas, una variedad.
- **Premium**: Canada, PEI, Maine, New Hampshire.
- **East Coast**: el resto de la costa este.
- East Coast y Premium: 1, 6 o 12 ostras (1 o 6 = una variedad; 12 = hasta dos variedades). Todas las opciones bajo un solo botón "Oysters".
- Precios sueltas en Clover (nov 2026): East Coast $4 · Premium $4.50 · Unique $4.75. Half/Dozen: East Coast $22/$38 · Premium $26/$46.
- Disponibilidad: se actualiza desde una **foto del pizarrón del raw bar**; lo que ya no está, se pone en 86.

## 3. Menú (lo que más vende, 1 ago–3 nov 2026)
Ventas de menú $415,745 (comida $304,017 · bebida $111,728), 4,396 órdenes. Detalle en `data/` y `conocimiento/menu-engineering/`.
- Raw bar: Unique sueltas, East Coast y Premium por media/docena, Endless Summer Oyster Shooter.
- Calientes estrella: Rockefeller ($26), Charbroiled ($25), Garlic Butter Shrimp, Award Winning Oysters.
- Mains estrella: Lobster Roll ($32), Snow Crab, 12oz Angus Churrasco, Crab Cakes, Lobster Tail.
- Ceviches: Seafood Medley, Mahi, Shrimp, Guacamole.
- Bebidas: Margaritas 2x1 Endless Summer, Piña Colada, Shack Pain Killer, Martini, Medalla.
- **Seafood Tower**: plato nuevo y más exclusivo; foco de la campaña con Platea (nov 2026).

## 4. Operación
- Inventario: un mensaje largo de WhatsApp por conteo (GRUPO 1–10), reglas en `conocimiento/inventario/reglas.md`.
- Reporte diario del grupo: también un mensaje largo de WhatsApp.
- Facturas: se quiere que cocina suba facturas de compra al recibir pedidos `[FALTA: flujo]`.
- Compra fija de los lunes en Sam's: cherries, centerpull paper, galón de alcohol, blueberries, bolsas negras Power Flex 33.
- Labor (ago–nov 2026): staffing de cena casi plano todos los días aunque la demanda no lo es; detalle en `conocimiento/labor/`.
- Contraseñas compartidas: migrando de una Google Sheet en Dropbox a 1Password.

## 5. Herramientas internas ya hechas
Distribución de propinas (TipHaus vs pool manual) · auditoría del cash log (9+ meses de Clover) · app de horarios ·
generador de specials · SOP de cierre de caja · guía de TipHaus (+ versión para empleados) · manual de cócteles ·
Recipe Hub (Excel, 50+ pestañas) · checklist Server-Captain · rediseño del manual de Shucker · guía de bebidas ·
tutorial del oyster board para DLE Play · SOP de rollos de papel de Clover · reporte de items removidos ·
cheat sheet de raw bar (pedido BT-4767, Everglades Oysters) · Training Hub con quizzes · landing (oyster-shack-pr.html).

## 6. Activos y dónde viven
| Activo | Dónde |
|---|---|
| Training (285 archivos) | Dropbox `/Oyster Shack/Capacitacion de Empleados` (no mover nada) |
| Recipe Hub | Dropbox `/Oyster Shack/Capacitacion de Empleados/Kitchen/The Oyster Shack Recipe Hub.xlsx` |
| Fotos de menú | Dropbox "Master Photos Folder - The Oyster Shack" (organizar por sección, una carpeta por plato) |
| Menú exterior oficial | https://claude.ai/artifact/XE6zgJ5yqoMJ6f1CbU6oZc (versión 1794408383-6d2a) |
| Training Hub | https://claude.ai/artifact/MZ43XwtdDMgtBzQD2GKxcJ |
| Reporte Fase 1 | https://claude.ai/artifact/Y6wXB3yn6taxMLUcVRoSR4 |
| Labor vs mesas (sheet) | https://claude.ai/artifact/Ay8hkvR5hQnqmjiFC6QhWp |

## 7. Proyectos abiertos
Bot de WhatsApp (Baileys) · agente de reviews · menú completo 2027 (6 páginas) · Oyster Shucking / Tasting Experience ·
videos de training (empezando por Host Operations Manual) · conexión con ADP · Fase 2 de menu engineering (faltan costos) ·
limpieza de Clover por categoría (empezando por Hot Plates). Ver `pendientes/PRIMERAS-MISIONES.md`.

## 8. Producto a futuro
**Mesa / Restaurant OS**: empaquetar estas herramientas para otros restaurantes. Casa Lucca es el cliente #2 de prueba
(su conector de Clover es un clon de este). Recomendación vigente: vender primero la Fase 1 como servicio.
