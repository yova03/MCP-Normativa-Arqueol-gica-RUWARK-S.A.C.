#!/usr/bin/env python3
"""
pmar_agent.py â€” Agente especializado en Plan de Monitoreo ArqueolÃ³gico.

Ejecutar: python pmar_agent.py
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from base_agent import ArchaeologyAgent


class PmarAgent(ArchaeologyAgent):
    """Agente especializado en Plan de Monitoreo ArqueolÃ³gico (PMAR)."""

    AGENT_SPEC = {
        "name": "Agente PMAR",
        "domain": "Plan de Monitoreo ArqueolÃ³gico",
        "knowledge_sources": [
            # Normativa principal
            "normativa-general/ria-ds-011-2022-mc.md",
            "normativa-general/ria-modificatoria-ds-004-2025-mc.md",
            # Dominio especÃ­fico
            "pmar/flujo-pmar.md",
            "pmar/requisitos-pmar.md",
            # ComÃºn
            "comun/tupa-pagos.md",
            "comun/coarpe-habilitacion.md",
        ],
        "capabilities": [
            "Validar requisitos del expediente PMAR segÃºn Art. 27 RIA",
            "Generar checklist de documentos para presentar a DDC",
            "Buscar artÃ­culos del RIA relevantes al PMAR",
            "Verificar requisitos de habilitaciÃ³n COARPE",
            "Calcular plazos de evaluaciÃ³n segÃºn TUPA",
            "Explicar el flujo completo del proceso PMAR",
            "Consultar procedimiento en caso de hallazgos (Art. 28)",
            "Guiar la elaboraciÃ³n del informe de resultados (Art. 29)",
        ],
        "system_prompt": """
            Eres un especialista en Planes de Monitoreo ArqueolÃ³gico (PMAR)
            bajo la normativa peruana. Tu conocimiento se basa en el RIA
            (D.S. NÂ° 011-2022-MC y su modificatoria D.S. NÂ° 004-2025-MC),
            la Ley 28296, y los flujos operativos de RUWARK S.A.C.
            
            Responde con precisiÃ³n normativa, cita artÃ­culos especÃ­ficos,
            y genera documentos en el formato estÃ¡ndar corporativo.
        """,
    }

    # â”€â”€â”€ CHECKLIST PMAR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    PMAR_CHECKLIST = {
        # Administrativos
        "Formulario P01DGPA": False,
        "Comprobante de pago TUPA": False,
        "Carta de financiamiento (DJ titular)": False,
        "Carta poder simple": False,
        "AcreditaciÃ³n de titularidad": False,
        # Legales
        "DJ habilitaciÃ³n Director (COARPE)": False,
        "DJ habilitaciÃ³n Residente (COARPE)": False,
        "Carta consentimiento expreso residente": False,
        "Cartas compromiso no afectaciÃ³n": False,
        # TÃ©cnicos
        "Plan de Monitoreo ArqueolÃ³gico": False,
        "InformaciÃ³n tÃ©cnica del proyecto": False,
        "Antecedentes arqueolÃ³gicos": False,
        "DescripciÃ³n del proyecto de obra": False,
        "MetodologÃ­a de monitoreo": False,
        "Planos (ubicaciÃ³n, delimitaciÃ³n)": False,
    }

    def show_checklist(self):
        """Muestra el checklist de documentos PMAR."""
        print("\n  ðŸ“‹ CHECKLIST â€” Expediente PMAR (Art. 27 RIA)")
        print("  " + "â”€" * 50)
        
        sections = {
            "Documentos Administrativos": [
                "Formulario P01DGPA",
                "Comprobante de pago TUPA",
                "Carta de financiamiento (DJ titular)",
                "Carta poder simple",
                "AcreditaciÃ³n de titularidad",
            ],
            "Documentos Legales": [
                "DJ habilitaciÃ³n Director (COARPE)",
                "DJ habilitaciÃ³n Residente (COARPE)",
                "Carta consentimiento expreso residente",
                "Cartas compromiso no afectaciÃ³n",
            ],
            "Documentos TÃ©cnicos": [
                "Plan de Monitoreo ArqueolÃ³gico",
                "InformaciÃ³n tÃ©cnica del proyecto",
                "Antecedentes arqueolÃ³gicos",
                "DescripciÃ³n del proyecto de obra",
                "MetodologÃ­a de monitoreo",
                "Planos (ubicaciÃ³n, delimitaciÃ³n)",
            ],
        }
        
        for section, items in sections.items():
            print(f"\n  {section}:")
            for item in items:
                status = "â˜‘" if self.PMAR_CHECKLIST.get(item) else "â˜"
                print(f"    {status} {item}")
        
        result = self.validate_checklist(self.PMAR_CHECKLIST)
        print(f"\n  Estado: {result['completed']}/{result['total']} ({result['percentage']:.0f}%)")
        if result['missing']:
            print(f"  âš ï¸  Faltan {len(result['missing'])} documentos")
        else:
            print(f"  âœ… Expediente completo â€” listo para presentar")
        print()


    def generate_plan_from_template(self, project_data, output_path):
        """Genera el Plan de Trabajo PMAR en LaTeX a partir de la plantilla robusta."""
        template_path = Path("d:/PROYECTO_A_CODIGO/RUWARK OPERACIONES/PLANES_DE_TRABAJO/PMAR/plantillas/02_PLAN_TRABAJO_PMAR.tex")
        if not template_path.exists():
            print(f"Error: No se encontró la plantilla en {template_path}")
            return False
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Reemplazar variables
        for key, value in project_data.items():
            # Manejo básico de etiquetas tipo [NOMBRE_DEL_PROYECTO_DE_INVERSIÓN]
            placeholder = f"[{key}]"
            template_content = template_content.replace(placeholder, str(value))
            
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
            
        print(f"\n  [OK] Plan de Trabajo PMAR (LaTeX) generado exitosamente en: {out_file}")
        return True

if __name__ == "__main__":
    agent = PmarAgent()
    agent.run()


