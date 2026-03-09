#!/usr/bin/env python3
"""Fix encoding in the generated RIA 2022 markdown file."""
import sys
import os
import re

# Set stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'd:\PROYECTO_A_CODIGO\LEARNING NORMATIVA ARQUEOLOGICA\MARKDOWN\RIA 2022.txt'
output_path = r'd:\PROYECTO_A_CODIGO\LEARNING NORMATIVA ARQUEOLOGICA\knowledge_base\normativa-general\ria-ds-011-2022-mc.md'

# Read with latin-1 (never fails)
with open(input_path, 'rb') as f:
    raw = f.read()

text = raw.decode('latin-1')

# Now we have the text. Let's see what chars need fixing.
# The file uses a mix of encodings. Let's build a replacement map.
# Common garbled patterns in this Latin-1 decoded text:
replacements = {
    '\x93': '"',   # left double quote
    '\x94': '"',   # right double quote
    '\x96': '–',   # en dash
    '\x97': '—',   # em dash
    '\x91': "'",   # left single quote
    '\x92': "'",   # right single quote
    '\x85': '...',  # ellipsis
    '\xa0': ' ',   # non-breaking space
    # Spanish accented chars - these are already correct in latin-1
    # á = \xe1, é = \xe9, í = \xed, ó = \xf3, ú = \xfa, ñ = \xf1
    # ü = \xfc, Á = \xc1, É = \xc9, Í = \xcd, Ó = \xd3, Ú = \xda
    # Ñ = \xd1, ¿ = \xbf, ¡ = \xa1
}

for old, new in replacements.items():
    text = text.replace(old, new)

# The Spanish accented chars from latin-1 are already correct Unicode
# Now fix the OCR artifacts
ocr_fixes = [
    (r'\.caci', 'ficaci'),
    (r'\.cado', 'ficado'),
    (r'\.car ', 'ficar '),
    (r'\.nes ', 'fines '),
    (r'\.nes,', 'fines,'),
    (r'\.nes\.', 'fines.'),
    (r'\.cos ', 'ficos '),
    (r'\.cos,', 'ficos,'),
    (r'\.ca ', 'fica '),
    (r'\.cio ', 'ficio '),
    (r'\.co ', 'fico '),
    (r'\.cia ', 'ficia '),
    (r'\.cial', 'ficial'),
    (r'\.cien', 'ficien'),
    (r'\.dad', 'fidad'),
    (r'\.ja ', 'fija '),
    (r'\.nanc', 'financ'),
    (r'\.nali', 'finali'),
    (r'\.nida', 'finida'),
    (r'\.nido', 'finido'),
    (r'\.nir', 'finir'),
    (r'\.nit', 'finit'),
    (r'\.rma', 'firma'),
    (r'\.sic', 'físic'),
    (r'\.sonom', 'fisonom'),
    (r'\.xib', 'flexib'),
    (r'\.ej', 'fiej'),  # this won't work, skip
    (r'de\.ne', 'define'),
    (r'De\.n', 'Defin'),
    (r'\.nal ', 'final '),
    (r'\.nal,', 'final,'),
    (r'\.nal\.', 'final.'),
    (r'\.n ', 'fin '),
    (r'\.n,', 'fin,'),
    (r'\.n\.', 'fin.'),
    (r'a \.n ', 'a fin '),
    (r'super\.cie', 'superficie'),
    (r'Super\.cie', 'Superficie'),
    (r'cient[íi]\.c', 'científic'),
    (r'espec[íi]\.c', 'específic'),
    (r'signi\.c', 'signific'),
    (r'clasi\.c', 'clasific'),
    (r'cali\.c', 'calific'),
    (r'Cali\.c', 'Calific'),
    (r'veri\.c', 'verific'),
    (r'Veri\.c', 'Verific'),
    (r'identi\.c', 'identific'),
    (r'justi\.c', 'justific'),
    (r'gráfi\.c', 'gráfic'),
    (r'grá\.c', 'gráfic'),
    (r'gr[áa]\.c', 'gráfic'),
    (r'fotogr[áa]\.c', 'fotográfic'),
    (r'noti\.c', 'notific'),
    (r'modi\.c', 'modific'),
    (r'simpli\.c', 'simplific'),
    (r'plani\.c', 'planific'),
    (r'certi\.c', 'certific'),
    (r'Certi\.c', 'Certific'),
    (r'in\.uencia', 'influencia'),
    (r'in\.ación', 'inflación'),
    (r're\.eja', 'refleja'),
    (r'edi\.c', 'edific'),
    (r'\.cha', 'ficha'),
    (r'\.chas', 'fichas'),
]

for old, new in ocr_fixes:
    text = re.sub(re.escape(old) if not old.startswith('r') else old, new, text)

# Additional specific fixes
text = text.replace('.dwg', '.dwg')  # keep .dwg as is
text = text.replace('o.cio', 'oficio')
text = text.replace('O.cio', 'Oficio')
text = text.replace('o.cial', 'oficial')
text = text.replace('.eje', 'fleje')

# Fix ".n " but be careful not to break ".dwg" etc.
# We need smarter handling for remaining cases

print(f"First 200 chars: {text[:200]}")
print(f"Total: {len(text)} chars")

