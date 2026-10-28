from docx import Document
from docx.oxml.ns import qn
import csv
import os
from collections import defaultdict

doc_path = "E4_MERCHÁN_MONTALVÁN_JOSÉ_RAMIRO_FINAL_reducido.docx"
doc = Document(doc_path)

# Map relationship id to image
img_rels = {}
for rel_id, rel in doc.part.rels.items():
    if "image" in rel.reltype:
        img_rels[rel_id] = {
            'rel_id': rel_id,
            'target': rel.target_ref,
            'reltype': rel.reltype
        }

print(f"Total image relationships: {len(img_rels)}")

# Find which paragraphs contain drawings with images
para_to_imgs = []
for idx, p in enumerate(doc.paragraphs):
    # Look for drawing elements
    drawings = p._element.xpath('.//w:drawing')
    if drawings:
        # Find which rId is used
        for d in drawings:
            # Look for a:blip or pic:blip
            blips = d.xpath('.//a:blip')
            for blip in blips:
                embed = blip.get(qn('r:embed'))
                if not embed:
                    embed = blip.get(qn('r:link'))
                if embed:
                    para_to_imgs.append({
                        'para_idx': idx,
                        'text': p.text[:200],
                        'rId': embed,
                        'has_drawing': True
                    })
                    break
            else:
                continue
            break

print(f"Paragraphs with drawings: {len(para_to_imgs)}")

# Also look for figure captions
fig_captions = []
for idx, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t.lower().startswith('figura') or 'figura #' in t.lower():
        fig_captions.append({
            'para_idx': idx,
            'text': t
        })

print(f"Figure caption paragraphs: {len(fig_captions)}")

# Write inventory
with open('inventario_figuras.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['para_idx', 'texto_parrafo', 'rId_imagen', 'imagen_target', 'es_caption_figura', 'seccion_contexto'])
    
    # Build set of caption para indices
    caption_indices = set(c['para_idx'] for c in fig_captions)
    
    for item in para_to_imgs:
        para_idx = item['para_idx']
        # Determine section context by looking backwards
        contexto = 'OTROS'
        # Look back up to 50 paragraphs for section markers
        for j in range(para_idx, max(0, para_idx-100), -1):
            t2 = doc.paragraphs[j].text.lower()
            if 'anexo' in t2 or 'apéndice' in t2 or 'apendice' in t2:
                contexto = 'ANEXOS'
                break
            elif 'prueba' in t2 or 'test' in t2 or 'validación' in t2 or 'verificación' in t2:
                contexto = 'PRUEBAS'
                break
            elif 'prototipo' in t2:
                contexto = 'PROTOTIPO'
                break
            elif 'historia' in t2 and 'usuario' in t2:
                contexto = 'DETALLE_US'
                break
            elif 'detalle' in t2 and 'us' in t2:
                contexto = 'DETALLE_US'
                break
        
        img_target = img_rels.get(item['rId'], {}).get('target', '')
        es_caption = para_idx in caption_indices or item['text'].lower().startswith('figura')
        
        writer.writerow([
            para_idx,
            item['text'],
            item['rId'],
            img_target,
            'SI' if es_caption else 'NO',
            contexto
        ])

print("Inventory written to inventario_figuras.csv")
