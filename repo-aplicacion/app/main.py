"""Código base de gestion-acueductos-api generado por la plantilla "Servicio Backend GitOps"."""
from fastapi import FastAPI

app = FastAPI(title="API de Gestión de Acueductos", description="Servicio que consulta y registra información sobre cobertura, consumo y estado de acueductos veredales.")


@app.get("/health")
def health() -> dict:
    """Endpoint de salud usado por las sondas y por la verificación local."""
    return {"status": "ok", "service": "gestion-acueductos-api"}


@app.get("/")
def root() -> dict:
    return {"service": "gestion-acueductos-api", "owner": "group:equipo-datos-agua", "system": "plataforma-gestion-agua"}
