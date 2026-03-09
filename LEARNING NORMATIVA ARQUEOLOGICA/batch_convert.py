#!/usr/bin/env python3
"""
Batch converter: LEARNING NORMATIVA ARQUEOLOGICA txt → Markdown knowledge base.
Handles encoding (latin-1 → UTF-8), OCR artifact fixing, and Markdown structuring.
"""

import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'd:\PROYECTO_A_CODIGO\LEARNING NORMATIVA ARQUEOLOGICA'
MARKDOWN_DIR = os.path.join(BASE, 'MARKDOWN')
KB_DIR = os.path.join(BASE, 'knowledge_base')

# ─── OCR FI-LIGATURE FIXES ───────────────────────────────────────────────
FI_FIXES = {
    'de.ne': 'define', 'de.nición': 'definición', 'De.n': 'Defin',
    'signi.c': 'signific', 'especí.c': 'específic', 'cientí.c': 'científic',
    'Certi.c': 'Certific', 'certi.c': 'certific',
    'Super.c': 'Superfic', 'super.c': 'superfic',
    'verific': 'verific', 'Verific': 'Verific',
    'veri.c': 'verific', 'Veri.c': 'Verific',
    'identi.c': 'identific', 'Identi.c': 'Identific',
    'justi.c': 'justific', 'noti.c': 'notific',
    'modi.c': 'modific', 'Modi.c': 'Modific',
    'simpli.c': 'simplific', 'plani.c': 'planific',
    'cali.c': 'calific', 'Cali.c': 'Calific',
    'clasi.c': 'clasific', 'Clasi.c': 'Clasific',
    'bene.c': 'benefic', 'o.ci': 'ofici', 'O.ci': 'Ofici',
    'su.ci': 'sufici', 'e.ci': 'efici', 'edi.c': 'edific',
    'grá.c': 'gráfic', 'magní.c': 'magnífc',
    'in.uencia': 'influencia', 'In.uencia': 'Influencia',
    're.eja': 'refleja', 'Re.eja': 'Refleja',
    '.naliz': 'finaliz', '.nali': 'finali', '.nanc': 'financ',
    '.nid': 'finid', '.nir': 'finir',
    '.nal ': 'final ', '.nal,': 'final,', '.nal.': 'final.',
    '.rma': 'firma', '.rm': 'firm',
    '.ja ': 'fija ', '.jar ': 'fijar ',
    '.sic': 'físic', '.sonom': 'fisonom', '.xib': 'flexib',
    '.cha ': 'ficha ', '.cha,': 'ficha,', '.cha.': 'ficha.',
    '.chas ': 'fichas ', '.chas,': 'fichas,', '.chas.': 'fichas.',
    '.nes ': 'fines ', '.nes,': 'fines,', '.nes.': 'fines.',
    '.cos ': 'ficos ', '.cos,': 'ficos,', '.cos.': 'ficos.',
    '.co ': 'fico ', '.co,': 'fico,', '.co.': 'fico.',
    '.ca ': 'fica ', '.ca,': 'fica,', '.ca.': 'fica.',
    '.dad': 'fidad',
    '.cado': 'ficado', '.cados': 'ficados',
    '.cada': 'ficada', '.cadas': 'ficadas',
    '.car ': 'ficar ', '.car.': 'ficar.', '.car,': 'ficar,',
    '.cación': 'ficación', '.caciones': 'ficaciones',
    '.cio ': 'ficio ', '.cio,': 'ficio,', '.cio.': 'ficio.',
    '.cial': 'ficial', '.cia ': 'ficia ', '.cia,': 'ficia,',
    '.cia.': 'ficia.', '.cien': 'ficien',
    'a .n ': 'a fin ', 'a .n,': 'a fin,', 'a .n.': 'a fin.',
    'con .n': 'con fin', 'tal .n': 'tal fin',
    'dicho .n': 'dicho fin', 'este .n': 'este fin',
    'cuyo .n': 'cuyo fin', ' .n ': ' fin ', ' .n,': ' fin,', ' .n.': ' fin.',
}

