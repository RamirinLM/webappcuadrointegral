#!/usr/bin/env python3
"""
Correcciones restantes post-v2:
  1. Contexto narrativo para figuras en Sprints (next paragraph suele estar vacío)
  2. Figura #17 remanentes en el índice
  3. Objetivos de sprints con referencias a pares
  4. Page break para Capítulo cuatro (con dos puntos en el texto)
"""
import os, re
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral'
INPUT = None
for f in os.listdir(BASE):
    if 'FINAL' in f and f.endswith('.docx') and 'PREVIOUS' not in f:
        INPUT = os.path.join(BASE, f)
        break
print(f"📄 {os.path.basename(INPUT)}")

doc = Document(INPUT)
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def make_pb():
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    r = OxmlElement('w:r')
    br = OxmlElement('w:br')
    br.set(qn('w:type'), 'page')
    r.append(br)
    p.append(pPr)
    p.append(r)
    return p

# ==============================================================
# 1. PAGE BREAK for Capítulo cuatro
# ==============================================================
print("\n[1] Page break para 'Capítulo cuatro: Evaluación y resultados'...")
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if p.style.name == 'Heading 1' and 'Capítulo cuatro' in text:
        # Check if there's already a page break before it
        prev_element = p._element.getprevious()
        has_pb = False
        if prev_element is not None:
            for br in prev_element.iter():
                if br.tag == f'{{{W}}}br' and br.get(qn('w:type')) == 'page':
                    has_pb = True
                    break
        if not has_pb:
            pb = make_pb()
            p._element.addprevious(pb)
            print(f"   ✅ Page break antes de: '{text}'")
        else:
            print(f"   ⚠️  Ya tiene page break")
        break

# ==============================================================  
# 2. FIX REMAINING Figura #17 entries (checking p.text vs runs)
# ==============================================================
print("\n[2] Corrigiendo entradas 'Figura #17' remanentes...")

fig17_remaining = []
for p in doc.paragraphs:
    if 'Figura #17' in p.text:
        fig17_remaining.append(p)

print(f"   Encontradas {len(fig17_remaining)} entradas con 'Figura #17'")

# Assign corrected numbers starting from 51 for remaining index entries
fig_counter = 50
fixed_count = 0

for p in fig17_remaining:
    old_text = p.text
    fig_counter += 1
    new_text = old_text.replace('Figura #17', f'Figura #{fig_counter}', 1)
    
    # Need to modify the actual XML runs - for TOC entries the text is split in hyperlinks
    # Let's check if there's a hyperlink structure
    hyperlinks = p._element.findall(f'.//{{{W}}}hyperlink')
    runs = p._element.findall(f'.//{{{W}}}r')
    
    if hyperlinks:
        # TOC entry - modify within hyperlinks
        for hl in hyperlinks:
            for r in hl.findall(f'.//{{{W}}}r'):
                t = r.find(f'{{{W}}}t')
                if t is not None and 'Figura #17' in (t.text or ''):
                    t.text = t.text.replace('Figura #17', f'Figura #{fig_counter}')
                    fixed_count += 1
    elif runs:
        for r in runs:
            t = r.find(f'{{{W}}}t')
            if t is not None and 'Figura #17' in (t.text or ''):
                t.text = t.text.replace('Figura #17', f'Figura #{fig_counter}')
                fixed_count += 1
    
    if old_text != new_text:
        pass  # tracking

print(f"   → {fixed_count} correcciones aplicadas")

# ==============================================================
# 3. FIX SPRINT OBJECTIVES
# ==============================================================
print("\n[3] Corrigiendo objetivos de sprints con referencias a pares...")

