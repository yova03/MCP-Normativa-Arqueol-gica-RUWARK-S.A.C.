#!/usr/bin/env python3
"""
otf_agent.py — Agente especializado en Opinión Técnica Favorable.

Ejecutar: python otf_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class OtfAgent(ArchaeologyAgent):
    """Agente especializado en Opinión Técnica Favorable (OTF)."""

    AGENT_SPEC = {
        "name": "Agente OTF",
        "domain": "Opinión Técnica Favorable",
        "knowledge_sources": [
            "normativa-general/ria-ds-011-2022-mc.md",
            "normativa-general/tuo-ley-27444-procedimiento-administrativo.md",
            "otf/flujo-otf.md",
            "comun/tupa-pagos.md",
        ],
        "capabilities": [
            "Generar carta de fundamentación para OTF",
            "Calcular plazos según TUO 27444",
            "Preparar documentación pre-PEA",
            "Explicar el proceso de OTF ante DDC",
            "Diferenciar OTF favorable / condicionada / no favorable",
            "Guiar siguiente paso post-OTF",
        ],
        "system_prompt": """
            Eres un especialista en Opiniones Técnicas Favorables (OTF)
            ante el Ministerio de Cultura. La OTF es un pronunciamiento
            previo al PEA. Dominas el TUO de la Ley 27444 y el RIA
            para calcular plazos y fundamentar solicitudes.
        """,
    }

    OTF_CHECKLIST = {
        "Carta de fundamentación": False,
        "Datos del solicitante": False,
        "Descripción del proyecto": False,
        "Coordenadas UTM del área": False,
        "Plano de ubicación": False,
        "Antecedentes arqueológicos": False,
        "EIA (si existe)": False,
    }

    def show_checklist(self):
        """Muestra el checklist OTF."""
        print("\n  📋 CHECKLIST — Solicitud OTF")
        print("  " + "─" * 50)
        for item, done in self.OTF_CHECKLIST.items():
            status = "☑" if done else "☐"
            print(f"    {status} {item}")
        result = self.validate_checklist(self.OTF_CHECKLIST)
        print(f"\n  Estado: {result['completed']}/{result['total']} ({result['percentage']:.0f}%)")
        print()


if __name__ == "__main__":
    agent = OtfAgent()
    agent.run()
