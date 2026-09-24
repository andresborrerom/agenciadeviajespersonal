# Modelo de calificación (scoring) — spec

Este documento define cómo el agente verificador calcula un **rating
general (0–100)** por candidato, combinando varias variables con pesos
configurables por el usuario. Aplica primero a hoteles; el mismo mecanismo
se reutiliza para vuelos/carros/golf cuando toque construirlos (cada
vertical define sus propias variables, pero la fórmula y el manejo de
pesos es el mismo).

## Por qué no un filtro binario

Un mínimo tipo "descarta todo lo que no llegue a 8.4" trata igual a un
hotel de 7.3 que a uno de 9.5 si ambos pasan (o descarta de más si ambos
no pasan). Un **rating ponderado y continuo** deja pasar más candidatos
(mínimo más bajo) pero los sigue diferenciando entre sí, en vez de
tratarlos como aprobado/reprobado.

## Filtro duro (gate) antes de calificar

Un candidato ni siquiera entra al cálculo si:
- Reviews por debajo de **7.0** (antes 8.4 — relajado a pedido del
  usuario) en Booking o Google.
- Está agotado / no disponible para las fechas pedidas.
- No cumple la categoría mínima pedida, salvo que el usuario la relaje
  explícitamente para ese pedido.

Todo lo que pasa el gate se califica con la fórmula de abajo — el gate ya
no decide "bueno vs. malo", solo filtra lo claramente descartable.

## Variables (0.0–1.0 cada una, luego ponderadas)

| Variable | Cómo se normaliza | Nota |
|---|---|---|
| `reviews` | Ajuste bayesiano: `adj = (n/(n+k))*raw + (k/(n+k))*prior`, con `k=100`, `prior=7.5` (promedio de categoría). Luego `raw/10`. Penaliza automáticamente ratings altos con pocas reseñas (ej. un 10.0 con 5 reseñas pesa menos que un 8.8 con 3,000). | `n` = número de reseñas, `raw` = rating crudo /10. |
| `distancia` | `max(0, 1 - distancia_caminando_m / D_max)`, `D_max` configurable (default 1600 m ≈ 20 min). | Ver metodología de distancia abajo — **no** se usa la distancia en línea recta al "centro" del punto de interés, ni el bounding box, por el sesgo de la cuadrícula de Manhattan (ver nota). |
| `precio` | 1.0 si `precio <= ideal`; decae lineal de 1.0 a 0.3 entre `ideal` y `techo`; decae de 0.3 a 0 entre `techo` y `1.5×techo`. | `ideal` y `techo` vienen del pedido del usuario (ej. $350 / $750). |
| `categoria` | Tabla: 5★=1.0, boutique 4★ equivalente=0.85, 4★ oficial=0.85, 3★=0.5, "tourist class"/2★=0.35, sin categoría=0.2. | Verificar la categoría real, no solo el marketing del sitio (ej. un hotel puede llamarse "boutique" y ser oficialmente 2★). |
| `camas` | 1.0 = configuración pedida confirmada disponible; 0.5 = ambigua/sin confirmar; 0.0 = confirmado que NO hay la configuración pedida. | Refleja qué tan segura está la info, no solo si existe la categoría de cuarto en el sitio del hotel. |
| `cancelacion` | 1.0 = cancelación gratis disponible; 0.5 = flexible con cargo / no verificado; 0.0 = no reembolsable. | Ligado al principio de preferir cancelación gratis si la diferencia de precio es <10%. |
| `zona_seguridad` | Lista curada en `perfil/viajeros.yaml` (no hay API de criminalidad conectada hoy) — placeholder hasta tener una fuente real de datos. | Ver "Variables futuras" — candidata a mejorar con un índice real. |

## Pesos por defecto (ajustables por el usuario)

Viven en `perfil/viajeros.yaml` bajo `preferencias.hoteles.pesos_scoring`.
Deben sumar 1.0 (el script los renormaliza si no suman exacto).

```yaml
reviews: 0.30
distancia: 0.20
precio: 0.20
camas: 0.10
categoria: 0.10
cancelacion: 0.05
zona_seguridad: 0.05
```

`overall = Σ (peso_i × variable_i) × 100`

## Metodología de distancia (cómo se calculó, no solo "según Google dice")

1. Geocodificar la dirección exacta del hotel (Nominatim/OpenStreetMap).
2. Geocodificar el polígono real del punto de interés (ej. Central Park
   completo, no un punto ni un bounding box — Manhattan está rotado ~29°
   respecto al norte real, así que un bounding box mete millas de más o de
   menos según el lado del hotel).
3. Calcular la distancia mínima en línea recta del hotel al borde del
   polígono (punto a segmento, para cada arista).
4. Aplicar un factor de corrección de cuadrícula (`1.3×`) para aproximar
   distancia caminando real (las calles no son línea recta).
5. El resultado son metros y minutos caminando aproximados — **no
   sustituye una API de rutas real** (Google/Mapbox Directions), que
   daría la ruta real incluyendo semáforos, cruces cerrados, etc. Cuando
   se conecte una de esas APIs, esta metodología se reemplaza.

Script de referencia: `scripts/distancia_a_punto.py`.

## Variables futuras (candidatas, requieren datos que no tenemos hoy)

- **Recencia de reseñas** (últimos 12 meses vs. históricas) — hoy los
  agregadores no siempre exponen esto en snippets de búsqueda.
- **Amenities relevantes** (desayuno incluido, A/C, gimnasio, piso
  alto/vista, accesibilidad) — se podría ponderar como variable aparte en
  vez de mezclarlo en "categoría".
- **Coincidencia con programas de lealtad** del perfil — bono, no
  reemplazo, si la marca del hotel coincide con un programa guardado en
  `perfil/viajeros.yaml`.
- **Transparencia de impuestos/cargos**: penalizar si el total final con
  impuestos difiere mucho del precio anunciado (resort fees ocultos, etc.)
  — requiere verificación en pantalla real.
- **Tamaño de habitación** (m²/sq ft) — relevante para 2 adultos + equipaje,
  hoy sale mencionado en reseñas de forma no estructurada.
- **Ruido/tranquilidad** — señal cualitativa de reseñas (ej. "paredes
  delgadas" en Belleclaire), difícil de cuantificar sin NLP sobre reseñas
  reales.
- **Índice de seguridad real por zona** (ej. datos de NYPD por precinto) en
  vez de la lista curada manual que usamos hoy en `zona_seguridad`.
- **Walk Score / Transit Score** vía API, si se conecta una.
- **Punto de interés ancla configurable por búsqueda**: hoy usamos Central
  Park como ancla fija para este pedido, pero el ancla debería ser un
  parámetro del pedido (ej. otra vez podría ser la universidad de la hija,
  una oficina, un estadio de golf), no algo hardcodeado.
- **Confianza del dato** (`verificado_en_vivo: true/false`): no se mete en
  el score (mezclaría "calidad del hotel" con "calidad del dato"), pero se
  muestra siempre junto al resultado como metadato de confianza.
