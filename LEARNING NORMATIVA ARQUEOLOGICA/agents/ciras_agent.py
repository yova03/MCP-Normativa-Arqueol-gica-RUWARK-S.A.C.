#!/usr/bin/env python3
"""
ciras_agent.py — Agente especializado en CIRAS.

Ejecutar: python ciras_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class CirasAgent(ArchaeologyAgent):
    """Agente especializado en Certificado de Inexistencia de Restos Arqueológicos (CIRAS)."""

    AGENT_SPEC = {
        "name": "Agente CIRAS",
        "domain": "Certificado de Inexistencia de Restos Arqueológicos en Superficie",
        "knowledge_sources": [
            "normativa-general/ria-ds-011-2022-mc.md",
            "ciras/guia-expedicion-ciras.md",
            "ciras/flujo-ciras.md",
            "comun/tupa-pagos.md",
        ],
        "capabilities": [
            "Guiar el llenado de solicitud CIRAS",
            "Validar Memoria Descriptiva según formato oficial",
            "Verificar especificaciones del plano perimétrico",
            "Calcular plazos de evaluación y subsanación",
            "Explicar proceso de CIRAS automático (post-PEA)",
            "Validar coordenadas UTM (WGS84, zona 17S/18S/19S)",
            "Listar requisitos del Art. 34 RIA",
        ],
        "system_prompt": """
            Eres un especialista en Certificados de Inexistencia de Restos
            Arqueológicos en Superficie (CIRAS). Dominas la Guía de Expedición
            del CIRAS (R.M. 000439-2024-MC) y los Arts. 32-35 del RIA.
            Conoces las especificaciones técnicas de planos, memorias descriptivas
            y coordenadas UTM requeridas.
        """,
    }

    CIRAS_CHECKLIST = {
        "Formulario de solicitud": False,
        "Comprobante de pago TUPA": False,
        "Memoria Descriptiva (Formato N°6)": False,
        "Plano perimétrico georreferenciado": False,
        "Cuadro de datos técnicos": False,
        "Esquema de ubicación": False,
        "Esquema de localización": False,
    }

    def show_checklist(self):
        """Muestra el checklist CIRAS."""
        print("\n  📋 CHECKLIST — Solicitud CIRAS (Art. 34 RIA)")
        print("  " + "─" * 50)
        for item, done in self.CIRAS_CHECKLIST.items():
            status = "☑" if done else "☐"
            print(f"    {status} {item}")
        result = self.validate_checklist(self.CIRAS_CHECKLIST)
        print(f"\n  Estado: {result['completed']}/{result['total']} ({result['percentage']:.0f}%)")
        print()


if __name__ == "__main__":
    agent = CirasAgent()
    agent.run()
