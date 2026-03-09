#!/usr/bin/env python3
"""
Script to convert extracted .txt files from LEARNING NORMATIVA ARQUEOLOGICA
into properly formatted Markdown knowledge base files.

Handles:
1. Encoding correction (garbled Spanish chars → proper UTF-8)
2. OCR error fixes (common patterns)
3. Markdown structuring with proper hierarchy
"""

import re
import sys
import os

# Common OCR replacement patterns for the RIA texts
# These PDFs were extracted with a broken encoding that garbles accented chars
OCR_FIXES = {
    # Most of these are already garbled to '?' in the extraction
    # Re-readable patterns from context
    '.caci': 'ficaci',
    '.cado': 'ficado',
    '.car': 'ficar',
    '.nes': 'fines',
    '.cos': 'ficos',
    '.ca ': 'fica ',
    '.ca.': 'fica.',
    '.cio': 'ficio',
    '.co ': 'fico ',
    '.co.': 'fico.',
    '.co,': 'fico,',
    '.cia ': 'ficia ',
    '.cia.': 'ficia.',
    '.cial': 'ficial',
    '.cien': 'ficien',
    '.cul': 'fícul',
    '.dad': 'fidad',
    '.ja ': 'fija ',
    '.jar ': 'fijar ',
    '.n ': 'fin ',
    '.nali': 'finali',
    '.nanc': 'financ',
    '.nida': 'finida',
    '.nido': 'finido',
    '.nir': 'finir',
    '.nit': 'finit',
    '.rma': 'firma',
    '.rm': 'firm',
    '.sic': 'físic',
    '.sonom': 'fisonom',
    '.xib': 'flexib',
    # Add missing fix for "de.ne" → "define"
}

def fix_encoding(text):
    """Fix known encoding issues in the extracted text."""
    # The texts use windows-1252 but some chars got garbled
    # Most are already readable, just need OCR fixes
    return text

def fix_ocr_errors(text):
    """Fix common OCR errors from PDF extraction."""
    for old, new in OCR_FIXES.items():
        text = text.replace(old, new)
    
    # Fix ".ej." patterns  
    text = text.replace('(p. ej.', '(p. ej.')
    
    # Fix double periods
    text = re.sub(r'\.\.+', '.', text)
    
    # Fix broken line breaks within paragraphs
    # (lines that don't end with period, colon, or are headers)
    
    return text

def is_titulo(line):
    """Check if line is a TÍTULO heading."""
    return bool(re.match(r'^TÍTULO\s+[IVX]+\b', line.strip(), re.IGNORECASE)) or \
           bool(re.match(r'^T[ÍI]TULO\s+[IVX]+\b', line.strip(), re.IGNORECASE)) or \
           bool(re.match(r'^T.TULO\s+[IVX]+\b', line.strip()))

def is_capitulo(line):
    """Check if line is a CAPÍTULO heading."""  
    return bool(re.match(r'^CAP[ÍI]TULO\s+[IVX]+\b', line.strip(), re.IGNORECASE)) or \
           bool(re.match(r'^CAP.TULO\s+[IVX]+\b', line.strip()))

def is_articulo(line):
    """Check if line is an Artículo heading."""
    return bool(re.match(r'^Art[íi]culo\s+\d+[\.\-]', line.strip(), re.IGNORECASE)) or \
           bool(re.match(r'^Art[íi]culo\s+[IVX]+[\.\-]', line.strip(), re.IGNORECASE)) or \
           bool(re.match(r'^Art.culo\s+\d+[\.\-]', line.strip())) or \
           bool(re.match(r'^Art.culo\s+[IVX]+[\.\-]', line.strip()))

def is_disposicion(line):
    """Check if line is a DISPOSICIÓN heading."""
    return bool(re.match(r'^DISPOSICI', line.strip(), re.IGNORECASE))

def is_titulo_prelim(line):
    """Check if line is TÍTULO PRELIMINAR."""
    return 'TÍTULO PRELIMINAR' in line.upper() or 'TITULO PRELIMINAR' in line.upper() or \
           'T\xcdTULO PRELIMINAR' in line

def get_titulo_name(lines, idx):
    """Get the name following a TÍTULO line (usually on next line)."""
    if idx + 1 < len(lines):
        next_line = lines[idx + 1].strip()
        if next_line and not is_capitulo(next_line) and not is_articulo(next_line):
            return next_line
    return ""

def get_capitulo_name(lines, idx):
    """Get the name following a CAPÍTULO line (usually on next line)."""
    if idx + 1 < len(lines):
        next_line = lines[idx + 1].strip()
        if next_line and not is_articulo(next_line) and not is_titulo(next_line):
            return next_line
    return ""

