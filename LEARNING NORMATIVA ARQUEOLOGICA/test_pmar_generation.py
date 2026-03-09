import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path("d:/PROYECTO_A_CODIGO/LEARNING NORMATIVA ARQUEOLOGICA/agents")))

from pmar_agent import PmarAgent

def run_test():
    print("Iniciando prueba de generaciÃ³n de Plan de Trabajo PMAR en LaTeX...")
    
    agent = PmarAgent()
    
    # Datos "Dummy" simulados para el proyecto
    dummy_project_data = {
        "NOMBRE_DEL_PROYECTO_DE_INVERSIÃ“N": "MEJORAMIENTO Y AMPLIACIÃ“N DE LOS SERVICIOS DE AGUA POTABLE Y ALCANTARILLADO DE LA CIUDAD DE JULIACA - PUNO",
        "RAZÃ“N SOCIAL / NOMBRE COMPLETO": "CONSORCIO SANEAMIENTO JULIACA S.A.",
        "X": "Juliaca",
        "Y": "San RomÃ¡n",
        "Z": "Puno",
        "Nombre Apellido": "Juan PÃ©rez Torres",
        "000": "1234",
        "RazÃ³n Social, RUC": "CONSORCIO SANEAMIENTO JULIACA S.A. - RUC: 20456789123",
        "17S/18S/19S": "19S",
        "000000": "375420.00",
        "0000000": "8286540.00",
        "Nombre del Sitio": "Capillapampa",
        "Distancia": "2.5",
        "metros/km": "km",
        "Apertura de zanjas / ExplanaciÃ³n de plataformas / NivelaciÃ³n": "Apertura de zanjas para instalaciÃ³n de redes colectoras",
        "X.XX": "3.50",
        "Y.YY": "1.20",
        "Retroexcavadora Orugas / Cargador Frontal / Martillo HidrÃ¡ulico": "Retroexcavadora sobre llantas y Excavadora sobre orugas",
        "0.00 ha / 0.00 km": "45.00 km",
        "X dÃ­as": "120 dÃ­as calendario",
        "0,000.00": "45,000.00",
        "NOMBRE DEL DIRECTOR": "JUAN PÃ‰REZ TORRES",
        "0000": "1234"
    }
    
    # Directorio de salida (usamos una carpeta de prueba)
    output_dir = Path("d:/PROYECTO_A_CODIGO/RUWARK OPERACIONES/PLANES_DE_TRABAJO/test_output")
    output_file = output_dir / "02_PLAN_TRABAJO_PMAR_TEST.tex"
    
    # Crear directorio si no existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar el plan
    success = agent.generate_plan_from_template(dummy_project_data, str(output_file))
    
    if success:
        print("\n  ðŸŽ‰ Prueba exitosa! El archivo fue generado.")
        print(f"  ðŸ“‚ Ruta: {output_file}")
    else:
        print("\n  âŒ FallÃ³ la prueba de generaciÃ³n.")

if __name__ == "__main__":
    run_test()

