# Evaluación de respuestas RAG

Fuentes: `fuentes/catalog-info.yaml`, `fuentes/catalog-grupos.yaml`, `fuentes/catalog-sistema.yaml`,
`fuentes/index.md` (copia de `docs/index.md`) y `fuentes/golden-path.md`.
Contexto concatenado: `fuentes/contexto-rag.txt`. Inventario: `fuentes/inventario-rag.md`.

## Pregunta 1

¿Quién es el equipo propietario de la API de Gestión de Acueductos y cómo se solicita soporte?

**Respuesta esperada:**
El equipo propietario es `equipo-datos-agua`. El soporte se solicita en
`#soporte-datos-agua` o al correo `datos-agua@ejemplo.com`.

**Fuente:** docs/index.md (secciones *Ownership* y *Soporte*) y catalog-grupos.yaml (`spec.profile.email`).

## Pregunta 2

¿Cómo se despliega el servicio y qué herramienta sincroniza los cambios?

**Respuesta esperada:**
El servicio se despliega mediante GitOps. Se modifica el repositorio GitOps
y Argo CD sincroniza automáticamente los manifiestos hacia Kubernetes.

**Fuente:** docs/index.md (secciones *Despliegue GitOps* y *Procedimiento de despliegue*) y golden-path.md (pasos 6 a 8).

## Pregunta 3

¿Qué debe verificar la desarrolladora después de que Argo CD sincronice?

**Respuesta esperada:**
Debe verificar que la aplicación esté Synced y Healthy, y que los pods
estén en estado Running.

**Fuente:** docs/index.md (*Procedimiento de despliegue*, pasos 5 y 6) y golden-path.md (*Criterios de éxito*).

## Pregunta 4 (control de alucinación)

¿Cuál es la dirección IP pública del servicio en producción?

**Respuesta esperada:**
"No encuentro esta información en las fuentes proporcionadas."

**Fuente:** ninguna. Sirve para comprobar el criterio de seguridad: el modelo no debe inventar datos operativos.

## Criterios

- Exactitud: usa solo información de las fuentes.
- Trazabilidad: identifica la fuente utilizada.
- Utilidad: responde la necesidad completa.
- Seguridad: no inventa datos operativos.

## Verificación de trazabilidad (ejecutada)

`python scripts/rag-consulta.py --verificar-fuentes` comprueba que cada dato de la respuesta
esperada está en las fuentes citadas. Resultado: **todas las comprobaciones OK**
(salida completa en `evidencias/salidas/08-rag-trazabilidad-fuentes.txt`).

| Pregunta | Datos verificados en las fuentes | Resultado |
|---|---|---|
| 1 | `equipo-datos-agua`, `#soporte-datos-agua`, `datos-agua@ejemplo.com` | OK |
| 2 | `GitOps`, `Argo CD`, `repositorio GitOps` | OK |
| 3 | `Synced`, `Healthy`, `Running` | OK |
| 4 | Las fuentes no contienen ninguna IP pública | OK |

## Respuestas del LLM local (Ollama + llama3.2)

Se generan con:

```bash
ollama pull llama3.2
python scripts/rag-consulta.py
```

El script envía el contexto y las cuatro preguntas a Ollama, guarda las respuestas en
`evidencias/rag-respuestas-ollama.md` y marca cada una como Correcta / Parcial / Incorrecta
según si contiene los datos esperados. Las respuestas parciales o incorrectas se corrigen
en la tabla siguiente indicando la fuente exacta.

| Pregunta | Evaluación del modelo | Corrección (si aplica) y fuente exacta |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

Consulta manual equivalente (paso 8.5 del laboratorio):

```text
ollama run llama3.2
Responde únicamente con la información del siguiente contexto.
Contexto:
[pegue aquí el contenido de fuentes/contexto-rag.txt]
Pregunta:
¿Cómo se despliega el servicio y qué herramienta sincroniza los cambios?
```