def process_ria_2022(input_path, output_path):
    """Process the RIA 2022 text file into structured Markdown."""
    
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Fix encoding and OCR
    content = fix_ocr_errors(content)
    
    lines = content.split('\n')
    
    # Build the markdown output
    md = []
    
    # Metadata header
    md.append("# Reglamento de Intervenciones Arqueológicas")
    md.append("")
    md.append("> **Tipo:** Decreto Supremo")
    md.append("> **Número:** D.S. N° 011-2022-MC")
    md.append("> **Fecha de publicación:** 23/11/2022")
    md.append("> **Estado:** Vigente, modificado por D.S. N° 004-2025-MC (→ ver [Modificatoria RIA](ria-modificatoria-ds-004-2025-mc.md))")
    md.append("")
    md.append("---")
    md.append("")
    
    in_decreto_header = True  # Skip the decreto preamble until we hit the Reglamento
    skip_next_as_subheading = False
    current_titulo = ""
    current_capitulo = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines at beginning
        if not line:
            if not in_decreto_header:
                md.append("")
            i += 1
            continue
        
        # Skip page headers like "El Peruano" 
        if line in ('El Peruano', 'NORMAS LEGALES', ''):
            i += 1
            continue
        
        # Detect end of decreto header / start of Reglamento
        if 'REGLAMENTO DE INTERVENCIONES ARQUEOLÓGICAS' in line.upper() or \
           'REGLAMENTO DE INTERVENCIONES ARQUEOL' in line:
            in_decreto_header = False
            # Don't add the duplicate title, we already have it
            i += 1
            continue
        
        if in_decreto_header:
            # Include decreto articles and disposiciones in the header section
            if is_articulo(line) or is_disposicion(line) or line.startswith('Primera.') or \
               line.startswith('Segunda.') or line.startswith('Tercera.') or \
               line.startswith('Cuarta.') or line.startswith('Quinta.') or \
               line.startswith('Sexta.') or line.startswith('Única.') or \
               line.startswith('Dado en'):
                in_decreto_header = False  
                # We'll keep collecting the reglamento header info
                if 'REGLAMENTO' not in line.upper():
                    i += 1
                    continue
            else:
                i += 1
                continue
        
        # TÍTULO PRELIMINAR
        if is_titulo_prelim(line):
            md.append("## Título Preliminar")
            md.append("")
            i += 1
            continue
        
        # TÍTULO I, II, etc.
        if is_titulo(line):
            titulo_match = re.search(r'[IVX]+', line)
            if titulo_match:
                titulo_num = titulo_match.group()
                name = get_titulo_name(lines, i)
                if name:
                    md.append(f"## Título {titulo_num} — {name}")
                    i += 2  # Skip the name line too
                else:
                    md.append(f"## Título {titulo_num}")
                    i += 1
                md.append("")
                continue
            i += 1
            continue
        
        # CAPÍTULO
        if is_capitulo(line):
            cap_match = re.search(r'[IVX]+', line)
            if cap_match:
                cap_num = cap_match.group()
                name = get_capitulo_name(lines, i)
                if name:
                    md.append(f"### Capítulo {cap_num} — {name}")
                    i += 2
                else:
                    md.append(f"### Capítulo {cap_num}")
                    i += 1
                md.append("")
                continue
            i += 1
            continue
        
        # DISPOSICIONES headings
        if is_disposicion(line):
            md.append(f"### {line}")
            md.append("")
            i += 1
            continue
        
        # Artículo
        if is_articulo(line):
            # Format: "Artículo X. Title" or "Artículo X.- Title"
            # Use #### for articles
            art_line = line.replace('.-', '.').replace('Artículo', 'Artículo').replace('Articulo', 'Artículo')
            # Fix garbled 'Artículo'
            art_line = re.sub(r'Art.culo', 'Artículo', art_line)
            md.append(f"#### {art_line}")
            md.append("")
            i += 1
            continue
        
        # Sub-articles like "1.1", "23.7", etc.
        sub_art_match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
        if sub_art_match:
            num = sub_art_match.group(1)
            rest = sub_art_match.group(2)
            md.append(f"**{num}** {rest}")
            md.append("")
            i += 1
            continue
        
        # Numbered items: "1.", "2.", etc. at start
        numbered_match = re.match(r'^(\d+)\.\s*$', line)
        if numbered_match:
            # Number alone on line, content follows
            i += 1
            if i < len(lines):
                next_content = lines[i].strip()
                md.append(f"**{numbered_match.group(1)}.** {next_content}")
                md.append("")
            i += 1
            continue
        
        # Lettered items: a), b), etc.
        letter_match = re.match(r'^([a-z])\)\s*(.+)', line)
        if letter_match:
            md.append(f"**{letter_match.group(1)})** {letter_match.group(2)}")
            md.append("")
            i += 1
            continue
        
        # Named disposiciones: "Primera.-", "Segunda.-"
        disp_match = re.match(r'^(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Única)[\.\-]+\s*(.*)', line)
        if disp_match:
            md.append(f"**{disp_match.group(1)}.** {disp_match.group(2)}")
            md.append("")
            i += 1
            continue
        
        # Regular paragraph - just add it
        md.append(line)
        md.append("")
        i += 1
    
    # Clean up multiple blank lines
    result = '\n'.join(md)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    # Final encoding fixes for the output
    # Replace garbled characters that made it through
    result = result.replace('ón', 'ón')
    result = result.replace('á', 'á')
    result = result.replace('é', 'é')
    result = result.replace('í', 'í')
    result = result.replace('ú', 'ú')
    result = result.replace('ñ', 'ñ')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"Written {len(result)} chars to {output_path}")
    return result

if __name__ == '__main__':
    base = r"d:\PROYECTO_A_CODIGO\LEARNING NORMATIVA ARQUEOLOGICA"
    input_file = os.path.join(base, "MARKDOWN", "RIA 2022.txt")
    output_file = os.path.join(base, "knowledge_base", "normativa-general", "ria-ds-011-2022-mc.md")
    
    process_ria_2022(input_file, output_file)
    print("RIA 2022 conversion complete!")
