# Laboratorio: plataforma interna con Backstage, Golden Path, GitOps y Argo CD

Golden Path en el que una desarrolladora crea un servicio desde una plantilla, el servicio
queda registrado en el catálogo de Backstage, sus manifiestos se versionan en un
repositorio GitOps y Argo CD los sincroniza automáticamente hacia Kubernetes.

Servicio de ejemplo: **`gestion-acueductos-api`** (equipo `equipo-datos-agua`,
sistema `plataforma-gestion-agua`).

## Estructura

```text
laboratorio-plataforma-gitops/
├── golden-path.md                      # Actividad 2
├── plantilla-servicio-backend/         # Actividad 3
│   ├── plantilla-minima.md
│   ├── valores-ejemplo.yaml
│   ├── gitops/argocd-application.yaml
│   └── skeleton/
│       ├── README.md
│       ├── catalog-info.yaml
│       ├── mkdocs.yml
│       ├── docs/index.md
│       ├── app/main.py, requirements.txt, tests/
│       ├── k8s/ (namespace, deployment, service)
│       └── .github/workflows/ci.yml
├── repo-aplicacion/                    # Actividad 4 (+ archivos generados por la plantilla)
│   ├── catalog-info.yaml
│   ├── catalog-grupos.yaml
│   ├── catalog-sistema.yaml
│   └── catalog-location.yaml
├── repo-gitops/                        # Actividad 5 (lo que vigila Argo CD)
│   └── apps/gestion-acueductos-api/
│       ├── namespace.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       └── argocd-application.yaml
├── docs/index.md                       # Actividad 7
├── fuentes/                            # Actividades 1 y 8
│   ├── consumidor.md
│   ├── inventario-rag.md
│   ├── contexto-rag.txt
│   └── (copias de las 5 fuentes RAG)
├── evidencias/                         # Actividades 6, 8 y 9
│   ├── rag-evaluacion.md
│   ├── demostracion.md
│   ├── entorno-de-ejecucion.md
│   ├── capturas/                       # UI de Argo CD: Synced / Healthy
│   └── salidas/                        # salidas reales de kubectl, argocd y validaciones
└── scripts/
    ├── generar-servicio.py             # aplica la plantilla con sus validaciones
    ├── validar-catalogo-backstage.py   # valida el catálogo con los esquemas de Backstage
    └── rag-consulta.py                 # contexto RAG + consulta a Ollama
```

## Rúbrica y evidencias

| Criterio | Puntaje | Evidencia |
|---|---|---|
| Consumidor identificado | 2 | `fuentes/consumidor.md` |
| Golden Path GitOps completo | 3 | `golden-path.md` |
| Plantilla mínima con manifiestos | 3 | `plantilla-servicio-backend/`, `evidencias/salidas/03-plantilla-generacion-y-validaciones.txt` |
| Catálogo Backstage correcto | 2 | `repo-aplicacion/catalog-info.yaml`, `evidencias/salidas/04-validacion-catalogo-y-yaml.txt` |
| Repositorio GitOps con manifiestos | 3 | `repo-gitops/apps/gestion-acueductos-api/` |
| Aplicación Argo CD configurada | 3 | `repo-gitops/apps/gestion-acueductos-api/argocd-application.yaml` |
| Despliegue sincronizado y healthy | 2 | `evidencias/capturas/`, `evidencias/salidas/06-*.txt` |
| RAG evaluado con fuentes | 1 | `evidencias/rag-evaluacion.md` |
| Demostración integradora | 1 | `evidencias/demostracion.md` |

## Ejecutarlo en tu equipo (kind)

Requisitos: Git, Docker, kubectl, kind, la CLI de Argo CD y Python 3.11+.

```bash
git clone https://github.com/bermudezkenny03/laboratorio-plataforma-gitops.git
cd laboratorio-plataforma-gitops

# Bloque 0: clúster
kind create cluster --name laboratorio-gitops
kubectl get nodes

# Actividad 6: Argo CD (--server-side evita el error "annotations: Too long" del CRD)
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# En otra terminal
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Contraseña inicial de admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
argocd login localhost:8080 --insecure --username admin

# Crear la aplicación desde el repositorio GitOps
kubectl apply -f repo-gitops/apps/gestion-acueductos-api/argocd-application.yaml
argocd app get gestion-acueductos-api
kubectl get pods -n gestion-acueductos-api
```

En Windows PowerShell la contraseña se decodifica con:
`[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}")))`

### Probar el flujo GitOps

```bash
# Paso 6.5: cambiar replicas en repo-gitops/apps/gestion-acueductos-api/deployment.yaml
git commit -am "Escalar gestion-acueductos-api a 3 réplicas" && git push origin main
argocd app get gestion-acueductos-api --refresh   # sin --refresh, Argo CD lo detecta en su sondeo (~3 min)

# Paso 6.6: autocorrección
kubectl scale deployment gestion-acueductos-api -n gestion-acueductos-api --replicas=1
kubectl get pods -n gestion-acueductos-api -w
```

### Backstage

```bash
npx @backstage/create-app@latest
cd <tu-app> && yarn start
```

En Backstage: **Create → Register Existing Component** y pega
`https://github.com/bermudezkenny03/laboratorio-plataforma-gitops/blob/main/repo-aplicacion/catalog-location.yaml`
(registra el componente, el grupo y el sistema de una vez).

### RAG con Ollama

```bash
ollama pull llama3.2
python scripts/rag-consulta.py                      # genera evidencias/rag-respuestas-ollama.md
python scripts/rag-consulta.py --verificar-fuentes  # trazabilidad sin LLM
```

## Ajustes respecto al enunciado

- **Un solo repositorio.** `repo-aplicacion/` y `repo-gitops/` son carpetas de este repositorio;
  la Application de Argo CD apunta a `repo-gitops/apps/gestion-acueductos-api`.
- **Instalación de Argo CD con `--server-side --force-conflicts`.** El `kubectl apply` del
  enunciado falla porque la anotación del CRD `applicationsets.argoproj.io` supera 256 KB.
- **`backstage.io/source-location`** estaba partido en dos líneas en el enunciado; aquí va en una
  sola línea con el prefijo `url:`.
- **`backstage.io/techdocs-ref: dir:.`** con `mkdocs.yml` en la raíz del repositorio de aplicación:
  TechDocs busca `mkdocs.yml` en la carpeta indicada, por eso `dir:./docs` no funcionaría.
- **Tiempo de detección (paso 6.5).** Sin webhook, Argo CD revisa Git cada ~3 minutos; en la
  prueba tardó 2 min 46 s. `argocd app get --refresh` fuerza la revisión inmediata.
- **Código base en la plantilla** (`app/main.py` con `/health`, pruebas y `requirements.txt`) para
  que el README generado (`uvicorn app.main:app`) sea ejecutable.
- **Pregunta de control en el RAG** (IP pública de producción) para comprobar que el modelo no
  inventa datos operativos.

El flujo de GitHub Actions `.github/workflows/validar-laboratorio.yml` valida en cada push los
YAML, el catálogo contra los esquemas de Backstage, que la plantilla genera los mismos
manifiestos del repositorio GitOps, las pruebas del código base y la trazabilidad RAG.
