#!/usr/bin/env python3
"""
das_agent.py — Agente especializado en Diagnóstico Arqueológico de Superficie.

Ejecutar: python das_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class DasAgent(ArchaeologyAgent):
    """Agente especializado en Diagnóstico Arqueológico de Superficie (DAS)."""

    AGENT_SPEC = {
        "name": "Agente DAS",
        "domain": "Diagnóstico Arqueológico de Superficie",
        "knowledge_sources": [
            "normativa-general/ria-ds-011-2022-mc.md",
            "das/flujo-das.md",
            "normativa-general/ley-28296-patrimonio-cultural.md",
        ],
        "capabilities": [
            "Generar estructura de informe técnico DAS",
            "Verificar que el DAS no requiere tasa TUPA",
            "Diferenciar DAS de CIRAS y PEA",
            "Guiar la inspección de superficie",
            "Consultar antecedentes en SIGDA",
            "Generar recomendaciones post-diagnóstico",
        ],
        "system_prompt": """
            Eres un especialista en Diagnósticos Arqueológicos de Superficie (DAS).
            El DAS es un informe técnico de evaluación visual sin excavación,
            no regulado directamente en el RIA pero utilizado como evaluación
            preliminar. No requiere tasa TUPA.
        """,
    }

    DAS_CHECKLIST = {
        "Datos del proyecto": False,
        "Ubicación y coordenadas UTM": False,
        "Consulta SIGDA": False,
        "Inspección de campo realizada": False,
        "Registro fotográfico": False,
        "Informe técnico DAS": False,
        "Conclusiones y recomendaciones": False,
    }

    def show_checklist(self):
        """Muestra el checklist DAS."""
        print("\n  📋 CHECKLIST — Informe DAS")
        print("  " + "─" * 50)
        for item, done in self.DAS_CHECKLIST.items():
            status = "☑" if done else "☐"
            print(f"    {status} {item}")
        result = self.validate_checklist(self.DAS_CHECKLIST)
        print(f"\n  Estado: {result['completed']}/{result['total']} ({result['percentage']:.0f}%)")
        print()


if __name__ == "__main__":
    agent = DasAgent()
    agent.run()