# Now do the structural Markdown conversion
lines = text.split('\n')

md = []
md.append("# Reglamento de Intervenciones Arqueológicas")
md.append("")
md.append("> **Tipo:** Decreto Supremo")
md.append("> **Número:** D.S. N° 011-2022-MC")
md.append("> **Fecha de publicación:** 23/11/2022")
md.append("> **Estado:** Vigente, modificado por D.S. N° 004-2025-MC (→ ver [Modificatoria RIA](ria-modificatoria-ds-004-2025-mc.md))")
md.append("")
md.append("---")
md.append("")

skip_preamble = True
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    if not line:
        if not skip_preamble:
            md.append("")
        i += 1
        continue
    
    # Skip page headers
    if line in ('El Peruano', 'NORMAS LEGALES'):
        i += 1
        continue
    
    # Detect start of the Reglamento body (after "TÍTULO PRELIMINAR")
    if 'REGLAMENTO DE INTERVENCIONES ARQUEOLÓGICAS' in line.upper() or \
       'REGLAMENTO DE INTERVENCIONES ARQUEOL' in line:
        skip_preamble = False
        i += 1
        continue
    
    if skip_preamble:
        i += 1
        continue
    
    # TÍTULO PRELIMINAR
    if 'TÍTULO PRELIMINAR' in line or 'TITULO PRELIMINAR' in line or 'TULO PRELIMINAR' in line:
        md.append("## Título Preliminar")
        md.append("")
        i += 1
        continue
    
    # TÍTULO X
    titulo_match = re.match(r'^T[ÍI]TULO\s+([IVX]+)\s*$', line, re.IGNORECASE)
    if not titulo_match:
        titulo_match = re.match(r'^T.TULO\s+([IVX]+)\s*$', line)
    if titulo_match:
        titulo_num = titulo_match.group(1)
        # Get name from next line
        name = ""
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and not re.match(r'^(CAP|ART)', next_line, re.IGNORECASE):
                name = next_line
                i += 1
        if name:
            md.append(f"## Título {titulo_num} — {name}")
        else:
            md.append(f"## Título {titulo_num}")
        md.append("")
        i += 1
        continue
    
    # CAPÍTULO X
    cap_match = re.match(r'^CAP[ÍI]TULO\s+([IVX]+)\s*$', line, re.IGNORECASE)
    if not cap_match:
        cap_match = re.match(r'^CAP.TULO\s+([IVX]+)\s*$', line)
    if cap_match:
        cap_num = cap_match.group(1)
        name = ""
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and not re.match(r'^(ART|CAP|T.T)', next_line, re.IGNORECASE):
                name = next_line
                i += 1
        if name:
            md.append(f"### Capítulo {cap_num} — {name}")
        else:
            md.append(f"### Capítulo {cap_num}")
        md.append("")
        i += 1
        continue
    
    # DISPOSICIONES headings
    if re.match(r'^DISPOSICI[OÓ]N', line, re.IGNORECASE):
        md.append(f"### {line}")
        md.append("")
        i += 1
        continue
    
    # Artículo X. (numbered or roman)
    art_match = re.match(r'^Art[íi]culo\s+(\d+|[IVX]+)[\.\-]\s*(.*)', line, re.IGNORECASE)
    if not art_match:
        art_match = re.match(r'^Art.culo\s+(\d+|[IVX]+)[\.\-]\s*(.*)', line)
    if art_match:
        art_num = art_match.group(1)
        art_title = art_match.group(2).strip()
        if art_title:
            md.append(f"#### Artículo {art_num}. {art_title}")
        else:
            md.append(f"#### Artículo {art_num}.")
        md.append("")
        i += 1
        continue
    
    # Sub-article: X.Y content
    sub_match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
    if sub_match:
        md.append(f"**{sub_match.group(1)}** {sub_match.group(2)}")
        md.append("")
        i += 1
        continue
    
    # Numbered items alone on a line
    num_alone = re.match(r'^(\d+)\.\s*$', line)
    if num_alone:
        if i + 1 < len(lines):
            next_content = lines[i+1].strip()
            if next_content:
                md.append(f"**{num_alone.group(1)}.** {next_content}")
                md.append("")
                i += 2
                continue
    
    # Letter items: a), b), etc.
    letter_match = re.match(r'^([a-zA-Z])\)\s*(.+)', line)
    if letter_match:
        md.append(f"**{letter_match.group(1)})** {letter_match.group(2)}")
        md.append("")
        i += 1
        continue
    
    # Named disposiciones
    disp_match = re.match(r'^(Primera|Segunda|Tercera|Cuarta|Quinta|Sexta|Séptima|Única)[\.\-]+\s*(.*)', line)
    if disp_match:
        md.append(f"**{disp_match.group(1)}.** {disp_match.group(2)}")
        md.append("")
        i += 1
        continue
    
    # Regular line
    md.append(line)
    md.append("")
    i += 1

# Clean up multiple blank lines
result = '\n'.join(md)
result = re.sub(r'\n{3,}', '\n\n', result)

# Write output as UTF-8
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Written {len(result)} chars to {output_path}")
print("Encoding fix complete!")
