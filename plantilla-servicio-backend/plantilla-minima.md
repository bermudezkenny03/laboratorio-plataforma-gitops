# Plantilla mínima: Servicio Backend GitOps

Plantilla del Golden Path que genera el repositorio de aplicación y la carpeta del
servicio en el repositorio GitOps. Las variables usan la sintaxis `{{ variable }}`.

## Campos solicitados

| Campo | Ejemplo |
|---|---|
| nombre_servicio | gestion-acueductos-api |
| titulo_servicio | API de Gestión de Acueductos |
| descripcion | API para consultar información de acueductos |
| owner | group:equipo-datos-agua |
| sistema | plataforma-gestion-agua |
| organizacion | bermudezkenny03 |
| ciclo_vida | experimental |
| canal_soporte | #soporte-datos-agua |
| repositorio_gitops | https://github.com/bermudezkenny03/laboratorio-plataforma-gitops.git |
| ruta_apps_gitops | repo-gitops/apps |

Los valores de ejemplo están en `valores-ejemplo.yaml`.

## Archivos generados

Repositorio de aplicación (`skeleton/`):

- README.md
- catalog-info.yaml
- mkdocs.yml
- docs/index.md
- app/main.py, requirements.txt, pytest.ini, tests/test_main.py (código base FastAPI con `/health`)
- k8s/namespace.yaml
- k8s/deployment.yaml
- k8s/service.yaml
- .github/workflows/ci.yml

Repositorio GitOps (`gitops/` → `<ruta_apps_gitops>/<nombre_servicio>/`):

- namespace.yaml
- deployment.yaml
- service.yaml
- argocd-application.yaml

## Validaciones

- El nombre del servicio debe ser único (no puede existir ya en el repositorio GitOps)
  y cumplir el formato de nombres de Kubernetes: minúsculas, números y guiones.
- El owner debe existir en el catálogo (`kind: Group` en `catalog-grupos.yaml`).
- La descripción debe tener al menos 20 caracteres.
- El repositorio GitOps debe ser una URL válida (`https://...`).
- El ciclo de vida debe ser `experimental` o `production`.

## Cómo generar un servicio con la plantilla

```bash
python scripts/generar-servicio.py \
  --valores plantilla-servicio-backend/valores-ejemplo.yaml \
  --salida-app repo-aplicacion \
  --raiz-gitops . \
  --catalogo-grupos repo-aplicacion/catalog-grupos.yaml
```

El script valida los campos, reemplaza las variables y comprueba que cada YAML generado
sea válido. Con `--sobrescribir` permite regenerar un servicio existente.
