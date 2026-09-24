# Logs de búsquedas

Un archivo `YYYY-MM-DD.jsonl` por día, una línea JSON por búsqueda. Ver el
formato exacto y un ejemplo en `CLAUDE.md` → "Formato de log de búsquedas".

Campos mínimos: `timestamp`, `vertical`, `agente`, `fuente`, `parametros`,
`resultados_resumen`, `verificado_en_vivo` (bool), `notas`.
