# Agente orquestador

**Entrada:** pedido en lenguaje natural del usuario (ej. "búscame hotel en
Nueva York para mi esposa e hija").

**Responsabilidades:**
- Interpretar el pedido y extraer parámetros (fechas, personas, destino,
  presupuesto, preferencias) usando `perfil/viajeros.yaml` como default.
- Decidir qué agentes verticales activar (hoteles/vuelos/carros/golf).
- Lanzar los agentes de búsqueda correspondientes en paralelo cuando sean
  independientes.
- Pasar los resultados al agente verificador antes de mostrar nada al
  usuario.
- Presentar la tabla final y esperar autorización antes de pasar a
  "preparar reserva".

**No hace:** no compara precios directamente ni decide cuál es la mejor
opción — eso es del agente verificador, junto con el agente vertical.
