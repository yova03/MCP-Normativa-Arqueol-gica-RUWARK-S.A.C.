# MCP Normativa Arqueológica RUWARK

Servidor MCP para consultar normativa arqueológica del Perú desde clientes compatibles con Model Context Protocol.

Versión actual: `2026.3.1`

## Qué incluye

- Reglamento de Intervenciones Arqueológicas: D.S. N.° 011-2022-MC y modificatoria D.S. N.° 004-2025-MC.
- Ley N.° 28296 y normativa reglamentaria relacionada.
- TUPA 2025 del Ministerio de Cultura y TUO de la Ley N.° 27444.
- Procedimientos PMAR, PEA, DAS, OTF y CIRAS.
- 113 decretos supremos del Ministerio de Cultura entre 2015 y 2025.
- 147 documentos normativos indexados en Markdown.

## Herramientas MCP

- `buscar_normativa`: búsqueda por palabras clave en toda la base.
- `consultar_procedimiento`: flujos y requisitos de PMAR, PEA, DAS, OTF y CIRAS.
- `obtener_checklist`: checklist documental por procedimiento.
- `consultar_decreto_supremo`: búsqueda por año, número o texto libre.
- `leer_documento`: lectura completa de un documento de la base.
- `listar_normativas`: catálogo por categoría.
- `consultar_ria`: consulta por artículo o tema dentro del RIA.
- `referencias_cruzadas`: relaciones entre normas y procedimientos.
- `info_servidor`: estado y estadísticas del servidor.

## Recursos MCP

- `normativa://indice`
- `normativa://categorias`
- `normativa://referencias`

## Instalación local

```bash
git clone https://github.com/ruwark/mcp-normativa-ruwark.git
cd mcp-normativa-ruwark
python -m pip install -e .
```

Para desarrollo y pruebas:

```bash
python -m pip install -e .[dev]
pytest
```

## Instalación desde GitHub

Reemplaza `ruwark/mcp-normativa-ruwark` por la ruta real de tu repositorio si cambia.

```bash
python -m pip install git+https://github.com/ruwark/mcp-normativa-ruwark.git
```

## Ejecución

```bash
python -m normativa_ruwark.server
```

También queda disponible el script:

```bash
python -m normativa_ruwark
normativa-ruwark
```

## Cómo conectar otros clientes MCP

### Claude Desktop

Archivo: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "normativa-ruwark": {
      "command": "python",
      "args": ["-m", "normativa_ruwark.server"]
    }
  }
}
```

### VS Code

Archivo: `.vscode/mcp.json`

```json
{
  "servers": {
    "normativa-ruwark": {
      "command": "python",
      "args": ["-m", "normativa_ruwark.server"]
    }
  }
}
```

### Cursor o Windsurf

```json
{
  "mcpServers": {
    "normativa-ruwark": {
      "command": "python",
      "args": ["-m", "normativa_ruwark.server"]
    }
  }
}
```

## Verificación rápida

```bash
python -c "from normativa_ruwark.server import info_servidor; print(info_servidor())"
```

Si deseas cargar una base documental externa, define:

```bash
NORMATIVA_RUWARK_KB_DIR=/ruta/a/knowledge_base
```

## Estructura

```text
mcp-normativa-ruwark/
├── .github/workflows/ci.yml
├── README.md
├── pyproject.toml
├── src/normativa_ruwark/
│   ├── __init__.py
│   ├── search.py
│   ├── server.py
│   └── knowledge_base/
└── tests/
```

## Publicación recomendada

1. Crea el repositorio en GitHub.
2. Sube este contenido.
3. Verifica que GitHub Actions ejecute `pytest` y el build.
4. Comparte la URL del repositorio para que otros instalen con `pip install git+...`.

## Licencia

MIT. Revisa [LICENSE](LICENSE).