REGEX_FI_FIXES = [
    (r'bibliográ\.c', 'bibliográfic'),
    (r'fotográ\.c', 'fotográfic'),
    (r'topográ\.c', 'topográfic'),
    (r'geográ\.c', 'geográfic'),
    (r'cartográ\.c', 'cartográfic'),
]

CHAR_FIXES = {
    '\x93': '"', '\x94': '"', '\x96': '–', '\x97': '—',
    '\x91': "'", '\x92': "'", '\x85': '...', '\xa0': ' ',
}

def fix_text(text):
    """Fix encoding, OCR, and clean up text."""
    for old, new in CHAR_FIXES.items():
        text = text.replace(old, new)
    for old, new in FI_FIXES.items():
        text = text.replace(old, new)
    for pattern, replacement in REGEX_FI_FIXES:
        text = re.sub(pattern, replacement, text)
    return text

def structurize_markdown(text, metadata):
    """Convert plain text to structured Markdown with headers."""
    lines = text.split('\n')
    md = []
    
    # Add metadata header
    md.append(f"# {metadata['title']}")
    md.append("")
    md.append(f"> **Tipo:** {metadata['tipo']}")
    md.append(f"> **Número:** {metadata['numero']}")
    md.append(f"> **Fecha de publicación:** {metadata['fecha']}")
    md.append(f"> **Estado:** {metadata['estado']}")
    md.append("")
    md.append("---")
    md.append("")
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty
        if not stripped:
            md.append("")
            continue
        
        # Skip page headers
        if stripped in ('El Peruano', 'NORMAS LEGALES'):
            continue
        
        # TÍTULO PRELIMINAR
        if 'TÍTULO PRELIMINAR' in stripped or 'TITULO PRELIMINAR' in stripped:
            md.append("## Título Preliminar")
            md.append("")
            continue
        
        # TÍTULO X (alone on line)
        titulo_match = re.match(r'^T[ÍI]TULO\s+([IVX]+)\s*$', stripped, re.IGNORECASE)
        if titulo_match:
            titulo_num = titulo_match.group(1)
            # Peek at next line for name
            if i + 1 < len(lines) and lines[i+1].strip() and not re.match(r'^(CAP|ART|T[ÍI]T)', lines[i+1].strip(), re.IGNORECASE):
                name = lines[i+1].strip()
                lines[i+1] = ''  # consume it
                md.append(f"## Título {titulo_num} — {name}")
            else:
                md.append(f"## Título {titulo_num}")
            md.append("")
            continue
        
        # CAPÍTULO X (alone on line)
        cap_match = re.match(r'^CAP[ÍI]TULO\s+([IVX]+)\s*$', stripped, re.IGNORECASE)
        if cap_match:
            cap_num = cap_match.group(1)
            if i + 1 < len(lines) and lines[i+1].strip() and not re.match(r'^(ART|CAP|T[ÍI]T)', lines[i+1].strip(), re.IGNORECASE):
                name = lines[i+1].strip()
                lines[i+1] = ''
                md.append(f"### Capítulo {cap_num} — {name}")
            else:
                md.append(f"### Capítulo {cap_num}")
            md.append("")
            continue
        
        # DISPOSICIONES headings
        if re.match(r'^DISPOSICI[OÓ]N', stripped, re.IGNORECASE):
            md.append(f"### {stripped}")
            md.append("")
            continue
        
        # Artículo X.
        art_match = re.match(r'^Art[íi]culo\s+(\d+|[IVX]+)[\.\-]+\s*(.*)', stripped, re.IGNORECASE)
        if art_match:
            art_num = art_match.group(1)
            art_title = art_match.group(2).strip()
            if art_title:
                md.append(f"#### Artículo {art_num}. {art_title}")
            else:
                md.append(f"#### Artículo {art_num}.")
            md.append("")
            continue
        
        # Sub-article: X.Y content  
        sub_match = re.match(r'^(\d+\.\d+)\s+(.+)', stripped)
        if sub_match:
            md.append(f"**{sub_match.group(1)}** {sub_match.group(2)}")
            md.append("")
            continue
        
        # Regular text
        md.append(stripped)
        md.append("")
    
    result = '\n'.join(md)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def convert_file(src_txt, dest_md, metadata):
    """Convert a single txt file to markdown."""
    with open(src_txt, 'rb') as f:
        raw = f.read()
    
    text = raw.decode('latin-1')
    text = fix_text(text)
    result = structurize_markdown(text, metadata)
    
    os.makedirs(os.path.dirname(dest_md), exist_ok=True)
    with open(dest_md, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"  ✅ {os.path.basename(dest_md)}: {len(result):,} chars")
    return len(result)

