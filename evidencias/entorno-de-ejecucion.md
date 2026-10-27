# Entorno donde se generaron las evidencias

Las salidas de `evidencias/salidas/` y las capturas de `evidencias/capturas/` se obtuvieron
en una máquina virtual Linux (Ubuntu 24.04, 2 CPU, 8 GB RAM) **sin acceso a los registros
públicos de contenedores** (Docker Hub, quay.io, public.ecr.aws, ghcr.io) ni a PyPI, npm u
Ollama; solo tenía salida hacia GitHub. Por eso hubo que adaptar el entorno, no los
archivos del laboratorio. En un equipo con Internet y kind ninguna de estas adaptaciones
es necesaria.

| Componente | Lo que pide el laboratorio | Lo que se usó para las evidencias | Motivo |
|---|---|---|---|
| Clúster | kind `laboratorio-gitops` | k3s v1.37.1, nodo único `laboratorio-gitops`, contexto `laboratorio-gitops` | kind necesita descargar la imagen `kindest/node` de Docker Hub. |
| kubectl | 1.29+ | v1.37.1 (incluido en k3s) | — |
| Argo CD | estable | v3.5.6, `install.yaml` oficial del tag v3.5.6 | — |
| Instalación de Argo CD | `kubectl apply -n argocd -f install.yaml` | `kubectl apply -n argocd --server-side --force-conflicts -f install.yaml` | El `apply` normal falla con `metadata.annotations: Too long` en el CRD `applicationsets.argoproj.io` (pasa igual en kind). |
| Imágenes de contenedor | se descargan de sus registros | construidas localmente con los mismos nombres y servidas por un espejo de registro local configurado en k3s | Sin acceso a registros. Los manifiestos se aplicaron **sin modificar**. |
| `quay.io/argoproj/argocd:v3.5.6` | imagen oficial | binario oficial `argocd` v3.5.6 (release de GitHub) + git y gpg | ídem |
| `redis:8.2.3-alpine` | imagen oficial | redis-server 7.0.15 | ídem |
| `nginx:1.27-alpine` | imagen oficial | nginx 1.27.5 compilado desde el código fuente oficial | ídem |
| Dex (SSO) | incluido en `install.yaml` | escalado a 0 réplicas | No se usa SSO; el acceso es con el usuario `admin`. |
| Acceso de Argo CD a GitHub | directo | `argocd-repo-server` con `HTTPS_PROXY` hacia el proxy de salida del entorno | La red del entorno solo sale por proxy. |
| Backstage | `npx @backstage/create-app` | no se pudo instalar (sin npm); el catálogo se validó con los JSON Schema oficiales de Backstage | Ver `salidas/04-validacion-catalogo-y-yaml.txt`. |
| Ollama + llama3.2 | LLM local | no disponible (sin acceso al registro de modelos); se verificó la trazabilidad de las fuentes y el script de consulta | Ver `rag-evaluacion.md`. |

## Lo que sí se ejecutó de punta a punta

- Generación del servicio con la plantilla y sus validaciones (`salidas/03-...`).
- Validación YAML del paso 4.3, dry-run de servidor de los manifiestos y validación del
  catálogo con los esquemas de Backstage (`salidas/04-...`).
- Instalación de Argo CD, login con la CLI y creación de la Application desde el
  manifiesto del repositorio GitOps (`salidas/06-1-...`, `salidas/06-4-...`).
- Sincronización desde GitHub (`https://github.com/bermudezkenny03/laboratorio-plataforma-gitops`)
  hasta **Synced / Healthy** con el pod **Running** y el servicio respondiendo HTTP 200.
- Paso 6.5: commit `Escalar gestion-acueductos-api a 2 réplicas` → Argo CD lo detectó solo
  (en su sondeo periódico de ~3 min, sin refresh manual) y el clúster quedó con 2 pods.
- Paso 6.6: `kubectl scale --replicas=1` manual → `selfHeal` restauró las 2 réplicas en ~2 s.
- Capturas de la interfaz web de Argo CD (`capturas/`).