# Find all "Objetivo" paragraphs (Estilo2) and check their text + next paragraph
fixed_objs = 0
for i, p in enumerate(doc.paragraphs):
    if p.style.name != 'Estilo2':
        continue
    text = p.text.strip()
    
    # Check current paragraph text
    overall_text = text
    
    # Also check the NEXT normal paragraph (the actual objective text)
    next_text = ''
    for j in range(i+1, min(i+3, len(doc.paragraphs))):
        p2 = doc.paragraphs[j]
        if p2.style.name == 'Normal' and p2.text.strip():
            next_text = p2.text.strip()
            break
    
    combined = overall_text + ' ' + next_text
    
    # Check for sprint pair references
    if re.search(r'sprints?\s+\d+\s+y\s+\d+', combined, re.IGNORECASE):
        # Determine sprint context from previous headings
        prev_sprint_num = None
        for j in range(i-1, max(i-20, 0), -1):
            prev = doc.paragraphs[j]
            if prev.style.name == 'Estilo2':
                sm = re.match(r'Sprint\s+(\d+):', prev.text.strip())
                if sm:
                    prev_sprint_num = int(sm.group(1))
                    break
        
        if prev_sprint_num and prev_sprint_num % 2 == 1:
            # Fix the next paragraph text
            p_to_fix = None
            for j in range(i+1, min(i+3, len(doc.paragraphs))):
                p2 = doc.paragraphs[j]
                if p2.style.name == 'Normal' and p2.text.strip():
                    p_to_fix = p2
                    break
            
            if p_to_fix is not None:
                old = p_to_fix.text
                replacements = [
                    (rf'Los sprints {prev_sprint_num} y {prev_sprint_num+1} tuvieron como objetivo',
                     f'El Sprint {prev_sprint_num} tuvo como objetivo'),
                    (rf'Los sprints {prev_sprint_num} y {prev_sprint_num+1} se enfocaron',
                     f'El Sprint {prev_sprint_num} se enfocó'),
                    (rf'Los sprints {prev_sprint_num} y {prev_sprint_num+1} implementaron',
                     f'El Sprint {prev_sprint_num} implementó'),
                    (rf'sprints {prev_sprint_num} y {prev_sprint_num+1}',
                     f'Sprint {prev_sprint_num}'),
                ]
                new = old
                for pat, repl in replacements:
                    new = re.sub(pat, repl, new, flags=re.IGNORECASE)
                
                if new != old:
                    # Apply to runs
                    for run in p_to_fix.runs:
                        run_new = run.text
                        for pat, repl in replacements:
                            run_new = re.sub(pat, repl, run_new, flags=re.IGNORECASE)
                        if run_new != run.text:
                            run.text = run_new
                    
                    fixed_objs += 1
                    print(f"   ✅ Sprint {prev_sprint_num}: '{old[:60]}...' → '{new[:60]}...'")

print(f"   → {fixed_objs} objetivos corregidos")

# ==============================================================
# 4. ADD NARRATIVE CONTEXT BEFORE IMAGES IN SPRINT SECTIONS
# ==============================================================
print("\n[4] Agregando contexto narrativo a figuras en Sprints...")

context_added = 0
for i, p in enumerate(doc.paragraphs):
    if p.style.name == 'table of figures' and 'Figura' in p.text:
        fig_match = re.search(r'(?:Figura|Ilustración)\s*#?(\d+)', p.text)
        if not fig_match:
            continue
        fig_num = fig_match.group(1)
        caption = p.text.strip()
        
        # Check the next non-empty paragraph(s) after this one
        # Skip empty paragraphs (often the image is between caption and text)
        target_p = None
        target_idx = -1
        
        for j in range(i+1, min(i+8, len(doc.paragraphs))):
            p2 = doc.paragraphs[j]
            text2 = p2.text.strip()
            style2 = p2.style.name
            
            # Skip table of figures (another caption), empty paragraphs
            if style2 == 'table of figures' or not text2:
                continue
            if style2 in ('Caption', 'Estilo2', 'Heading 1'):
                break  # Hit a different section, bad
            
            # Found a target
            if style2 in ('Normal', 'List Paragraph') and text2:
                # Check if already has context
                if any(w in text2.lower() for w in ['la figura', 'la imagen', 'se observa', 'se muestra', 'se presenta', 'el fragmento', 'nota:', 'en la figura']):
                    break  # Has context already, skip
                target_p = p2
                target_idx = j
                break
        
        if target_p is not None:
            # Prepend context text
            old_text = target_p.text
            context_prefix = f"En la Figura #{fig_num} se observa "
            new_text = context_prefix + old_text[0].lower() + old_text[1:] if len(old_text) > 1 else context_prefix + old_text
            
            for run in target_p.runs:
                if run.text == old_text or run.text.strip():
                    run.text = new_text
                    context_added += 1
                    break

print(f"   → {context_added} contextos agregados en sprints")

# ==============================================================  
# SAVE
# ==============================================================
doc.save(INPUT)
print(f"\n✅ Guardado: {os.path.basename(INPUT)} ({os.path.getsize(INPUT)} bytes)")

# ── VERIFY ──────────────────────────────────────────────────
doc2 = Document(INPUT)
pb_count = 0
for el in doc2.element.body.iter():
    if el.tag == f'{{{W}}}br' and el.get(qn('w:type')) == 'page':
        pb_count += 1
fig17_count = sum(1 for p in doc2.paragraphs if 'Figura #17' in p.text)
context_count = sum(1 for p in doc2.paragraphs if 'se observa' in p.text.lower() or 'se muestra' in p.text.lower())

print(f"\n📊 Page breaks: {pb_count}")
print(f"📊 'Figura #17' restantes: {fig17_count}")
print(f"📊 Contextos narrativos: {context_count}")
print(f"📊 Párrafos: {len(doc2.paragraphs)}")
