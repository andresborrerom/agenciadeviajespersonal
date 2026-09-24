# Agencia de Viajes Personal

Sistema de agentes (dentro de Claude Code) que busca, compara y —solo con
autorización explícita— deja lista para pago la mejor opción de vuelos,
hoteles, carros de alquiler y tee times de golf para la familia.

**Antes de usar nada de esto, lee `CLAUDE.md`.** Ahí están las reglas no
negociables (nunca pagos automáticos, siempre confirmación explícita,
verificación de fechas, etc.) y el estado real de qué funciona hoy.

## Estado actual

🚧 **Fase 0 — fundamentos.** Todavía no hay código de agentes ejecutable.
Lo que existe:

- `CLAUDE.md` — reglas operativas, arquitectura objetivo, permisos, modelos.
- `perfil/viajeros.yaml` — preferencias de la familia (sin datos de pago).
- `agentes/*.md` — spec de cada agente planeado (orquestador, hoteles,
  vuelos, carros, golf, verificador).
- `logs/busquedas/` — log de cada búsqueda hecha hasta ahora.

⚠️ **Limitación importante:** esta sesión no tiene un navegador real
conectado (tipo Playwright MCP). Eso significa que hoy los agentes pueden
buscar información pública (búsqueda web) pero **no pueden abrir Booking,
Expedia, GolfNow, etc., confirmar fechas en pantalla, ni diligenciar un
checkout real**. Cualquier precio que se reporte sin esa herramienta debe
marcarse como estimado y el usuario debe verificarlo antes de decidir.

## Cómo usarlo hoy

Simplemente pídele a Claude Code, dentro de este repo, lo que necesites
(ej. "búscame vuelos a Madrid en diciembre" o "hotel en Nueva York para mi
esposa e hija"). Claude leerá `CLAUDE.md` y `perfil/viajeros.yaml`
automáticamente y aplicará las reglas de ahí.

Ten en cuenta que, hasta que se conecte automatización de navegador real,
el resultado será una investigación best-effort con links para que tú
verifiques y completes cualquier pago — nunca una reserva ya confirmada.

## Roadmap

| Fase | Entregable |
|---|---|
| 0 (esta) | CLAUDE.md, perfil, estructura, specs de agentes, sin código |
| 1 | Orquestador + agente de hoteles funcionando con búsqueda web (best-effort) |
| 2 | Browser automation conectado (ej. Playwright MCP) → verificación real en pantalla y checkout diligenciado |
| 3 | Agente de vuelos |
| 4 | Agente de carros |
| 5 | Agente de golf (GolfNow, Chronogolf, sitios de club) |
| 6 | Agente verificador formalizado + módulo de permisos como capa transversal |
| 7 | Extensiones: restaurantes, experiencias, seguros de viaje |

Ver `CLAUDE.md` para el detalle de cada fase y las recomendaciones de
modelo por rol.
