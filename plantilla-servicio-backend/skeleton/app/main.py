"""Código base de {{ nombre_servicio }} generado por la plantilla "Servicio Backend GitOps"."""
from fastapi import FastAPI

app = FastAPI(title="{{ titulo_servicio }}", description="{{ descripcion }}")


@app.get("/health")
def health() -> dict:
    """Endpoint de salud usado por las sondas y por la verificación local."""
    return {"status": "ok", "service": "{{ nombre_servicio }}"}


@app.get("/")
def root() -> dict:
    return {"service": "{{ nombre_servicio }}", "owner": "{{ owner }}", "system": "{{ sistema }}"}
