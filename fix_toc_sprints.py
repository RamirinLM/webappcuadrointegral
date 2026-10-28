"""
Fix TOC entries: replace 5 old combined sprint entries (Sprint 1-2, 3-4, etc.)
with 14 individual sprint entries in the DOCX TOC section (TDC2 style).
"""
import zipfile, os, copy, shutil
from lxml import etree

basedir = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral'

# Find the FINAL file
final = None
for f in os.listdir(basedir):
    if 'FINAL' in f and f.endswith('.docx') and 'PREVIOUS' not in f:
        final = os.path.join(basedir, f)
        break

if not final:
    print("FINAL file not found!")
    exit(1)

print(f"Processing: {os.path.basename(final)}")
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# Read the DOCX
with zipfile.ZipFile(final, 'r') as z:
    doc_xml = z.read('word/document.xml')
    tree = etree.fromstring(doc_xml)
    body = tree.find(f'{{{W}}}body')
    
    # Sprint titles matching the actual sprint section headings
    sprint_entries = [
        ("3.13.1",  "Sprint 1: Módulo de Gestión de Proyectos - Parte 1 (E1)", "121"),
        ("3.13.2",  "Sprint 2: Módulo de Gestión de Proyectos - Parte 2 (E1)", "121"),
        ("3.13.3",  "Sprint 3: Módulo de Planificación y Control - Parte 1 (E2)", "123"),
        ("3.13.4",  "Sprint 4: Módulo de Planificación y Control - Parte 2 (E2)", "123"),
        ("3.13.5",  "Sprint 5: Módulo de Gestión de Recursos y Costos - Parte 1 (E3)", "126"),
        ("3.13.6",  "Sprint 6: Módulo de Gestión de Recursos y Costos - Parte 2 (E3)", "126"),
        ("3.13.7",  "Sprint 7: Módulo de Seguimiento y Monitoreo - Parte 1 (E4)", "129"),
        ("3.13.8",  "Sprint 8: Módulo de Seguimiento y Monitoreo - Parte 2 (E4)", "129"),
        ("3.13.9",  "Sprint 9: Módulo de Generación de Informes y Análisis - Parte 1 (E5)", "129"),
        ("3.13.10", "Sprint 10: Módulo de Generación de Informes y Análisis - Parte 2 (E5)", "129"),
        ("3.13.11", "Sprint 11: Módulo de Comunicación y Gestión de Stakeholders - Parte 1 (E6)", "130"),
        ("3.13.12", "Sprint 12: Módulo de Comunicación y Gestión de Stakeholders - Parte 2 (E6)", "130"),
        ("3.13.13", "Sprint 13: Módulo de Gestión de Cambios y Control de Versiones - Parte 1 (E7)", "130"),
        ("3.13.14", "Sprint 14: Módulo de Gestión de Cambios y Control de Versiones - Parte 2 (E7)", "131"),
    ]
    
    # Find old TOC entries - search all body children for paragraphs with TDC2 style
    # and "Sprint X - Y" text (old combined format)
    old_paras = []  # (index_in_body, element, text)
    children_to_remove = []
    
    for i, child in enumerate(body):
        if child.tag != f'{{{W}}}p':
            continue
        # Check style
        pPr = child.find(f'{{{W}}}pPr')
        if pPr is None:
            continue
        pStyle = pPr.find(f'{{{W}}}pStyle')
        if pStyle is None or pStyle.get(f'{{{W}}}val') != 'TDC2':
            continue
        # Check text for combined sprint format
        texts = child.findall(f'.//{{{W}}}t')
        text = ''.join(t.text or '' for t in texts)
        # Match "Sprint X - Y" or "Sprint X – Y" patterns
        import re
        if re.search(r'Sprint \d+\s*[–-]\s*\d+', text):
            old_paras.append((i, child, text))
            children_to_remove.append(child)
    
    print(f"Found {len(old_paras)} old combined TOC entries to remove:")
    for idx, el, txt in old_paras:
        print(f"  Body child {idx}: '{txt[:80]}'")
    
    if not old_paras:
        print("ERROR: No old combined TOC entries found!")
        exit(1)
    
    # Get insertion point: the index of the first old entry
    first_idx = old_paras[0][0]
    
    # Remove old entries (in reverse to avoid index shifting)
    for el in reversed(children_to_remove):
        body.remove(el)
    
    # Create a template from a TDC2 paragraph that still exists
    # Find any remaining TDC2 paragraph to use as template
    template = None
    for child in body:
        if child.tag == f'{{{W}}}p':
            pPr = child.find(f'{{{W}}}pPr')
            if pPr is not None:
                pStyle = pPr.find(f'{{{W}}}pStyle')
                if pStyle is not None and pStyle.get(f'{{{W}}}val') == 'TDC2':
                    # Find the hyperlink structure
                    hyperlink = child.find(f'{{{W}}}hyperlink')
                    if hyperlink is not None:
                        template = child
                        break
    
    if template is None:
        print("ERROR: Could not find a TDC2 template paragraph!")
        exit(1)
    
    print(f"\nUsing template: '{''.join(t.text or '' for t in template.findall(f'.//{{{W}}}t'))[:60]}'")
    
    # Create prefix for anchor IDs
    # Find existing anchor IDs to avoid conflicts
    existing_anchors = set()
    for child in body:
        for hl in child.findall(f'.//{{{W}}}hyperlink'):
            anchor = hl.get(f'{{{W}}}anchor')
            if anchor:
                existing_anchors.add(anchor)
    
    # Create 14 new paragraph elements
    new_paras = []
    base_anchor_num = 221093600
    
    for i, (num, title, page) in enumerate(sprint_entries):
        # Deep copy the template
        new_p = copy.deepcopy(template)
        
        # Find hyperlink and update anchor
        hyperlink = new_p.find(f'{{{W}}}hyperlink')
        
        # Generate unique anchor
        anchor = f"_Toc{base_anchor_num + i}"
        while anchor in existing_anchors:
            base_anchor_num += 100
            anchor = f"_Toc{base_anchor_num + i}"
        existing_anchors.add(anchor)
        hyperlink.set(f'{{{W}}}anchor', anchor)
        
        # Find all runs within hyperlink
        runs = hyperlink.findall(f'{{{W}}}r')
        
        # Find the text elements and update them
        # Pattern: run[0] has numbering, run[2] has title, 
        # runs with fldChar contain page number
        
        for run_idx, run in enumerate(runs):
            # Update numbering (first t element that looks like "3.13.X")
            t_els = run.findall(f'{{{W}}}t')
            for t_el in t_els:
                if t_el.text and re.match(r'3\.\d+\.\d+', t_el.text.strip()):
                    old_num = t_el.text.strip()
                    t_el.text = num
                    # Preserve any suffix (like if there was a space after)
                    if t_el.tail:
                        pass  # keep tail
                    break
            
            # Update title (t element that starts with "Sprint")
            for t_el in t_els:
                if t_el.text and t_el.text.strip().startswith('Sprint'):
                    old_title = t_el.text.strip()
                    t_el.text = title
                    break
            
            # Update PAGEREF instruction
            instr = run.find(f'{{{W}}}instrText')
            if instr is not None and instr.text and 'PAGEREF' in instr.text:
                instr.text = f' PAGEREF {anchor} \\h '
            
            # Update page number text (the fldChar separate run's text)
            fldChar = run.find(f'{{{W}}}fldChar')
            if fldChar is not None:
                fc_type = fldChar.get(f'{{{W}}}fldCharType')
                if fc_type == 'separate':
                    # The page number should be in a t element in this or next run
                    for t_el in t_els:
                        if t_el.text and t_el.text.strip().isdigit():
                            t_el.text = page
                            break
        
        new_paras.append(new_p)
    
    # Insert new paragraphs at the first old entry's position
    # We need to find the reference element to insert before
    # After removing old entries, find what's at the insertion point
    body_children = list(body)
    
    # Find the element that was at position first_idx before removal
    # Since we removed children_to_remove, we need to find the element
    # that now occupies that position
    insert_pos = first_idx
    remaining = [c for c in body if c.tag == f'{{{W}}}p']
    
    # Find a reference element: the first paragraph at or after the old position
    ref_elem = None
    current_idx = 0
    for child in body:
        if child.tag == f'{{{W}}}p':
            if current_idx >= first_idx:
                ref_elem = child
                break
            current_idx += 1
    
    if ref_elem is None:
        # If nothing left, just append
        for p in new_paras:
            body.append(p)
        print("Appended all new entries at end of body.")
    else:
        # Insert before the reference element (in reverse order to maintain sequence)
        for p in reversed(new_paras):
            body.insert(list(body).index(ref_elem), p)
        print(f"Inserted 14 new entries before '{''.join(t.text or '' for t in ref_elem.findall(f'.//{{{W}}}t'))[:50]}'")
    
    # Verify
    all_paras = [c for c in body if c.tag == f'{{{W}}}p']
    
    # Count new style entries
    new_count = 0
    for p in all_paras:
        texts = p.findall(f'.//{{{W}}}t')
        text = ''.join(t.text or '' for t in texts)
        if 'Sprint' in text and re.search(r'Sprint \d+:', text) and 'Parte' in text:
            new_count += 1
    
    print(f"\nVerification: Found {new_count} individual sprint TOC entries (expected: 14)")
    
    old_remaining = 0
    for p in all_paras:
        texts = p.findall(f'.//{{{W}}}t')
        text = ''.join(t.text or '' for t in texts)
        if re.search(r'Sprint \d+\s*[–-]\s*\d+', text):
            old_remaining += 1
    
    print(f"Old combined entries remaining: {old_remaining} (expected: 0)")
    
    # Serialize and write back
    doc_bytes = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    
    # Write to a temp file first, then replace
    tmp_final = final + '.tmp'
    with zipfile.ZipFile(final, 'r') as zin:
        with zipfile.ZipFile(tmp_final, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, doc_bytes)
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    # Replace original
    shutil.move(tmp_final, final)
    print(f"\n✅ Document updated: {os.path.basename(final)} ({os.path.getsize(final)} bytes)")

print("\nDone!")
