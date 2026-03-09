from normativa_ruwark.search import KB_DIR, buscar, buscar_decreto_supremo, construir_indice


def test_knowledge_base_exists() -> None:
    assert KB_DIR.exists()


def test_build_index_loads_expected_categories() -> None:
    indice = construir_indice()

    assert indice.total_docs >= 140
    assert "README.md" not in indice.documentos
    assert "normativa-general" in indice.por_categoria
    assert "decretos-supremos" in indice.por_categoria


def test_keyword_search_returns_pmar_content() -> None:
    indice = construir_indice()

    resultados = buscar(indice, "monitoreo", categoria="pmar", max_resultados=5)

    assert resultados
    assert any(resultado.archivo.startswith("pmar/") for resultado in resultados)


def test_decreto_search_filters_by_year_and_number() -> None:
    indice = construir_indice()

    resultados = buscar_decreto_supremo(indice, anio="2025", numero="004")

    assert resultados
    assert resultados[0].archivo.startswith("decretos-supremos/2025/")
