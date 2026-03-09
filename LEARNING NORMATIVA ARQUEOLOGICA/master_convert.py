#!/usr/bin/env python3
"""
Master pipeline: Extract text from ALL PDFs and convert to structured Markdown.
Handles:
  1. Root folder PDFs (26 files)
  2. DS subfolder PDFs (113 Decretos Supremos)
  
Uses PyMuPDF (fitz) for text extraction when no .txt exists.
"""

import re
import sys
import os
import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'd:\PROYECTO_A_CODIGO\LEARNING NORMATIVA ARQUEOLOGICA'
MARKDOWN_DIR = os.path.join(BASE, 'MARKDOWN')
KB_DIR = os.path.join(BASE, 'knowledge_base')
DS_DIR = os.path.join(BASE, 'DS')

# ─── ENCODING & OCR FIXES ────────────────────────────────────────────
CHAR_FIXES = {
    '\x93': '"', '\x94': '"', '\x96': '–', '\x97': '—',
    '\x91': "'", '\x92': "'", '\x85': '...', '\xa0': ' ',
}

FI_FIXES = {
    'de.ne': 'define', 'de.nición': 'definición', 'De.n': 'Defin',
    'signi.c': 'signific', 'especí.c': 'específic', 'cientí.c': 'científic',
    'Certi.c': 'Certific', 'certi.c': 'certific',
    'Super.c': 'Superfic', 'super.c': 'superfic',
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

REGEX_FI = [
    (r'bibliográ\.c', 'bibliográfic'),
    (r'fotográ\.c', 'fotográfic'),
    (r'topográ\.c', 'topográfic'),
    (r'geográ\.c', 'geográfic'),
    (r'cartográ\.c', 'cartográfic'),
]


def fix_text(text):
    """Fix encoding and OCR artifacts."""
    for old, new in CHAR_FIXES.items():
        text = text.replace(old, new)
    for old, new in FI_FIXES.items():
        text = text.replace(old, new)
    for pattern, repl in REGEX_FI:
        text = re.sub(pattern, repl, text)
    return text


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return '\n'.join(text_parts)
    except Exception as e:
        return f"[ERROR extracting text: {e}]"


def read_txt_or_extract(pdf_path, txt_path=None):
    """Read existing .txt extraction or extract text from PDF."""
    if txt_path and os.path.exists(txt_path):
        with open(txt_path, 'rb') as f:
            raw = f.read()
        return raw.decode('latin-1')
    else:
        return extract_text_from_pdf(pdf_path)


def make_slug(filename):
    """Create a URL-safe slug from filename."""
    name = os.path.splitext(filename)[0]
    # Remove date prefix if present (YYYY-MM-DD -)
    name = re.sub(r'^\d{4}-\d{2}-\d{2}\s*-\s*', '', name)
    # Clean up
    slug = name.lower()
    slug = re.sub(r'[áàä]', 'a', slug)
    slug = re.sub(r'[éèë]', 'e', slug)
    slug = re.sub(r'[íìï]', 'i', slug)
    slug = re.sub(r'[óòö]', 'o', slug)
    slug = re.sub(r'[úùü]', 'u', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = slug.replace('º', '')
    slug = slug.replace('°', '')
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:80]  # cap length


def structurize_markdown(text, title, metadata_block=""):
    """Convert plain text to structured Markdown with basic headers."""
    text = fix_text(text)
    
    lines = text.split('\n')
    md = []
    
    # Add title
    md.append(f"# {title}")
    md.append("")
    if metadata_block:
        md.append(metadata_block)
        md.append("")
    md.append("---")
    md.append("")
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            md.append("")
            continue
        
        # Skip page headers
        if stripped in ('El Peruano', 'NORMAS LEGALES'):
            continue
        
        # TÍTULO
        if re.match(r'^T[ÍIUÚ]TULO\s+', stripped, re.IGNORECASE):
            md.append(f"## {stripped}")
            md.append("")
            continue
        
        # CAPÍTULO
        if re.match(r'^CAP[ÍIÚU]TULO\s+', stripped, re.IGNORECASE):
            md.append(f"### {stripped}")
            md.append("")
            continue
        
        # DISPOSICIÓN
        if re.match(r'^DISPOSICI', stripped, re.IGNORECASE):
            md.append(f"### {stripped}")
            md.append("")
            continue
        
        # Artículo
        if re.match(r'^Art[íi]culo\s+\d', stripped, re.IGNORECASE):
            md.append(f"#### {stripped}")
            md.append("")
            continue
        
        # Regular text
        md.append(stripped)
        md.append("")
    
    result = '\n'.join(md)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


def extract_ds_metadata(filename):
    """Extract metadata from a DS filename like '2022-11-23 - D.S. 011-2022-MC - ...'"""
    # Pattern: YYYY-MM-DD - D.S. NNN-YYYY-MC - Description
    match = re.match(r'(\d{4}-\d{2}-\d{2})\s*-\s*(D\.S\.?\s*\d+[-/]\d{4}-MC)\s*-\s*(.+?)\.pdf$', filename, re.IGNORECASE)
    if match:
        fecha = match.group(1)
        numero = match.group(2).strip()
        descripcion = match.group(3).strip()
        return {
            'fecha': fecha,
            'numero': numero,
            'titulo': descripcion,
            'year': fecha[:4],
        }
    # Fallback: just use the filename
    name = os.path.splitext(filename)[0]
    year_match = re.match(r'(\d{4})', name)
    year = year_match.group(1) if year_match else 'otros'
    return {
        'fecha': year,
        'numero': name[:50],
        'titulo': name,
        'year': year,
    }


def process_root_pdfs():
    """Process all root folder PDFs."""
    print("\n" + "="*60)
    print("PHASE 1: ROOT PDFS")
    print("="*60)
    
    # Already converted files (skip these)
    already_converted = {
        'RIA 2022.pdf': 'normativa-general/ria-ds-011-2022-mc.md',
        'Modificatoria del RIA.pdf': 'normativa-general/ria-modificatoria-ds-004-2025-mc.md',
        'LEY Nº 28296 Ley General del Patrimonio Cultural de la Nación.doc.pdf': 'normativa-general/ley-28296-patrimonio-cultural.md',
        'TUPA 2025.pdf': 'normativa-general/tupa-2025-ministerio-cultura.md',
        'RIA 2025.pdf': 'normativa-general/ria-2025-consolidado.md',
        'Normas_Legales_20200808.indd.pdf': 'normativa-general/reglamento-ley-28296-modificatoria-2020.md',
        'Guía para la expedición del CIRAS.pdf': 'ciras/guia-expedicion-ciras.md',
        'PEA .pdf': 'pea/formatos-pea-pra.md',
        'GUIA DE EXCAVACIÓN.pdf': 'complementaria/guia-excavacion-rvm-063-2021.md',
        'Guia para la Entrega de Bienes Culturales Muebles-RV N 00171-2020-VMPCIC.pdf.pdf': 'complementaria/guia-entrega-bienes-culturales.md',
        'DS_014-92-EM.pdf': 'complementaria/ds-014-92-em-reglamento-mineria.md',
        '6302533-rm-000439-2024-mc-anexo-1.pdf': 'complementaria/rm-000439-2024-mc-formatos.md',
        'RESOLUCION DIRECTORAL-001081-2025-DE-DDC-CUS.pdf': 'complementaria/rd-001081-2025-ddc-cusco.md',
    }
    
    # New root PDFs to convert
    new_root = {
        '208458_rm282.pdf20181203-3039-3ppemu.pdf': {
            'txt': '208458_rm282.pdf20181203-3039-3ppemu.txt',
            'dest': 'complementaria/rm-282-2018-mc-proma.md',
            'title': 'Resolución Ministerial N° 282-2018-MC — PROMA',
            'meta': '> **Tipo:** Resolución Ministerial\n> **Número:** R.M. N° 282-2018-MC\n> **Fecha:** 2018\n> **Estado:** Vigente',
        },
        'DS N° 004-2025-MC.pdf': {
            'txt': 'DS N° 004-2025-MC.txt',
            'dest': 'normativa-general/ds-004-2025-mc-modificatoria-ria.md',
            'title': 'Decreto Supremo N° 004-2025-MC — Modificatoria del RIA',
            'meta': '> **Tipo:** Decreto Supremo\n> **Número:** D.S. N° 004-2025-MC\n> **Fecha:** 12/03/2025\n> **Estado:** Vigente',
        },
        'RVM 063-2021-VMPCIC-MC - ANEXO.pdf.pdf': {
            'txt': 'RVM 063-2021-VMPCIC-MC - ANEXO.pdf.txt',
            'dest': 'complementaria/rvm-063-2021-anexo.md',
            'title': 'RVM N° 063-2021-VMPCIC-MC — Anexo (Guía de Excavación)',
            'meta': '> **Tipo:** Resolución Viceministerial (Anexo)\n> **Número:** RVM N° 063-2021-VMPCIC-MC\n> **Fecha:** 2021\n> **Estado:** Vigente',
        },
        'Lima, 02 de Diciembre de 2004.pdf': {
            'txt': 'Lima, 02 de Diciembre de 2004.txt',
            'dest': 'complementaria/reglamento-ley-28296-ds-011-2006-ed.md',
            'title': 'Reglamento de la Ley N° 28296 — D.S. N° 011-2006-ED',
            'meta': '> **Tipo:** Decreto Supremo\n> **Número:** D.S. N° 011-2006-ED\n> **Fecha:** 02/12/2004\n> **Estado:** Vigente — con modificatorias',
        },
        'N° 012-2024-PRODUCE.pdf': {
            'txt': 'N° 012-2024-PRODUCE.txt',
            'dest': 'complementaria/ds-012-2024-produce.md',
            'title': 'Decreto Supremo N° 012-2024-PRODUCE',
            'meta': '> **Tipo:** Decreto Supremo\n> **Número:** D.S. N° 012-2024-PRODUCE\n> **Fecha:** 2024\n> **Estado:** Vigente',
        },
        'Publicacion Oficial - Diario Oficial El Peruano.pdf': {
            'txt': 'Publicacion Oficial - Diario Oficial El Peruano.txt',
            'dest': 'complementaria/publicacion-oficial-diario-peruano.md',
            'title': 'Publicación Oficial — Diario Oficial El Peruano',
            'meta': '> **Tipo:** Publicación Oficial\n> **Número:** Diario Oficial\n> **Fecha:** —\n> **Estado:** Vigente',
        },
        # PDFs without txt extraction - will be extracted with PyMuPDF
        '2014-12-22 (13).pdf': {
            'txt': None,
            'dest': 'complementaria/norma-2014-12-22.md',
            'title': 'Norma del 22 de Diciembre de 2014',
            'meta': '> **Tipo:** Norma Legal\n> **Fecha:** 22/12/2014\n> **Estado:** Vigente',
        },
        'EVALUACION DE MUSEOS.pdf': {
            'txt': None,
            'dest': 'complementaria/evaluacion-museos.md',
            'title': 'Evaluación de Museos',
            'meta': '> **Tipo:** Guía/Normativa\n> **Estado:** Vigente',
        },
        'FICHA TÉCNICA PARA DECLARATORIA COMO PATRIMONIO CULTURAL DE LA NACIÓN.pdf': {
            'txt': None,
            'dest': 'complementaria/ficha-tecnica-declaratoria-patrimonio.md',
            'title': 'Ficha Técnica para Declaratoria como Patrimonio Cultural de la Nación',
            'meta': '> **Tipo:** Ficha Técnica\n> **Estado:** Vigente',
        },
        'Guía de identificación y registro del Qhapaq Ñan.pdf': {
            'txt': None,
            'dest': 'complementaria/guia-identificacion-qhapaq-nan.md',
            'title': 'Guía de Identificación y Registro del Qhapaq Ñan',
            'meta': '> **Tipo:** Guía Técnica\n> **Estado:** Vigente',
        },
        'IDENTIFICACIÓN DEL IMPACTO AL PATRIMONIO CULTURAL - IIPC.pdf': {
            'txt': None,
            'dest': 'complementaria/identificacion-impacto-patrimonio-iipc.md',
            'title': 'Identificación del Impacto al Patrimonio Cultural — IIPC',
            'meta': '> **Tipo:** Guía Técnica\n> **Estado:** Vigente',
        },
        'REGLAMENTO DE EDIFICACIONES.pdf': {
            'txt': None,
            'dest': 'complementaria/reglamento-edificaciones.md',
            'title': 'Reglamento de Edificaciones',
            'meta': '> **Tipo:** Reglamento\n> **Estado:** Vigente',
        },
        'TUO-27444-PROCED-ADMINISTRA-Final.pdf': {
            'txt': None,
            'dest': 'normativa-general/tuo-ley-27444-procedimiento-administrativo.md',
            'title': 'TUO de la Ley N° 27444 — Ley del Procedimiento Administrativo General',
            'meta': '> **Tipo:** Decreto Supremo (TUO)\n> **Número:** D.S. N° 004-2019-JUS\n> **Estado:** Vigente',
        },
    }
    
    converted = 0
    total_chars = 0
    
    for pdf_name, info in new_root.items():
        pdf_path = os.path.join(BASE, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"  ❌ NOT FOUND: {pdf_name}")
            continue
        
        dest_path = os.path.join(KB_DIR, info['dest'])
        
        # Read text from txt or extract from PDF
        txt_path = os.path.join(MARKDOWN_DIR, info['txt']) if info['txt'] else None
        text = read_txt_or_extract(pdf_path, txt_path)
        
        if not text or len(text) < 50:
            print(f"  ⚠️  EMPTY/SHORT: {pdf_name}")
            continue
        
        result = structurize_markdown(text, info['title'], info['meta'])
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        converted += 1
        total_chars += len(result)
        print(f"  ✅ {os.path.basename(dest_path)}: {len(result):,} chars")
    
    print(f"\n  Root PDFs: {converted} converted, {total_chars:,} chars")
    return converted, total_chars


def process_ds_pdfs():
    """Process all DS subfolder PDFs."""
    print("\n" + "="*60)
    print("PHASE 2: DS SUBFOLDER (113 DECRETOS SUPREMOS)")
    print("="*60)
    
    ds_pdfs = sorted([f for f in os.listdir(DS_DIR) if f.lower().endswith('.pdf')])
    
    converted = 0
    total_chars = 0
    errors = []
    
    for pdf_name in ds_pdfs:
        pdf_path = os.path.join(DS_DIR, pdf_name)
        meta = extract_ds_metadata(pdf_name)
        year = meta['year']
        slug = make_slug(pdf_name)
        
        # Create year subfolder
        dest_dir = os.path.join(KB_DIR, 'decretos-supremos', year)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, f"{slug}.md")
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        if not text or len(text) < 50:
            errors.append(pdf_name)
            print(f"  ⚠️  EMPTY: {pdf_name}")
            continue
        
        metadata_block = (
            f"> **Tipo:** Decreto Supremo\n"
            f"> **Número:** {meta['numero']}\n"
            f"> **Fecha:** {meta['fecha']}\n"
            f"> **Estado:** Vigente"
        )
        
        result = structurize_markdown(text, meta['titulo'], metadata_block)
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        converted += 1
        total_chars += len(result)
        
        if converted % 10 == 0:
            print(f"  ... {converted}/{len(ds_pdfs)} processed")
    
    print(f"\n  DS PDFs: {converted}/{len(ds_pdfs)} converted, {total_chars:,} chars")
    if errors:
        print(f"  ⚠️  {len(errors)} files with extraction issues")
    
    return converted, total_chars


def main():
    print("=" * 60)
    print("MASTER PIPELINE: ALL PDFs → MARKDOWN KNOWLEDGE BASE")
    print("=" * 60)
    
    root_count, root_chars = process_root_pdfs()
    ds_count, ds_chars = process_ds_pdfs()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"  Root PDFs converted: {root_count}")
    print(f"  DS PDFs converted:   {ds_count}")
    print(f"  Total new files:     {root_count + ds_count}")
    print(f"  Total chars written: {root_chars + ds_chars:,}")
    print("=" * 60)


if __name__ == '__main__':
    main()
