#!/usr/bin/env python3
"""Valida las entidades del catálogo con los JSON Schema oficiales de Backstage.

Además comprueba que las referencias (owner, system) apunten a entidades que existen
en los archivos validados.

Obtener los esquemas (una sola vez):
  git clone --depth 1 --filter=blob:none --sparse https://github.com/backstage/backstage.git /tmp/backstage
  git -C /tmp/backstage sparse-checkout set packages/catalog-model/src/schema

Uso:
  python scripts/validar-catalogo-backstage.py /tmp/backstage/packages/catalog-model/src/schema \
      repo-aplicacion/catalog-info.yaml repo-aplicacion/catalog-grupos.yaml \
      repo-aplicacion/catalog-sistema.yaml repo-aplicacion/catalog-location.yaml
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

KIND_A_ESQUEMA = {
    "Component": "ComponentV1alpha1",
    "Group": "GroupV1alpha1",
    "System": "SystemV1alpha1",
    "Location": "LocationV1alpha1",
    "API": "ApiV1alpha1",
    "Resource": "ResourceV1alpha1",
    "Domain": "DomainV1alpha1",
    "User": "UserV1alpha1",
}


def cargar_registro(dir_esquemas: Path):
    esquemas = {}
    for archivo in dir_esquemas.rglob("*.schema.json"):
        contenido = json.loads(archivo.read_text(encoding="utf-8"))
        if "$id" in contenido:
            esquemas[contenido["$id"]] = contenido
    registro = Registry().with_resources(
        (sid, Resource.from_contents(c, default_specification=DRAFT7)) for sid, c in esquemas.items()
    )
    return esquemas, registro


def ref(valor: str, kind_por_defecto: str) -> str:
    """Normaliza una referencia de entidad a kind:namespace/nombre."""
    kind, _, resto = valor.rpartition(":") if ":" in valor else (kind_por_defecto, "", valor)
    ns, _, nombre = resto.rpartition("/") if "/" in resto else ("default", "", resto)
    return f"{kind.lower()}:{ns}/{nombre}"


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    esquemas, registro = cargar_registro(Path(sys.argv[1]))
    entidades, errores = [], 0
    for ruta in sys.argv[2:]:
        for doc in yaml.safe_load_all(Path(ruta).read_text(encoding="utf-8")):
            if not doc:
                continue
            kind = doc.get("kind")
            esquema = esquemas.get(KIND_A_ESQUEMA.get(kind, ""))
            if esquema is None:
                print(f"[ERROR] {ruta}: kind {kind!r} no reconocido")
                errores += 1
                continue
            fallos = sorted(Draft7Validator(esquema, registry=registro).iter_errors(doc), key=str)
            nombre = doc.get("metadata", {}).get("name")
            if fallos:
                errores += len(fallos)
                for f in fallos:
                    print(f"[ERROR] {ruta} ({kind} {nombre}): {'/'.join(map(str, f.path))} -> {f.message}")
            else:
                print(f"[OK]    {ruta}: {kind} {nombre} cumple el esquema {esquema['$id']}")
            entidades.append(doc)

    existentes = {f"{e['kind'].lower()}:{e['metadata'].get('namespace', 'default')}/{e['metadata']['name']}" for e in entidades}
    for e in entidades:
        spec, nombre = e.get("spec", {}), e["metadata"]["name"]
        for campo, kind_defecto in (("owner", "group"), ("system", "system")):
            if campo in spec:
                destino = ref(spec[campo], kind_defecto)
                if destino in existentes:
                    print(f"[OK]    {e['kind']} {nombre}: {campo} -> {destino} existe")
                else:
                    print(f"[ERROR] {e['kind']} {nombre}: {campo} -> {destino} no existe en los archivos validados")
                    errores += 1
    print(f"\nResultado: {'VÁLIDO' if errores == 0 else f'{errores} error(es)'}")
    return 0 if errores == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
