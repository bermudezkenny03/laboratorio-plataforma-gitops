#!/usr/bin/env python3
"""RAG del laboratorio con un LLM local (Ollama).

1. Construye fuentes/contexto-rag.txt con las 5 fuentes del inventario.
2. Verifica que la respuesta esperada de cada pregunta esté en las fuentes citadas (trazabilidad).
3. Consulta a Ollama con el contexto y guarda las respuestas en evidencias/rag-respuestas-ollama.md.

Uso (desde la raíz del repositorio):
  python scripts/rag-consulta.py --solo-contexto       # paso 8.4
  python scripts/rag-consulta.py --verificar-fuentes   # comprueba trazabilidad sin LLM
  python scripts/rag-consulta.py                       # paso 8.5 completo (requiere `ollama serve` y `ollama pull llama3.2`)

Opciones: --modelo llama3.2  --url http://localhost:11434
Solo usa la biblioteca estándar de Python.
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = [
    "fuentes/catalog-info.yaml",
    "fuentes/catalog-grupos.yaml",
    "fuentes/catalog-sistema.yaml",
    "fuentes/index.md",
    "fuentes/golden-path.md",
]
SIN_RESPUESTA = "No encuentro esta información en las fuentes proporcionadas."

PREGUNTAS = [
    {
        "pregunta": "¿Quién es el equipo propietario de la API de Gestión de Acueductos y cómo se solicita soporte?",
        "esperada": "El equipo propietario es equipo-datos-agua. El soporte se solicita en #soporte-datos-agua "
                    "o al correo datos-agua@ejemplo.com.",
        "fuentes": ["fuentes/index.md", "fuentes/catalog-grupos.yaml"],
        "claves": ["equipo-datos-agua", "#soporte-datos-agua", "datos-agua@ejemplo.com"],
    },
    {
        "pregunta": "¿Cómo se despliega el servicio y qué herramienta sincroniza los cambios?",
        "esperada": "El servicio se despliega mediante GitOps. Se modifica el repositorio GitOps y Argo CD "
                    "sincroniza automáticamente los manifiestos hacia Kubernetes.",
        "fuentes": ["fuentes/index.md", "fuentes/golden-path.md"],
        "claves": ["GitOps", "Argo CD", "repositorio GitOps"],
    },
    {
        "pregunta": "¿Qué debe verificar la desarrolladora después de que Argo CD sincronice?",
        "esperada": "Debe verificar que la aplicación esté Synced y Healthy, y que los pods estén en estado Running.",
        "fuentes": ["fuentes/index.md", "fuentes/golden-path.md"],
        "claves": ["Synced", "Healthy", "Running"],
    },
    {
        "pregunta": "¿Cuál es la dirección IP pública del servicio en producción?",
        "esperada": SIN_RESPUESTA,
        "fuentes": [],
        "claves": [],
        "control": True,
    },
]


def construir_contexto() -> str:
    partes = []
    for ruta in FUENTES:
        texto = (RAIZ / ruta).read_text(encoding="utf-8").strip()
        partes.append(f"### FUENTE: {Path(ruta).name}\n{texto}\n")
    contexto = "\n".join(partes)
    (RAIZ / "fuentes" / "contexto-rag.txt").write_text(contexto, encoding="utf-8")
    return contexto


def verificar_fuentes() -> bool:
    todo_ok = True
    for i, p in enumerate(PREGUNTAS, 1):
        print(f"Pregunta {i}: {p['pregunta']}")
        if p.get("control"):
            contexto = (RAIZ / "fuentes" / "contexto-rag.txt").read_text(encoding="utf-8").lower()
            hay_ip = any(t in contexto for t in ("ip pública", "ip publica", "dirección ip"))
            print(f"  [{'OK' if not hay_ip else 'FALLA'}] pregunta de control: las fuentes no contienen una IP pública"
                  f" -> la respuesta correcta es \"{SIN_RESPUESTA}\"")
            todo_ok &= not hay_ip
            continue
        texto = "\n".join((RAIZ / f).read_text(encoding="utf-8") for f in p["fuentes"])
        for clave in p["claves"]:
            ok = clave in texto
            todo_ok &= ok
            donde = [f for f in p["fuentes"] if clave in (RAIZ / f).read_text(encoding="utf-8")]
            print(f"  [{'OK' if ok else 'FALLA'}] '{clave}' aparece en: {', '.join(donde) or 'ninguna fuente'}")
    return todo_ok


def preguntar(url: str, modelo: str, contexto: str, pregunta: str) -> str:
    prompt = (
        "Responde únicamente con la información del siguiente contexto. "
        f"Si no encuentras la respuesta, di exactamente: \"{SIN_RESPUESTA}\". "
        "Al final indica entre paréntesis el nombre del archivo fuente que usaste.\n\n"
        f"Contexto:\n{contexto}\n\nPregunta:\n{pregunta}"
    )
    cuerpo = json.dumps({"model": modelo, "prompt": prompt, "stream": False,
                         "options": {"temperature": 0}}).encode("utf-8")
    req = urllib.request.Request(f"{url}/api/generate", data=cuerpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read())["response"].strip()


def evaluar_automatico(p: dict, respuesta: str) -> str:
    if p.get("control"):
        return "Correcta (no inventó datos)" if "no encuentro" in respuesta.lower() else "Incorrecta (inventó un dato)"
    faltan = [c for c in p["claves"] if c.lower() not in respuesta.lower()]
    return "Correcta" if not faltan else f"Parcial: faltan {', '.join(faltan)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", default="llama3.2")
    ap.add_argument("--url", default="http://localhost:11434")
    ap.add_argument("--solo-contexto", action="store_true")
    ap.add_argument("--verificar-fuentes", action="store_true")
    args = ap.parse_args()

    contexto = construir_contexto()
    print(f"Contexto generado: fuentes/contexto-rag.txt ({len(contexto)} caracteres, {len(FUENTES)} fuentes)")
    if args.solo_contexto:
        return 0
    if args.verificar_fuentes:
        return 0 if verificar_fuentes() else 1

    filas = []
    for i, p in enumerate(PREGUNTAS, 1):
        print(f"Consultando pregunta {i} a {args.modelo}...")
        try:
            r = preguntar(args.url, args.modelo, contexto, p["pregunta"])
        except urllib.error.URLError as e:
            print(f"No se pudo conectar con Ollama en {args.url}: {e}. ¿Está corriendo `ollama serve`?")
            return 1
        filas.append((i, p, r, evaluar_automatico(p, r)))

    salida = RAIZ / "evidencias" / "rag-respuestas-ollama.md"
    lineas = [f"# Respuestas del LLM local ({args.modelo})", "",
              f"Generado el {datetime.datetime.now():%Y-%m-%d %H:%M} con `python scripts/rag-consulta.py`.", ""]
    for i, p, r, ev in filas:
        lineas += [f"## Pregunta {i}", "", p["pregunta"], "", "**Respuesta del modelo:**", "", r, "",
                   f"**Respuesta esperada:** {p['esperada']}", "",
                   f"**Fuente:** {', '.join(p['fuentes']) or 'ninguna (pregunta de control)'}", "",
                   f"**Evaluación automática:** {ev}", ""]
    salida.write_text("\n".join(lineas), encoding="utf-8")
    correctas = sum(1 for *_, ev in filas if ev.startswith("Correcta"))
    print(f"Respuestas guardadas en {salida.relative_to(RAIZ)} — correctas: {correctas}/{len(filas)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
