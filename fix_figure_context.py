#!/usr/bin/env python3
"""
CORRECCIÓN v3b — Agrega contexto narrativo a figuras del cuerpo del documento.
Las figuras del cuerpo usan estilos 'Tabladeilustraciones' y 'Descripcin',
mientras que las del índice usan 'table of figures'.

Estructura típica en el cuerpo:
  [Caption] style=Tabladeilustraciones  "Figura #25 Fragmento de código..."
  [Image]   style=Normal                (drawing element)
  [Note?]   style=Normal                "Nota: ..."
"""
import os, re
from docx import Document
from docx.oxml.ns import qn

BASE = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral'
INPUT = None
for f in os.listdir(BASE):
    if 'FINAL' in f and f.endswith('.docx') and 'PREVIOUS' not in f and 'BACKUP' not in f and not f.startswith('~'):
        INPUT = os.path.join(BASE, f)
        break

print(f"📄 Documento: {os.path.basename(INPUT)}")

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def get_text(el):
    return ''.join(t.text or '' for t in el.findall(f'.//{{{W}}}t')).strip()

def get_style(el):
    ppr = el.find(f'{{{W}}}pPr')
    if ppr is not None:
        ps = ppr.find(f'{{{W}}}pStyle')
        if ps is not None:
            return ps.get(qn('w:val'))
    return None

def make_para(text, style='Normal'):
    from docx.oxml import OxmlElement
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style)
    pPr.append(pStyle)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
    return p

doc = Document(INPUT)
body = doc.element.body
children = list(body)

# Find figure captions in BODY (not index) that need context
# Styles: 'Tabladeilustraciones', 'Descripcin', or None with 'Figura #N' text
BODY_CAPTION_STYLES = ('Tabladeilustraciones', 'Descripcin')

context_added = 0
figures_processed = 0

for i, child in enumerate(children):
    if child.tag != f'{{{W}}}p':
        continue
    
    style = get_style(child)
    text = get_text(child)
    
    # Must be a figure caption in the body (after index section, para ~430+)
    if i < 430:
        continue
    
    is_caption = (
        (style in BODY_CAPTION_STYLES and 'Figura' in text and '#' in text) or
        (style == 'table of figures' and 'Figura' in text and '#' in text and i > 900)
    )
    
    if not is_caption:
        continue
    
    figures_processed += 1
    
    # Extract figure number and description
    fig_match = re.search(r'Figura\s*#?(\d+)\s+(.*)', text)
    if not fig_match:
        continue
    fig_num = fig_match.group(1)
    fig_desc = fig_match.group(2).strip()
    
    # Check if context already exists BEFORE this caption
    has_context_before = False
    if i > 0:
        # Walk backwards through nearby paragraphs (skip empty ones)
        for j in range(i-1, max(i-5, 0), -1):
            prev = children[j]
            if prev.tag != f'{{{W}}}p':
                continue
            prev_text = get_text(prev)
            if not prev_text:
                continue
            prev_lower = prev_text.lower()
            if any(w in prev_lower for w in ['en la figura', 'la imagen', 'se observa', 'se muestra', 'se presenta', 'el siguiente código', 'a continuación']):
                has_context_before = True
                break
            # If we hit non-empty text that's not context, stop
            break
    
    # Check if context exists AFTER the image (which is after the caption)
    has_context_after = False
    if i + 2 < len(children):
        for j in range(i+1, min(i+5, len(children))):
            next_p = children[j]
            if next_p.tag != f'{{{W}}}p':
                continue
            next_text = get_text(next_p)
            if not next_text:
                continue
            next_lower = next_text.lower()
            if any(w in next_lower for w in ['en la figura', 'la imagen', 'se observa', 'se muestra', 'se presenta', 'nota:']):
                has_context_after = True
                break
            break
    
    if has_context_before or has_context_after:
        continue
    
    # Determine if it's code or interface
    desc_lower = fig_desc.lower()
    is_code = any(w in desc_lower for w in ['código', 'fragmento', 'modelo', 'clase'])
    
    # Generate context paragraph
    if is_code:
        context = f"En la Figura #{fig_num} se presenta el siguiente fragmento de código que implementa {fig_desc.lower()}. Esta implementación forma parte del sistema de gestión de proyectos del GAD Municipal de Célica:"
    else:
        context = f"En la Figura #{fig_num} se observa {fig_desc.lower()}, correspondiente a la interfaz del sistema de gestión de proyectos del GAD Municipal de Célica:"
    
    # Insert context BEFORE the caption
    new_p = make_para(context, 'Normal')
    child.addprevious(new_p)
    context_added += 1

print(f"   Figuras procesadas: {figures_processed}")
print(f"   Contextos agregados: {context_added}")

doc.save(INPUT)
print(f"   ✅ Documento guardado ({os.path.getsize(INPUT)} bytes)")

# Verify
doc2 = Document(INPUT)
ctx_count = 0
for p in doc2.paragraphs:
    txt = p.text.lower()
    if any(w in txt for w in ['en la figura', 'se observa', 'se muestra', 'se presenta', 'a continuación, la tabla']):
        ctx_count += 1
print(f"\n📊 Total contextos narrativos en documento: {ctx_count}")
