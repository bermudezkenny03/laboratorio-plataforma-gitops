# Inventario de fuentes para RAG

| # | Fuente | Información que aporta | Pregunta que responde |
|---|---|---|---|
| 1 | catalog-info.yaml | Dueño, sistema, ciclo de vida y enlaces | ¿Quién es el propietario? |
| 2 | catalog-grupos.yaml | Equipo y correo de soporte | ¿A quién contacto? |
| 3 | catalog-sistema.yaml | Sistema al que pertenece | ¿En qué sistema está? |
| 4 | docs/index.md (copiado como `fuentes/index.md`) | Despliegue GitOps y soporte | ¿Cómo se despliega? |
| 5 | golden-path.md | Flujo completo del Golden Path | ¿Cuáles son los pasos? |

El contexto que recibe el modelo es la concatenación de las cinco fuentes, en ese orden,
en `fuentes/contexto-rag.txt`. Cada fuente va precedida de una línea
`### FUENTE: <archivo>` para que el modelo pueda citarla.

## Regla para el LLM

Responde únicamente con información presente en las fuentes proporcionadas.
Si no encuentras la respuesta, di:
"No encuentro esta información en las fuentes proporcionadas."
