#!/usr/bin/env python3
"""
server.py — MCP Server: Normativa Arqueológica del Perú | RUWARK S.A.C.

Versión: Marzo 2026
Servidor MCP que expone herramientas de consulta sobre la normativa
arqueológica peruana (RIA, Ley 28296, PMAR, PEA, CIRAS, DAS, OTF, DS).

Uso:
    # Ejecución directa
    python -m normativa_ruwark.server

    # Como paquete instalado
    normativa-ruwark

    # Con MCP Inspector
    mcp dev src/normativa_ruwark/server.py
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import __version__
from .search import (
    CATEGORIAS,
    KnowledgeIndex,
    construir_indice,
    buscar,
    buscar_decreto_supremo,
    obtener_documento,
    listar_categoria,
)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("normativa-ruwark")

# ── Servidor MCP ────────────────────────────────────────────────────────────
mcp = FastMCP(
    "Normativa Arqueológica RUWARK",
    instructions=(
        "MCP Server — Normativa Arqueológica del Perú | RUWARK S.A.C. "
        f"Versión {__version__}. "
        "Consulta el RIA, Ley 28296, PMAR, PEA, CIRAS, DAS, OTF, "
        "Decretos Supremos y normativa complementaria. Marzo 2026."
    ),
)

# ── Índice global ───────────────────────────────────────────────────────────
_indice: KnowledgeIndex | None = None


def _get_indice() -> KnowledgeIndex:
    global _indice
    if _indice is None:
        logger.info("Construyendo índice de knowledge base...")
        _indice = construir_indice()
        logger.info(f"Índice construido: {_indice.total_docs} documentos")
    return _indice


# ═══════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS (TOOLS)
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
def buscar_normativa(consulta: str, categoria: str | None = None,
                     max_resultados: int = 10) -> str:
    """Busca en toda la normativa arqueológica peruana por palabras clave.

    Args:
        consulta: Texto de búsqueda (ej: "monitoreo arqueológico", "hallazgo fortuito",
                  "CIRAS requisitos", "habilitación COARPE")
        categoria: Filtrar por categoría. Opciones:
                   normativa-general, decretos-supremos, pmar, pea, das, otf,
                   ciras, comun, complementaria
        max_resultados: Número máximo de resultados (default: 10)

    Returns:
        Resultados de búsqueda con archivo, título y fragmento relevante.
    """
    idx = _get_indice()
    resultados = buscar(idx, consulta, categoria, max_resultados)

    if not resultados:
        return f"No se encontraron resultados para: '{consulta}'"

    salida = [f"📋 {len(resultados)} resultado(s) para: '{consulta}'\n"]
    for i, r in enumerate(resultados, 1):
        salida.append(
            f"─── Resultado {i} ───\n"
            f"📄 Archivo: {r.archivo}\n"
            f"📁 Categoría: {r.categoria}\n"
            f"📝 Título: {r.titulo}\n"
            f"🔍 Relevancia: {r.relevancia:.1f}\n"
            f"───\n{r.fragmento}\n"
        )
    return "\n".join(salida)


@mcp.tool()
def consultar_procedimiento(procedimiento: str) -> str:
    """Consulta la información completa de un procedimiento arqueológico.

    Args:
        procedimiento: Tipo de procedimiento. Opciones:
                       pmar - Plan de Monitoreo Arqueológico
                       pea  - Proyecto de Evaluación Arqueológica
                       das  - Diagnóstico Arqueológico de Superficie
                       otf  - Opinión Técnica Favorable
                       ciras - Certificado de Inexistencia de Restos Arqueológicos

    Returns:
        Información del flujo, requisitos y documentación del procedimiento.
    """
    idx = _get_indice()
    proc = procedimiento.lower().strip()

    # Mapeo de procedimientos a archivos
    mapeo: dict[str, list[str]] = {
        "pmar": ["pmar/flujo-pmar.md", "pmar/requisitos-pmar.md"],
        "pea": ["pea/flujo-pea.md", "pea/formatos-pea-pra.md"],
        "das": ["das/flujo-das.md"],
        "otf": ["otf/flujo-otf.md"],
        "ciras": ["ciras/flujo-ciras.md", "ciras/guia-expedicion-ciras.md"],
    }

    archivos = mapeo.get(proc)
    if not archivos:
        opciones = ", ".join(mapeo.keys())
        return f"Procedimiento '{proc}' no reconocido. Opciones: {opciones}"

    partes = [f"📋 PROCEDIMIENTO: {proc.upper()}\n{'═' * 50}\n"]
    for archivo in archivos:
        contenido = obtener_documento(idx, archivo)
        if contenido:
            partes.append(f"\n📄 {archivo}\n{'─' * 40}\n{contenido}\n")
        else:
            partes.append(f"\n⚠️ Archivo no encontrado: {archivo}\n")

    return "\n".join(partes)


@mcp.tool()
def obtener_checklist(procedimiento: str) -> str:
    """Obtiene el checklist de documentos requeridos para un procedimiento.

    Args:
        procedimiento: pmar, pea, das, otf, ciras

    Returns:
        Lista de documentos requeridos organizados por sección.
    """
    checklists: dict[str, dict[str, list[str]]] = {
        "pmar": {
            "Documentos Administrativos": [
                "Formulario P01DGPA",
                "Comprobante de pago TUPA",
                "Carta de financiamiento (DJ titular)",
                "Carta poder simple",
                "Acreditación de titularidad",
            ],
            "Documentos Legales": [
                "DJ habilitación Director (COARPE)",
                "DJ habilitación Residente (COARPE)",
                "Carta consentimiento expreso residente",
                "Cartas compromiso no afectación",
            ],
            "Documentos Técnicos": [
                "Plan de Monitoreo Arqueológico",
                "Información técnica del proyecto",
                "Antecedentes arqueológicos",
                "Descripción del proyecto de obra",
                "Metodología de monitoreo",
                "Planos (ubicación, delimitación)",
            ],
        },
        "pea": {
            "Documentos Administrativos": [
                "Formulario P01DGPA",
                "Comprobante de pago TUPA",
                "Carta de financiamiento",
                "Carta poder simple",
            ],
            "Documentos Legales": [
                "DJ habilitación Director (COARPE)",
                "DJ habilitación miembros del equipo",
                "Cartas compromiso de no afectación",
            ],
            "Documentos Técnicos": [
                "Proyecto de Evaluación Arqueológica",
                "Antecedentes arqueológicos del área",
                "Metodología de evaluación",
                "Plan de trabajo y cronograma",
                "Planos (ubicación, delimitación, cuadrículas)",
            ],
        },
        "das": {
            "Documentos Administrativos": [
                "Formulario correspondiente",
                "Comprobante de pago TUPA",
            ],
            "Documentos Técnicos": [
                "Informe de Diagnóstico Arqueológico de Superficie",
                "Planos del área evaluada",
                "Registro fotográfico",
            ],
        },
        "otf": {
            "Documentos Administrativos": [
                "Solicitud de OTF",
                "Comprobante de pago TUPA",
            ],
            "Documentos Técnicos": [
                "Informe técnico del proyecto",
                "Estudio de impacto arqueológico",
                "Planos de ubicación",
            ],
        },
        "ciras": {
            "Documentos Administrativos": [
                "Formulario de solicitud CIRAS",
                "Comprobante de pago TUPA",
                "Carta poder simple (si aplica)",
            ],
            "Documentos Legales": [
                "DJ habilitación del arqueólogo (COARPE)",
                "Acreditación de titularidad del terreno",
            ],
            "Documentos Técnicos": [
                "Informe arqueológico de campo",
                "Registro fotográfico",
                "Plano de ubicación georreferenciado",
                "Plano de delimitación del área",
                "Coordenadas UTM WGS84",
            ],
        },
    }

    proc = procedimiento.lower().strip()
    checklist = checklists.get(proc)
    if not checklist:
        return f"Procedimiento '{proc}' no reconocido. Opciones: {', '.join(checklists.keys())}"

    partes = [f"📋 CHECKLIST — {proc.upper()}\n{'═' * 50}\n"]
    for seccion, items in checklist.items():
        partes.append(f"\n🔹 {seccion}:")
        for item in items:
            partes.append(f"   ☐ {item}")

    partes.append(f"\n{'─' * 50}")
    partes.append("Nota: Consulte el TUPA vigente para montos actualizados.")
    return "\n".join(partes)


@mcp.tool()
def consultar_decreto_supremo(anio: str | None = None, numero: str | None = None,
                              texto: str | None = None) -> str:
    """Busca decretos supremos del Ministerio de Cultura por año, número o contenido.

    Args:
        anio: Año del decreto (ej: "2025", "2024", "2022")
        numero: Número del decreto (ej: "004", "011")
        texto: Búsqueda por contenido (ej: "patrimonio cultural", "modificatoria RIA")

    Returns:
        Lista de decretos supremos encontrados con extractos.
    """
    idx = _get_indice()
    resultados = buscar_decreto_supremo(idx, anio, numero, texto)

    if not resultados:
        filtros = []
        if anio:
            filtros.append(f"año={anio}")
        if numero:
            filtros.append(f"número={numero}")
        if texto:
            filtros.append(f"texto='{texto}'")
        return f"No se encontraron decretos supremos con: {', '.join(filtros) or 'sin filtros'}"

    partes = [f"📜 {len(resultados)} decreto(s) supremo(s) encontrado(s)\n"]
    for i, r in enumerate(resultados, 1):
        partes.append(
            f"─── DS {i} ───\n"
            f"📄 {r.archivo}\n"
            f"📝 {r.titulo}\n"
            f"📁 {r.categoria}\n"
            f"───\n{r.fragmento[:400]}\n"
        )
    return "\n".join(partes)


@mcp.tool()
def leer_documento(ruta: str) -> str:
    """Lee el contenido completo de un documento de la knowledge base.

    Args:
        ruta: Ruta relativa del documento (ej: "normativa-general/ria-ds-011-2022-mc.md",
              "pmar/flujo-pmar.md", "ciras/guia-expedicion-ciras.md")

    Returns:
        Contenido completo del documento en Markdown.
    """
    idx = _get_indice()
    contenido = obtener_documento(idx, ruta)
    if contenido is None:
        # Sugerir documentos similares
        sugerencias = [r for r in idx.documentos if ruta.split("/")[-1].split(".")[0] in r]
        msg = f"Documento no encontrado: '{ruta}'"
        if sugerencias:
            msg += f"\n\n¿Quizás quisiste decir?\n" + "\n".join(f"  • {s}" for s in sugerencias[:5])
        return msg
    return contenido


@mcp.tool()
def listar_normativas(categoria: str | None = None) -> str:
    """Lista todas las normativas disponibles, opcionalmente filtradas por categoría.

    Args:
        categoria: Filtrar por categoría. Opciones:
                   normativa-general, decretos-supremos, pmar, pea, das, otf,
                   ciras, comun, complementaria
                   (dejar vacío para listar todas las categorías)

    Returns:
        Lista organizada de normativas disponibles.
    """
    idx = _get_indice()

    if not categoria:
        # Listar todas las categorías con conteos
        partes = [f"📚 KNOWLEDGE BASE — Normativa Arqueológica del Perú\n"
                  f"   Total: {idx.total_docs} documentos\n{'═' * 55}\n"]
        for cat, desc in CATEGORIAS.items():
            docs = idx.por_categoria.get(cat, [])
            count = len(docs)
            if cat == "decretos-supremos":
                # Desglosar por año
                anios: dict[str, int] = {}
                for d in docs:
                    partes_ruta = d.split("/")
                    if len(partes_ruta) >= 2:
                        a = partes_ruta[1]
                        anios[a] = anios.get(a, 0) + 1
                detalle = ", ".join(f"{a}: {n}" for a, n in sorted(anios.items()))
                partes.append(f"\n📁 {cat}/ — {desc}\n   📊 {count} documentos ({detalle})")
            else:
                partes.append(f"\n📁 {cat}/ — {desc}\n   📊 {count} documento(s)")
        return "\n".join(partes)

    # Listar documentos de una categoría específica
    docs = listar_categoria(idx, categoria)
    if not docs:
        return f"Categoría '{categoria}' no encontrada o vacía.\nCategorías disponibles: {', '.join(CATEGORIAS.keys())}"

    desc = CATEGORIAS.get(categoria, categoria)
    partes = [f"📁 {categoria}/ — {desc}\n   {len(docs)} documento(s)\n{'─' * 50}\n"]
    for d in docs:
        partes.append(f"  📄 {d['archivo']}\n     {d['titulo']}\n")
    return "\n".join(partes)


@mcp.tool()
def consultar_ria(articulo: str | None = None, tema: str | None = None) -> str:
    """Consulta el Reglamento de Intervenciones Arqueológicas (RIA) D.S. 011-2022-MC.

    Args:
        articulo: Número de artículo a consultar (ej: "27", "28", "32")
        tema: Tema a buscar en el RIA (ej: "monitoreo", "hallazgo", "CIRAS")

    Returns:
        Artículo(s) o secciones relevantes del RIA.
    """
    idx = _get_indice()

    # Cargar el RIA principal y su modificatoria
    ria_docs = [
        "normativa-general/ria-ds-011-2022-mc.md",
        "normativa-general/ria-modificatoria-ds-004-2025-mc.md",
        "normativa-general/ria-2025-consolidado.md",
    ]

    contenido_ria = ""
    for doc in ria_docs:
        c = obtener_documento(idx, doc)
        if c:
            contenido_ria += f"\n\n{'═' * 50}\n📄 {doc}\n{'═' * 50}\n\n{c}"

    if not contenido_ria:
        return "No se encontró el RIA en la knowledge base."

    if articulo:
        # Buscar artículo específico
        patrones = [
            rf"(?i)(Art[íi]culo\s+{articulo}[\.\s\-–—].*?)(?=Art[íi]culo\s+\d|$)",
            rf"(?i)(Art\.\s*{articulo}[\.\s\-–—].*?)(?=Art\.\s*\d|$)",
        ]
        fragmentos = []
        for patron in patrones:
            matches = re.findall(patron, contenido_ria, re.DOTALL)
            for m in matches:
                texto = m.strip()[:2000]
                if texto and texto not in fragmentos:
                    fragmentos.append(texto)

        if fragmentos:
            partes = [f"📜 RIA — Artículo {articulo}\n{'═' * 50}\n"]
            for f in fragmentos:
                partes.append(f"{f}\n{'─' * 40}\n")
            return "\n".join(partes)
        return f"No se encontró el Artículo {articulo} en el RIA."

    if tema:
        # Buscar por tema
        resultados = buscar(idx, tema, "normativa-general", 5)
        if not resultados:
            return f"No se encontró '{tema}' en la normativa general."

        partes = [f"📜 RIA — Búsqueda: '{tema}'\n{'═' * 50}\n"]
        for r in resultados:
            partes.append(f"📄 {r.archivo}\n{r.fragmento}\n{'─' * 40}\n")
        return "\n".join(partes)

    return "Especifica un artículo (ej: articulo='27') o un tema (ej: tema='monitoreo')."


@mcp.tool()
def referencias_cruzadas(norma: str) -> str:
    """Obtiene las referencias cruzadas de una norma dentro del sistema normativo.

    Args:
        norma: Nombre o identificador de la norma (ej: "RIA", "Ley 28296",
               "PMAR", "DS 004-2025")

    Returns:
        Mapa de referencias cruzadas de la norma solicitada.
    """
    refs = {
        "ria": {
            "norma": "RIA — D.S. N° 011-2022-MC",
            "base_legal": ["Ley N° 28296 — Patrimonio Cultural de la Nación"],
            "modificatorias": [
                "D.S. N° 004-2025-MC — Modificatoria del RIA",
            ],
            "reglamentos_relacionados": [
                "D.S. N° 011-2006-ED — Reglamento Ley 28296",
                "D.S. N° 007-2020-MC — Modificatoria del Reglamento",
            ],
            "procedimientos": {
                "PMAR": "Arts. 27-29 del RIA",
                "PEA": "Arts. 23-24 del RIA → formatos-pea-pra.md",
                "CIRAS": "Arts. 32-35 del RIA → guia-expedicion-ciras.md",
                "DAS": "Procedimiento de diagnóstico superficial",
                "OTF": "Opinión técnica favorable previa",
            },
            "documentos_kb": [
                "normativa-general/ria-ds-011-2022-mc.md",
                "normativa-general/ria-modificatoria-ds-004-2025-mc.md",
                "normativa-general/ria-2025-consolidado.md",
            ],
        },
        "ley 28296": {
            "norma": "Ley N° 28296 — Ley General del Patrimonio Cultural de la Nación",
            "reglamento": "D.S. N° 011-2006-ED",
            "modificatorias": [
                "D.S. N° 007-2020-MC — Modificatoria del Reglamento",
            ],
            "normas_derivadas": [
                "RIA — D.S. N° 011-2022-MC",
                "TUPA 2025 — Ministerio de Cultura",
            ],
            "documentos_kb": [
                "normativa-general/ley-28296-patrimonio-cultural.md",
                "complementaria/reglamento-ley-28296-ds-011-2006-ed.md",
                "normativa-general/reglamento-ley-28296-modificatoria-2020.md",
            ],
        },
        "pmar": {
            "norma": "Plan de Monitoreo Arqueológico (PMAR)",
            "base_legal": [
                "Arts. 27-29 del RIA (D.S. N° 011-2022-MC)",
                "D.S. N° 004-2025-MC — Modificatoria",
            ],
            "requisitos": [
                "Habilitación COARPE del Director y Residente",
                "TUPA — Procedimiento y tasas",
            ],
            "documentos_kb": [
                "pmar/flujo-pmar.md",
                "pmar/requisitos-pmar.md",
                "comun/coarpe-habilitacion.md",
                "comun/tupa-pagos.md",
            ],
        },
        "pea": {
            "norma": "Proyecto de Evaluación Arqueológica (PEA)",
            "base_legal": ["Arts. 23-24 del RIA (D.S. N° 011-2022-MC)"],
            "documentos_kb": [
                "pea/flujo-pea.md",
                "pea/formatos-pea-pra.md",
            ],
        },
        "ciras": {
            "norma": "Certificado de Inexistencia de Restos Arqueológicos (CIRAS)",
            "base_legal": [
                "Arts. 32-35 del RIA (D.S. N° 011-2022-MC)",
                "R.M. N° 000439-2024-MC — Guía CIRAS",
            ],
            "documentos_kb": [
                "ciras/flujo-ciras.md",
                "ciras/guia-expedicion-ciras.md",
            ],
        },
    }

    norma_key = norma.lower().strip()
    # Buscar coincidencia parcial
    ref = refs.get(norma_key)
    if not ref:
        for key, val in refs.items():
            if norma_key in key or key in norma_key:
                ref = val
                break

    if not ref:
        return (f"No se encontraron referencias cruzadas para '{norma}'.\n"
                f"Opciones: {', '.join(refs.keys())}")

    return json.dumps(ref, ensure_ascii=False, indent=2)


@mcp.tool()
def info_servidor() -> str:
    """Muestra información del servidor MCP y estadísticas de la knowledge base."""
    idx = _get_indice()

    categorias_info = []
    for cat, desc in CATEGORIAS.items():
        count = len(idx.por_categoria.get(cat, []))
        categorias_info.append(f"  📁 {cat}: {count} doc(s) — {desc}")

    return (
        f"🏛️ MCP Server — Normativa Arqueológica RUWARK\n"
        f"{'═' * 55}\n"
        f"📌 Versión: {__version__}\n"
        f"📅 Edición: Marzo 2026\n"
        f"🏢 Organización: RUWARK S.A.C.\n"
        f"📊 Total documentos: {idx.total_docs}\n\n"
        f"📚 Categorías:\n" + "\n".join(categorias_info) + "\n\n"
        f"🔧 Herramientas disponibles:\n"
        f"  • buscar_normativa — Búsqueda por palabras clave\n"
        f"  • consultar_procedimiento — Flujos PMAR/PEA/DAS/OTF/CIRAS\n"
        f"  • obtener_checklist — Checklists de documentos\n"
        f"  • consultar_decreto_supremo — Decretos Supremos por año/número\n"
        f"  • leer_documento — Lectura completa de documentos\n"
        f"  • listar_normativas — Catálogo de normativas\n"
        f"  • consultar_ria — Artículos del RIA\n"
        f"  • referencias_cruzadas — Mapa de referencias normativas\n"
    )


# ═══════════════════════════════════════════════════════════════════════════
# RECURSOS (RESOURCES)
# ═══════════════════════════════════════════════════════════════════════════


@mcp.resource("normativa://indice")
def recurso_indice() -> str:
    """Índice completo de la knowledge base de normativa arqueológica."""
    return listar_normativas()


@mcp.resource("normativa://categorias")
def recurso_categorias() -> str:
    """Categorías disponibles en la knowledge base."""
    return json.dumps(CATEGORIAS, ensure_ascii=False, indent=2)


@mcp.resource("normativa://referencias")
def recurso_referencias() -> str:
    """Mapa de referencias cruzadas del sistema normativo arqueológico."""
    refs = {
        "RIA (D.S. 011-2022-MC)": {
            "PMAR": "Arts. 27–29",
            "PEA": "Arts. 23–24",
            "CIRAS": "Arts. 32–35",
            "Modificatoria": "D.S. 004-2025-MC",
            "Base legal": "Ley 28296",
        },
        "Ley 28296": {
            "Reglamento": "D.S. 011-2006-ED",
            "Modificatoria": "D.S. 007-2020-MC",
        },
        "TUPA 2025": "Procedimientos y tasas vigentes",
        "TUO Ley 27444": "Procedimiento administrativo general",
    }
    return json.dumps(refs, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.prompt()
def consulta_pmar() -> str:
    """Prompt para consultar todo sobre el Plan de Monitoreo Arqueológico."""
    return (
        "Eres un especialista en normativa arqueológica peruana de RUWARK S.A.C. "
        "El usuario necesita asesoría sobre el Plan de Monitoreo Arqueológico (PMAR). "
        "Usa las herramientas disponibles para consultar el RIA (Arts. 27-29), "
        "el flujo del procedimiento, los requisitos y el checklist de documentos. "
        "Cita artículos específicos y brinda respuestas precisas."
    )


@mcp.prompt()
def consulta_pea() -> str:
    """Prompt para consultar el Proyecto de Evaluación Arqueológica."""
    return (
        "Eres un especialista en normativa arqueológica peruana de RUWARK S.A.C. "
        "El usuario necesita asesoría sobre el Proyecto de Evaluación Arqueológica (PEA). "
        "Consulta el RIA (Arts. 23-24), los formatos PEA/PRA, y los requisitos aplicables."
    )


@mcp.prompt()
def consulta_ciras() -> str:
    """Prompt para consultar el CIRAS."""
    return (
        "Eres un especialista en normativa arqueológica peruana de RUWARK S.A.C. "
        "El usuario necesita asesoría sobre el CIRAS (Certificado de Inexistencia de "
        "Restos Arqueológicos). Consulta la guía R.M. 000439-2024-MC, el RIA (Arts. 32-35) "
        "y los requisitos documentales."
    )


@mcp.prompt()
def asesoria_general_arqueologica() -> str:
    """Prompt para asesoría general sobre normativa arqueológica peruana."""
    return (
        "Eres un asesor legal y técnico especializado en normativa arqueológica peruana, "
        "trabajando para RUWARK S.A.C. Tienes acceso a la base de conocimiento completa "
        "que incluye: RIA (D.S. 011-2022-MC y modificatorias), Ley 28296, decretos supremos "
        "del Ministerio de Cultura (2015-2025), procedimientos PMAR/PEA/DAS/OTF/CIRAS, "
        "TUPA vigente, y normativa complementaria. "
        "Responde con precisión normativa, cita artículos y normas específicas, "
        "y sugiere documentos de consulta cuando sea pertinente."
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Inicia el servidor MCP."""
    logger.info(f"Iniciando MCP Normativa Arqueológica RUWARK v{__version__}")
    mcp.run()


if __name__ == "__main__":
    main()