# ─── DOCUMENT DEFINITIONS ─────────────────────────────────────────────
DOCUMENTS = [
    # Already done: RIA 2022
    
    # 2. Modificatoria RIA
    {
        'src': 'Modificatoria del RIA.txt',
        'dest': 'normativa-general/ria-modificatoria-ds-004-2025-mc.md',
        'metadata': {
            'title': 'Modificatoria del Reglamento de Intervenciones Arqueológicas',
            'tipo': 'Decreto Supremo',
            'numero': 'D.S. N° 004-2025-MC',
            'fecha': '12/03/2025',
            'estado': 'Vigente — modifica D.S. N° 011-2022-MC (→ ver [RIA](ria-ds-011-2022-mc.md))',
        }
    },
    # 3. Ley 28296
    {
        'src': 'LEY Nº 28296 Ley General del Patrimonio Cultural de la Nación.doc.txt',
        'dest': 'normativa-general/ley-28296-patrimonio-cultural.md',
        'metadata': {
            'title': 'Ley General del Patrimonio Cultural de la Nación',
            'tipo': 'Ley',
            'numero': 'Ley N° 28296',
            'fecha': '22/07/2004',
            'estado': 'Vigente — modificada por múltiples normas',
        }
    },
    # 4. TUPA 2025
    {
        'src': 'TUPA 2025.txt',
        'dest': 'normativa-general/tupa-2025-ministerio-cultura.md',
        'metadata': {
            'title': 'Texto Único de Procedimientos Administrativos — TUPA del Ministerio de Cultura',
            'tipo': 'TUPA',
            'numero': 'D.S. N° 005-2024-MC',
            'fecha': '22/08/2024',
            'estado': 'Vigente',
        }
    },
    # 5. Guía CIRAS
    {
        'src': 'Guía para la expedición del CIRAS.txt',
        'dest': 'ciras/guia-expedicion-ciras.md',
        'metadata': {
            'title': 'Guía para la Expedición del Certificado de Inexistencia de Restos Arqueológicos en Superficie (CIRAS)',
            'tipo': 'Guía Administrativa',
            'numero': 'R.M. N° 000439-2024-MC (Anexo)',
            'fecha': '2024',
            'estado': 'Vigente',
        }
    },
    # 6. PEA (Formatos)
    {
        'src': 'PEA .txt',
        'dest': 'pea/formatos-pea-pra.md',
        'metadata': {
            'title': 'Formatos de Información Técnica para Autorización de PEA y PRA',
            'tipo': 'Resolución Directoral',
            'numero': 'R.D. DGPA (Formatos PEA/PRA)',
            'fecha': '2024',
            'estado': 'Vigente',
        }
    },
    # 7. Guía de Excavación / RVM 063-2021
    {
        'src': 'GUIA DE EXCAVACIÓN.txt',
        'dest': 'complementaria/guia-excavacion-rvm-063-2021.md',
        'metadata': {
            'title': 'Guía de Excavación Arqueológica',
            'tipo': 'Resolución Viceministerial',
            'numero': 'RVM N° 063-2021-VMPCIC-MC',
            'fecha': '2021',
            'estado': 'Vigente',
        }
    },
    # 8. Guía Entrega Bienes Culturales
    {
        'src': 'Guia para la Entrega de Bienes Culturales Muebles-RV N 00171-2020-VMPCIC.pdf.txt',
        'dest': 'complementaria/guia-entrega-bienes-culturales.md',
        'metadata': {
            'title': 'Guía para la Entrega de Bienes Culturales Muebles',
            'tipo': 'Resolución Viceministerial',
            'numero': 'RV N° 00171-2020-VMPCIC',
            'fecha': '2020',
            'estado': 'Vigente',
        }
    },
    # 9. DS 014-92-EM
    {
        'src': 'DS_014-92-EM.txt',
        'dest': 'complementaria/ds-014-92-em-reglamento-mineria.md',
        'metadata': {
            'title': 'Reglamento de Procedimientos Mineros',
            'tipo': 'Decreto Supremo',
            'numero': 'D.S. N° 014-92-EM',
            'fecha': '04/06/1992',
            'estado': 'Vigente — con modificatorias',
        }
    },
    # 10. RM 000439-2024-MC (Formatos)
    {
        'src': '6302533-rm-000439-2024-mc-anexo-1.txt',
        'dest': 'complementaria/rm-000439-2024-mc-formatos.md',
        'metadata': {
            'title': 'Formatos para Intervenciones Arqueológicas — Anexo 1',
            'tipo': 'Resolución Ministerial',
            'numero': 'R.M. N° 000439-2024-MC',
            'fecha': '2024',
            'estado': 'Vigente',
        }
    },
    # 11. RIA 2025 (= RIA + Modificatoria consolidado)
    {
        'src': 'RIA 2025.txt',
        'dest': 'normativa-general/ria-2025-consolidado.md',
        'metadata': {
            'title': 'Reglamento de Intervenciones Arqueológicas — Texto Consolidado 2025',
            'tipo': 'Decreto Supremo (consolidado)',
            'numero': 'D.S. N° 011-2022-MC + D.S. N° 004-2025-MC',
            'fecha': '2025',
            'estado': 'Vigente — texto consolidado con modificaciones',
        }
    },
    # 12. Resolución DDC Cusco (ejemplo)
    {
        'src': 'RESOLUCION DIRECTORAL-001081-2025-DE-DDC-CUS.txt',
        'dest': 'complementaria/rd-001081-2025-ddc-cusco.md',
        'metadata': {
            'title': 'Resolución Directoral N° 001081-2025-DDC-CUS',
            'tipo': 'Resolución Directoral',
            'numero': 'R.D. N° 001081-2025-DE-DDC-CUS',
            'fecha': '2025',
            'estado': 'Vigente (caso específico)',
        }
    },
    # 13. DS 004-2025-MC (duplicate source)
    {
        'src': 'DS N° 004-2025-MC.txt',
        'dest': None,  # Skip, already covered by Modificatoria del RIA.txt
        'metadata': None,
    },
    # 14. Normas Legales 2020 (DS 007-2020-MC)
    {
        'src': 'Normas_Legales_20200808.indd.txt',
        'dest': 'normativa-general/reglamento-ley-28296-modificatoria-2020.md',
        'metadata': {
            'title': 'Modificación del Reglamento de la Ley N° 28296 (D.S. N° 007-2020-MC)',
            'tipo': 'Decreto Supremo',
            'numero': 'D.S. N° 007-2020-MC',
            'fecha': '05/06/2020',
            'estado': 'Vigente — modifica D.S. N° 011-2006-ED',
        }
    },
    # 15. RVM 063-2021 Anexo (same as Guía Excavación)
    {
        'src': 'RVM 063-2021-VMPCIC-MC - ANEXO.pdf.txt',
        'dest': None,  # Skip, same content as GUIA DE EXCAVACIÓN.txt
        'metadata': None,
    },
]

def main():
    total_chars = 0
    converted = 0
    skipped = 0
    
    print("=" * 60)
    print("BATCH CONVERSION: NORMATIVA → MARKDOWN KNOWLEDGE BASE")
    print("=" * 60)
    print()
    
    for doc in DOCUMENTS:
        src_path = os.path.join(MARKDOWN_DIR, doc['src'])
        
        if doc['dest'] is None:
            print(f"  ⏩ Skipped (duplicate): {doc['src']}")
            skipped += 1
            continue
        
        dest_path = os.path.join(KB_DIR, doc['dest'])
        
        if not os.path.exists(src_path):
            print(f"  ❌ NOT FOUND: {doc['src']}")
            continue
        
        chars = convert_file(src_path, dest_path, doc['metadata'])
        total_chars += chars
        converted += 1
    
    print()
    print(f"{'='*60}")
    print(f"RESULTS: {converted} converted, {skipped} skipped")
    print(f"Total: {total_chars:,} chars written")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
