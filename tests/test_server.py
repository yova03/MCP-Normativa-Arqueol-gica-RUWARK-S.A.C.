import normativa_ruwark
from normativa_ruwark.server import (
    consultar_procedimiento,
    info_servidor,
    leer_documento,
    listar_normativas,
)


def test_version_matches_release() -> None:
    assert normativa_ruwark.__version__ == "2026.3.1"


def test_info_servidor_lists_core_tools() -> None:
    contenido = info_servidor()

    assert "MCP Server" in contenido
    assert "buscar_normativa" in contenido
    assert "consultar_ria" in contenido


def test_listar_normativas_for_pmar_contains_expected_docs() -> None:
    contenido = listar_normativas("pmar")

    assert "flujo-pmar.md" in contenido
    assert "requisitos-pmar.md" in contenido


def test_leer_documento_returns_full_markdown() -> None:
    contenido = leer_documento("pmar/requisitos-pmar.md")

    assert "PMAR" in contenido
    assert "Director" in contenido


def test_consultar_procedimiento_pmar_aggregates_sources() -> None:
    contenido = consultar_procedimiento("pmar")

    assert "PROCEDIMIENTO" in contenido
    assert "pmar/flujo-pmar.md" in contenido
    assert "pmar/requisitos-pmar.md" in contenido
