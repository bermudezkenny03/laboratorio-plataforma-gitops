# {{ nombre_servicio }}

{{ descripcion }}

## Requisitos

- Python 3.11 o superior
- Git

## Ejecución local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Verificación

```bash
curl http://localhost:8000/health
```

## Despliegue

El despliegue se realiza mediante GitOps y Argo CD.
Los manifiestos Kubernetes se encuentran en la carpeta `k8s/`.

- Repositorio GitOps: {{ repositorio_gitops }}
- Equipo propietario: {{ owner }}
- Soporte: {{ canal_soporte }}

> Mientras no exista un pipeline que publique la imagen del servicio, el Deployment
> usa `nginx:1.27-alpine` como imagen de marcador para validar el flujo GitOps.
