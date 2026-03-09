#!/usr/bin/env python3
"""
pea_agent.py â€” Agente especializado en Proyecto de EvaluaciÃ³n ArqueolÃ³gica.

Ejecutar: python pea_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class PeaAgent(ArchaeologyAgent):
    """Agente especializado en Proyecto de EvaluaciÃ³n ArqueolÃ³gica (PEA)."""

    AGENT_SPEC = {
        "name": "Agente PEA",
        "domain": "Proyecto de EvaluaciÃ³n ArqueolÃ³gica",
        "knowledge_sources": [
            "normativa-general/ria-ds-011-2022-mc.md",
            "normativa-general/ria-modificatoria-ds-004-2025-mc.md",
            "pea/flujo-pea.md",
            "pea/formatos-pea-pra.md",
            "comun/tupa-pagos.md",
            "comun/coarpe-habilitacion.md",
        ],
        "capabilities": [
            "Generar solicitud de autorizaciÃ³n PEA segÃºn Art. 23 RIA",
            "Diferenciar ampliaciÃ³n de plazo (Art. 30) vs Ã¡rea/objetivos (Art. 23.7)",
            "Controlar vencimientos de R.D. de autorizaciÃ³n",
            "Preparar expediente de ampliaciÃ³n",
            "Guiar elaboraciÃ³n del Plan de Trabajo PEA",
            "Calcular plazos de evaluaciÃ³n DDC",
            "Explicar el proceso post-evaluaciÃ³n (â†’ CIRAS o PMAR)",
        ],
        "system_prompt": """
            Eres un especialista en Proyectos de EvaluaciÃ³n ArqueolÃ³gica (PEA)
            bajo la normativa peruana. Dominas los Arts. 23, 23.7, 24 y 30 del RIA,
            los flujos de autorizaciÃ³n, ampliaciÃ³n y presentaciÃ³n de informes.
        """,
    }

    PEA_CHECKLIST = {
        "Formulario de solicitud": False,
        "Comprobante de pago TUPA": False,
        "Carta de financiamiento": False,
        "AcreditaciÃ³n de titularidad": False,
        "DJ habilitaciÃ³n Director (COARPE)": False,
        "DJ habilitaciÃ³n Residente (COARPE)": False,
        "Carta consentimiento expreso residente": False,
        "Cartas compromiso no afectaciÃ³n": False,
        "Plan de Trabajo PEA": False,
        "Planos de ubicaciÃ³n y delimitaciÃ³n": False,
        "Antecedentes arqueolÃ³gicos": False,
        "DescripciÃ³n del proyecto de inversiÃ³n": False,
    }

    def show_checklist(self):
        """Muestra el checklist de documentos PEA."""
        print("\n  ðŸ“‹ CHECKLIST â€” Expediente PEA (Art. 23 RIA)")
        print("  " + "â”€" * 50)
        for item, done in self.PEA_CHECKLIST.items():
            status = "â˜‘" if done else "â˜"
            print(f"    {status} {item}")
        result = self.validate_checklist(self.PEA_CHECKLIST)
        print(f"\n  Estado: {result['completed']}/{result['total']} ({result['percentage']:.0f}%)")
        print()


    def generate_plan_from_template(self, project_data, output_path):
        """Genera el Plan de Evaluación PEA en LaTeX a partir de la plantilla robusta."""
        template_path = Path("d:/PROYECTO_A_CODIGO/RUWARK OPERACIONES/PLANES_DE_TRABAJO/PEA/plantillas/02_PLAN_TRABAJO_PEA.tex")
        if not template_path.exists():
            print(f"Error: No se encontró la plantilla en {template_path}")
            return False
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Reemplazar variables
        for key, value in project_data.items():
            placeholder = f"[{key}]"
            template_content = template_content.replace(placeholder, str(value))
            
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
            
        print(f"\n  [OK] Plan de Evaluación PEA (LaTeX) generado exitosamente en: {out_file}")
        return True

if __name__ == "__main__":
    agent = PeaAgent()
    agent.run()


