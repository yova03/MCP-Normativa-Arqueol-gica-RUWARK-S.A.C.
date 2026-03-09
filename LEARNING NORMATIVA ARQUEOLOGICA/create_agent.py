#!/usr/bin/env python3
"""
create_agent.py — Meta-agente: genera nuevos agentes a partir de specs YAML.

Uso:
    python create_agent.py --spec agent_specs/nuevo_spec.yaml
    python create_agent.py --list
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from textwrap import dedent

BASE_DIR = Path(__file__).resolve().parent
AGENTS_DIR = BASE_DIR / "agents"
SPECS_DIR = BASE_DIR / "agent_specs"


AGENT_TEMPLATE = '''\
#!/usr/bin/env python3
"""
{filename} — {name}

Generado automáticamente por create_agent.py
Ejecutar: python {filename}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class {class_name}(ArchaeologyAgent):
    """{docstring}"""

    AGENT_SPEC = {{
        "name": "{name}",
        "domain": "{domain}",
        "knowledge_sources": {sources},
        "capabilities": {capabilities},
        "system_prompt": """{system_prompt}""",
    }}

    {class_name}_CHECKLIST = {checklist}

    def show_checklist(self):
        """Muestra el checklist del agente."""
        print("\\n  📋 CHECKLIST — {{}}".format(self.AGENT_SPEC["domain"]))
        print("  " + "─" * 50)
        for item, done in self.{class_name}_CHECKLIST.items():
            status = "☑" if done else "☐"
            print(f"    {{status}} {{item}}")
        result = self.validate_checklist(self.{class_name}_CHECKLIST)
        print(f"\\n  Estado: {{result['completed']}}/{{result['total']}} ({{result['percentage']:.0f}}%)")
        print()


if __name__ == "__main__":
    agent = {class_name}()
    agent.run()
'''


def load_spec(spec_path: str) -> dict:
    """Carga una especificación YAML."""
    with open(spec_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_agent(spec: dict, output_dir: Path = AGENTS_DIR):
    """Genera un archivo .py de agente a partir de la spec."""
    name = spec["name"]
    domain = spec["domain"]
    slug = spec.get("slug", domain.lower().replace(" ", "_"))
    filename = f"{slug}_agent.py"
    class_name = "".join(w.capitalize() for w in slug.split("_")) + "Agent"
    
    sources = spec.get("knowledge_sources", [])
    capabilities = spec.get("capabilities", [])
    system_prompt = spec.get("system_prompt", f"Eres un especialista en {domain}.")
    checklist_items = spec.get("checklist", {})
    checklist = {item: False for item in checklist_items} if isinstance(checklist_items, list) else checklist_items
    
    code = AGENT_TEMPLATE.format(
        filename=filename,
        name=name,
        domain=domain,
        class_name=class_name,
        docstring=f"Agente especializado en {domain}.",
        sources=repr(sources),
        capabilities=repr(capabilities),
        system_prompt=system_prompt.strip(),
        checklist=repr(checklist),
    )
    
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"  ✅ Generado: {output_path}")
    return output_path


def list_specs():
    """Lista las specs disponibles."""
    if not SPECS_DIR.exists():
        print("  No hay directorio agent_specs/")
        return
    
    specs = list(SPECS_DIR.glob("*.yaml")) + list(SPECS_DIR.glob("*.yml"))
    if not specs:
        print("  No hay specs YAML disponibles.")
        return
    
    print("\n  📑 Specs disponibles:")
    for spec_path in sorted(specs):
        spec = load_spec(spec_path)
        print(f"    • {spec_path.name}: {spec.get('name', '?')} — {spec.get('domain', '?')}")
    print()


def list_agents():
    """Lista los agentes existentes."""
    agents = list(AGENTS_DIR.glob("*_agent.py"))
    print("\n  🤖 Agentes existentes:")
    for agent_path in sorted(agents):
        print(f"    • {agent_path.name}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generador de Agentes Antigravity")
    parser.add_argument("--spec", help="Ruta al archivo YAML de especificación")
    parser.add_argument("--list", action="store_true", help="Listar specs y agentes")
    args = parser.parse_args()
    
    print("\n  🚀 Antigravity Agent Generator\n")
    
    if args.list:
        list_specs()
        list_agents()
        return
    
    if args.spec:
        spec = load_spec(args.spec)
        generate_agent(spec)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
