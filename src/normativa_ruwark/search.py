"""
search.py - Motor de búsqueda sobre la knowledge base de normativa arqueológica.

Índice en memoria con búsqueda por palabras clave, categoría y decreto supremo.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


_HERE = Path(__file__).resolve().parent
_ROOT_README = "README.md"


def _resolver_kb_dir() -> Path:
    """Resuelve la ubicación de la knowledge base empaquetada o externa."""
    if env_kb_dir := os.getenv("NORMATIVA_RUWARK_KB_DIR"):
        candidate = Path(env_kb_dir).expanduser().resolve()
        if candidate.exists():
            return candidate

    return _HERE / "knowledge_base"


KB_DIR = _resolver_kb_dir()


CATEGORIAS = {
    "normativa-general": "Normativa General (RIA, Ley 28296, TUPA, TUO)",
    "decretos-supremos": "Decretos Supremos del Ministerio de Cultura",
    "pmar": "Plan de Monitoreo Arqueológico (PMAR)",
    "pea": "Proyecto de Evaluación Arqueológica (PEA)",
    "das": "Diagnóstico Arqueológico de Superficie (DAS)",
    "otf": "Opinión Técnica Favorable (OTF)",
    "ciras": "Certificado de Inexistencia de Restos Arqueológicos (CIRAS)",
    "comun": "Documentación común (COARPE, TUPA pagos)",
    "complementaria": "Normativa complementaria",
}


@dataclass
class SearchResult:
    """Un resultado de búsqueda en la knowledge base."""

    archivo: str
    categoria: str
    titulo: str
    fragmento: str
    relevancia: float = 0.0


@dataclass
class KnowledgeIndex:
    """Índice completo de la knowledge base."""

    documentos: dict[str, str] = field(default_factory=dict)
    titulos: dict[str, str] = field(default_factory=dict)
    por_categoria: dict[str, list[str]] = field(default_factory=dict)

    @property
    def total_docs(self) -> int:
        return len(self.documentos)


def construir_indice(kb_dir: Path | None = None) -> KnowledgeIndex:
    """Lee todos los .md de la knowledge_base y construye un índice."""
    kb = kb_dir or KB_DIR
    idx = KnowledgeIndex()

    if not kb.exists():
        return idx

    for md_file in sorted(kb.rglob("*.md")):
        rel = md_file.relative_to(kb).as_posix()
        if rel == _ROOT_README:
            continue

        contenido = md_file.read_text(encoding="utf-8", errors="replace")
        idx.documentos[rel] = contenido

        for linea in contenido.splitlines():
            if linea.strip().startswith("#"):
                idx.titulos[rel] = linea.strip().lstrip("#").strip()
                break
        else:
            idx.titulos[rel] = rel

        cat = rel.split("/")[0] if "/" in rel else "raiz"
        idx.por_categoria.setdefault(cat, []).append(rel)

    return idx


def buscar(
    indice: KnowledgeIndex,
    consulta: str,
    categoria: str | None = None,
    max_resultados: int = 10,
) -> list[SearchResult]:
    """Búsqueda por palabras clave en la knowledge base."""
    palabras = [p.lower() for p in re.split(r"\s+", consulta.strip()) if len(p) >= 2]
    if not palabras:
        return []

    resultados: list[SearchResult] = []

    for ruta, contenido in indice.documentos.items():
        cat = ruta.split("/")[0] if "/" in ruta else "raiz"
        if categoria and cat != categoria:
            continue

        contenido_lower = contenido.lower()
        score = 0.0
        for palabra in palabras:
            count = contenido_lower.count(palabra)
            if count > 0:
                score += 1.0 + min(count / 10.0, 5.0)

        if score <= 0:
            continue

        resultados.append(
            SearchResult(
                archivo=ruta,
                categoria=CATEGORIAS.get(cat, cat),
                titulo=indice.titulos.get(ruta, ruta),
                fragmento=_extraer_fragmento(contenido, palabras),
                relevancia=score,
            )
        )

    resultados.sort(key=lambda r: r.relevancia, reverse=True)
    return resultados[:max_resultados]


def buscar_decreto_supremo(
    indice: KnowledgeIndex,
    anio: str | None = None,
    numero: str | None = None,
    texto: str | None = None,
) -> list[SearchResult]:
    """Busca decretos supremos por año, número o texto libre."""
    resultados: list[SearchResult] = []
    ds_docs = {r: c for r, c in indice.documentos.items() if r.startswith("decretos-supremos/")}

    for ruta, contenido in ds_docs.items():
        partes = ruta.split("/")
        if anio and len(partes) >= 2 and partes[1] != anio:
            continue

        if numero:
            num_pattern = numero.replace("-", r"[\-\s]*")
            if not re.search(num_pattern, ruta, re.IGNORECASE):
                continue

        score = 1.0
        palabras = []
        if texto:
            palabras = [p.lower() for p in re.split(r"\s+", texto) if len(p) >= 2]
            contenido_lower = contenido.lower()
            for palabra in palabras:
                count = contenido_lower.count(palabra)
                if count > 0:
                    score += 1.0 + min(count / 10.0, 5.0)
                else:
                    score -= 0.5

        if score <= 0:
            continue

        cat = partes[1] if len(partes) >= 2 else "desconocido"
        resultados.append(
            SearchResult(
                archivo=ruta,
                categoria=f"Decreto Supremo - {cat}",
                titulo=indice.titulos.get(ruta, ruta),
                fragmento=_extraer_fragmento(contenido, palabras),
                relevancia=score,
            )
        )

    resultados.sort(key=lambda r: r.relevancia, reverse=True)
    return resultados


def obtener_documento(indice: KnowledgeIndex, ruta: str) -> str | None:
    """Obtiene el contenido completo de un documento por su ruta relativa."""
    return indice.documentos.get(ruta)


def listar_categoria(indice: KnowledgeIndex, categoria: str) -> list[dict[str, str]]:
    """Lista todos los documentos de una categoría."""
    docs = indice.por_categoria.get(categoria, [])
    return [{"archivo": d, "titulo": indice.titulos.get(d, d)} for d in sorted(docs)]


def _extraer_fragmento(contenido: str, palabras: list[str], largo: int = 500) -> str:
    """Extrae el fragmento más relevante del contenido."""
    if not palabras:
        lineas = [linea for linea in contenido.splitlines() if linea.strip()]
        return "\n".join(lineas[:8])[:largo]

    contenido_lower = contenido.lower()
    mejor_pos = 0
    mejor_score = 0

    for i in range(0, len(contenido_lower), 100):
        ventana = contenido_lower[i:i + largo]
        score = sum(ventana.count(palabra) for palabra in palabras)
        if score > mejor_score:
            mejor_score = score
            mejor_pos = i

    fragmento = contenido[mejor_pos:mejor_pos + largo]
    inicio_linea = fragmento.rfind("\n", 0, 50)
    if inicio_linea > 0:
        fragmento = fragmento[inicio_linea + 1:]

    return fragmento.strip()
