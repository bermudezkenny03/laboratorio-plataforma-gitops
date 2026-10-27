#!/usr/bin/env python3
"""Genera un servicio a partir de la plantilla "Servicio Backend GitOps".

Reemplaza las variables {{ variable }} del skeleton, aplica las validaciones de
plantilla-minima.md y escribe:
  - el repositorio de aplicación (README, catálogo, docs, código, k8s, CI)
  - la carpeta del servicio en el repositorio GitOps (manifiestos + Application de Argo CD)

Uso:
  python scripts/generar-servicio.py --valores plantilla-servicio-backend/valores-ejemplo.yaml \
      --salida-app repo-aplicacion --raiz-gitops . \
      --catalogo-grupos repo-aplicacion/catalog-grupos.yaml [--sobrescribir]
"""
import argparse
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla-servicio-backend"
CAMPOS = [
    "nombre_servicio", "titulo_servicio", "descripcion", "owner", "sistema",
    "organizacion", "ciclo_vida", "canal_soporte", "repositorio_gitops", "ruta_apps_gitops",
]
PATRON_VARIABLE = re.compile(r"\{\{\s*(" + "|".join(CAMPOS) + r")\s*\}\}")


def renderizar(texto: str, valores: dict) -> str:
    return PATRON_VARIABLE.sub(lambda m: str(valores[m.group(1)]), texto)


def owners_del_catalogo(ruta: Path) -> set:
    grupos = set()
    for doc in yaml.safe_load_all(ruta.read_text(encoding="utf-8")):
        if doc and doc.get("kind") == "Group":
            grupos.add("group:" + doc["metadata"]["name"])
    return grupos


def validar(valores: dict, raiz_gitops: Path, catalogo_grupos: Path | None, sobrescribir: bool) -> list:
    errores = []
    faltantes = [c for c in CAMPOS if not str(valores.get(c, "")).strip()]
    if faltantes:
        return [f"Faltan campos: {', '.join(faltantes)}"]

    nombre = valores["nombre_servicio"]
    if not re.fullmatch(r"[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?", nombre):
        errores.append("nombre_servicio debe usar minúsculas, números y guiones (máx. 63 caracteres)")
    destino_gitops = raiz_gitops / valores["ruta_apps_gitops"] / nombre
    if destino_gitops.exists() and not sobrescribir:
        errores.append(f"El servicio '{nombre}' ya existe en {destino_gitops} (use --sobrescribir para regenerarlo)")

    if catalogo_grupos is not None:
        if not catalogo_grupos.exists():
            errores.append(f"No existe el catálogo de grupos {catalogo_grupos}")
        elif valores["owner"] not in owners_del_catalogo(catalogo_grupos):
            errores.append(f"El owner {valores['owner']} no existe en {catalogo_grupos}")

    if len(valores["descripcion"]) < 20:
        errores.append("La descripción debe tener al menos 20 caracteres")

    url = urlparse(valores["repositorio_gitops"])
    if url.scheme not in ("https", "http") or not url.netloc or len(url.path.strip("/")) == 0:
        errores.append("repositorio_gitops debe ser una URL válida (https://host/organizacion/repositorio)")

    if valores["ciclo_vida"] not in ("experimental", "production"):
        errores.append("ciclo_vida debe ser experimental o production")
    return errores


def escribir(origen: Path, destino: Path, valores: dict, sobrescribir: bool, generados: list) -> None:
    if destino.exists() and not sobrescribir:
        print(f"  = {destino} (ya existe, se conserva)")
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(renderizar(origen.read_text(encoding="utf-8"), valores), encoding="utf-8")
    shutil.copymode(origen, destino)
    generados.append(destino)
    print(f"  + {destino}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--valores", required=True, type=Path)
    parser.add_argument("--salida-app", required=True, type=Path)
    parser.add_argument("--raiz-gitops", required=True, type=Path)
    parser.add_argument("--catalogo-grupos", type=Path)
    parser.add_argument("--sobrescribir", action="store_true")
    args = parser.parse_args()

    valores = yaml.safe_load(args.valores.read_text(encoding="utf-8"))
    errores = validar(valores, args.raiz_gitops, args.catalogo_grupos, args.sobrescribir)
    if errores:
        print("Validación fallida:")
        for e in errores:
            print(f"  - {e}")
        return 1

    generados = []
    print("Repositorio de aplicación:")
    skeleton = PLANTILLA / "skeleton"
    for origen in sorted(p for p in skeleton.rglob("*") if p.is_file()):
        escribir(origen, args.salida_app / origen.relative_to(skeleton), valores, args.sobrescribir, generados)

    print("Repositorio GitOps:")
    destino_gitops = args.raiz_gitops / valores["ruta_apps_gitops"] / valores["nombre_servicio"]
    for origen in sorted((skeleton / "k8s").glob("*.yaml")):
        escribir(origen, destino_gitops / origen.name, valores, args.sobrescribir, generados)
    origen_app = PLANTILLA / "gitops" / "argocd-application.yaml"
    escribir(origen_app, destino_gitops / origen_app.name, valores, args.sobrescribir, generados)

    for archivo in generados:
        if archivo.suffix in (".yaml", ".yml"):
            list(yaml.safe_load_all(archivo.read_text(encoding="utf-8")))
        if PATRON_VARIABLE.search(archivo.read_text(encoding="utf-8")):
            print(f"Quedaron variables sin reemplazar en {archivo}")
            return 1
    print(f"Listo: {len(generados)} archivos generados y validados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
