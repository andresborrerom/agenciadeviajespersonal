# Agencia de Viajes Personal — CLAUDE.md

Este repositorio es la "agencia de viajes personal" de Andrés: un sistema de
agentes que busca, compara y (solo con autorización explícita) deja lista
para pago la mejor opción de vuelos, hoteles, carros y tee times de golf.
Cualquier sesión de Claude que trabaje en este repo debe operar bajo las
reglas de este archivo.

## Estado actual del proyecto (leer primero)

- **Fase 0 en curso.** Todavía no existe código de agentes. Lo que existe hoy
  es: este CLAUDE.md, el perfil de viajeros, la estructura de carpetas, y
  specs (markdown) de los agentes planeados.
- **Sin navegador real conectado.** Esta sesión no tiene un MCP de
  automatización de navegador (tipo Playwright). Solo hay búsqueda web
  (`WebSearch`) y fetch de páginas (`WebFetch`), que casi nunca renderiza
  sitios de reservas dinámicos (Booking, Expedia, GolfNow son JS-heavy y
  bloquean fetch simple). **No asumas que puedes verificar fechas/precios en
  pantalla ni diligenciar un checkout hasta que se conecte esa herramienta.**
  Mientras tanto, cualquier precio/dato de disponibilidad que produzcas debe
  marcarse explícitamente como "estimado / no verificado en vivo" y el
  usuario debe confirmar en pantalla antes de decidir.
- Decisión tomada: el sistema vive **dentro de Claude Code** (no un servicio
  separado), y el perfil de viajeros se versiona **en este repo** (sin datos
  de pago, nunca).

## Principios no negociables

1. **Nunca** ingreses datos de tarjeta, contraseñas o documentos de
   identidad en ningún sitio. Llega hasta la pantalla de pago con todo
   diligenciado y pide al usuario que complete el pago.
2. **Toda reserva o cargo requiere un "sí" explícito** del usuario en el
   chat, con el resumen exacto: proveedor, fechas, precio total con
   impuestos, política de cancelación — antes de hacer clic en cualquier
   botón de confirmar/pagar/reservar.
3. **Verifica siempre que las fechas mostradas en la página coincidan** con
   las pedidas antes de leer cualquier precio. Un precio de otra fecha es un
   error grave. Si no puedes verificar esto en vivo (ver "Estado actual"),
   dilo explícitamente en vez de dar el precio como confirmado.
4. Prefiere tarifas con **cancelación gratuita** cuando la diferencia de
   precio sea menor al 10 %.
5. **Registra cada búsqueda** en `logs/busquedas/` (ver formato abajo) para
   poder auditar y comparar después.
6. Nunca aceptes términos y condiciones, suscripciones o cargos adicionales
   sin preguntar primero.
7. Si algo se agota o cambia de precio mientras se investiga, avísalo de
   inmediato y no lo dejes en ninguna tabla de resultados como si siguiera
   disponible.

## Módulo de permisos (tres niveles)

| Nivel | Qué incluye | Autorización requerida |
|---|---|---|
| **Buscar** | Consultar disponibilidad, precios, reviews. No modifica nada en ningún sitio externo. | Libre — no requiere permiso caso por caso. |
| **Preparar reserva** | Llenar formularios de reserva hasta (sin incluir) el paso de pago; seleccionar habitación/vuelo/tee time específico. | El agente avisa qué va a preparar antes de hacerlo, pero puede proceder sin esperar aprobación línea por línea. |
| **Pagar** | Cualquier acción que cobre dinero, guarde una tarjeta, o confirme una reserva no reembolsable. | **Siempre el usuario**, con un "sí" explícito sobre el resumen exacto. Nunca el agente. |

## Perfil del viajero

Vive en `perfil/viajeros.yaml`. Nunca debe contener números de tarjeta,
CVV, contraseñas, ni escaneos de documentos de identidad — solo nombres,
preferencias y números de programas de lealtad (que no son medios de pago).
Cualquier agente que necesite preferencias de viaje debe leer ese archivo
primero.

## Arquitectura de agentes (objetivo, se construye por fases)

- **Orquestador**: recibe el pedido en lenguaje natural, lo descompone por
  vertical (vuelos/hoteles/carros/golf) y delega.
- **Agentes especializados por vertical** (hoteles, vuelos, carros, golf):
  cada uno con sus fuentes propias y su lógica de comparación. Ver
  `agentes/` para el spec de cada uno.
- **Agente verificador**: cruza resultados de todos los agentes de búsqueda,
  descarta cualquier precio cuya fecha no coincida, calcula el total real
  con impuestos y cargos, y es quien autoriza que algo llegue a la tabla
  final que ve el usuario.
- Todos corren como subagentes en paralelo cuando las búsquedas son
  independientes entre sí (distintas fuentes, distintos hoteles).

## Formato de log de búsquedas

Un archivo JSONL por día en `logs/busquedas/YYYY-MM-DD.jsonl`, una línea por
búsqueda:

```json
{"timestamp": "2026-09-24T18:00:00Z", "vertical": "hoteles", "agente": "orquestador", "fuente": "websearch", "parametros": {"destino": "New York (UWS/UES)", "checkin": "2026-09-25", "checkout": "2026-09-27", "adultos": 2, "habitaciones": 1}, "resultados_resumen": "4 candidatos comparados, ver tabla en chat", "verificado_en_vivo": false, "notas": "Sin navegador conectado; precios best-effort"}
```

## Modelos recomendados por rol (sujeto a cambio — pide confirmación antes de asumir)

| Rol | Recomendación | Por qué |
|---|---|---|
| Orquestador | Sonnet 5 | Buen balance costo/razonamiento para descomponer pedidos y coordinar subagentes. |
| Agentes de búsqueda por vertical | Sonnet 5 (Haiku 4.5 si el volumen de subagentes en paralelo lo justifica por costo) | Tareas más mecánicas de extracción/comparación. |
| Agente verificador | Opus 5.5 | Es el que evita errores de fecha/precio con dinero real de por medio; vale la pena pagar más por precisión aquí. |

Al final de cada fase, la sesión debe indicar qué modelo recomienda para la
siguiente fase, sin asumir un cambio con `/model` por su cuenta.

## Reglas de repo

- Nunca commitear API keys, tokens ni credenciales. Van como secretos del
  entorno, nunca como archivos en el repo.
- `perfil/viajeros.yaml` se versiona en git, pero solo debe contener datos
  no sensibles (ver arriba). Si en algún momento se necesita guardar algo
  sensible, se saca del repo, no se agrega aquí.
