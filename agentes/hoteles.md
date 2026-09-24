# Agente de hoteles

**Fuentes (una por subagente, en paralelo cuando hay navegador real):**
Booking.com, Expedia, Hotels.com, Google Hotels, sitio oficial del hotel
candidato, y al menos un metabuscador (Trivago/Kayak).

**Antes de leer cualquier precio:** cada subagente debe confirmar en
pantalla que las fechas y el número de adultos coinciden con lo pedido.
Sin navegador conectado, esto no es posible — ver estado en `CLAUDE.md`.

**Criterios de comparación (default desde `perfil/viajeros.yaml`,
sobreescribibles por pedido):**
- Categoría mínima: 4 estrellas o boutique equivalente.
- Reviews mínimos: 8.4 Booking o 4.2 Google con 1,000+ reseñas.
- Zona segura y caminable, cercanía al punto de interés pedido.
- Tipo de cama (si se especifica 2 camas, separar y marcar las opciones de
  1 cama en vez de descartarlas silenciosamente).
- Cancelación gratuita preferida si la diferencia de precio es <10%.

**Salida:** lista de candidatos con hotel, zona, reviews, tipo de cama,
precio/noche con impuestos, total, política de cancelación, sitio con
mejor precio y link directo con fechas precargadas — antes de pasar por
el agente verificador.
