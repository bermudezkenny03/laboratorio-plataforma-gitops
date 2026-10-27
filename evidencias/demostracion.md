# Demostración integradora

## Duración

3 minutos.

## Orden

| # | Tiempo | Qué mostrar | Qué decir / comando |
|---|---|---|---|
| 1 | 0:00–0:20 | `fuentes/consumidor.md` | Desarrolladora backend junior: hoy pide despliegues a mano, no sabe qué manifiestos crear ni quién es el dueño del servicio. |
| 2 | 0:20–0:40 | `golden-path.md` (diagrama) | Backstage → plantilla → repo de aplicación + repo GitOps → Argo CD → Kubernetes. Criterio de éxito: Synced, Healthy, Running, sin `kubectl apply`. |
| 3 | 0:40–1:00 | `plantilla-servicio-backend/` | `python scripts/generar-servicio.py ...`: valida campos y genera README, catálogo, docs, código, k8s y CI, y la carpeta en el repo GitOps. |
| 4 | 1:00–1:15 | `repo-aplicacion/catalog-info.yaml` en Backstage | Componente `gestion-acueductos-api`, owner `group:equipo-datos-agua`, sistema `plataforma-gestion-agua`, lifecycle `experimental`. |
| 5 | 1:15–1:30 | `repo-gitops/apps/gestion-acueductos-api/` | Namespace, Deployment, Service y Application de Argo CD. |
| 6 | 1:30–1:50 | Argo CD (UI o `argocd app get gestion-acueductos-api`) | Aplicación **Synced** y **Healthy** (captura `capturas/01-argocd-synced-healthy-arbol.png`). |
| 7 | 1:50–2:05 | `kubectl get pods -n gestion-acueductos-api` | Pods en **Running**. |
| 8 | 2:05–2:30 | `python scripts/rag-consulta.py` | Pregunta "¿Cómo se despliega el servicio...?" y mostrar la fuente citada (`index.md` / `golden-path.md`). |
| 9 | 2:30–3:00 | Commit `Escalar gestion-acueductos-api a 2 réplicas` | Un `git push` cambia el clúster (1 → 2 pods); un `kubectl scale --replicas=1` manual es revertido por `selfHeal` en ~2 s. |

## Comandos de la demostración

```bash
argocd app get gestion-acueductos-api
kubectl get pods -n gestion-acueductos-api
git log --oneline -3 -- repo-gitops/

# Cambio en Git -> despliegue
#   editar repo-gitops/apps/gestion-acueductos-api/deployment.yaml (replicas)
git commit -am "Escalar gestion-acueductos-api a N réplicas" && git push origin main
argocd app get gestion-acueductos-api --refresh   # --refresh evita esperar el sondeo de ~3 min

# Autocorrección
kubectl scale deployment gestion-acueductos-api -n gestion-acueductos-api --replicas=1
kubectl get pods -n gestion-acueductos-api -w
```

## Evidencias

- `golden-path.md`
- `plantilla-servicio-backend/plantilla-minima.md`
- `repo-aplicacion/catalog-info.yaml`
- `repo-gitops/apps/gestion-acueductos-api/`
- Captura de Argo CD Synced y Healthy: `evidencias/capturas/01-argocd-synced-healthy-arbol.png`,
  `evidencias/capturas/01-argocd-synced-healthy-lista.png`
- Captura después del cambio en Git y del selfHeal (2 pods): `evidencias/capturas/02-argocd-2-replicas-selfheal-arbol.png`
- Salida de `kubectl get pods` y `argocd app get`: `evidencias/salidas/06-4-aplicacion-synced-healthy.txt`
- Cambio en Git → 2 réplicas: `evidencias/salidas/06-5-cambio-en-git-2-replicas.txt`
- Autocorrección (selfHeal): `evidencias/salidas/06-6-autocorreccion-selfheal.txt`
- `evidencias/rag-evaluacion.md`
