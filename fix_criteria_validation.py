#!/usr/bin/env python3
"""
FIX v3c — Move criteria validation from TOC to body.
The previous script inserted "A continuación se presenta la validación..." 
before TOC entries (style=toc 2) instead of body entries (style=Normal).
This script:
1. Removes the misplaced criteria paragraphs from TOC area
2. Re-inserts them in the body before each Registro de Pruebas section
"""
import os, re
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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

def make_para(text, style='Normal'):
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

def make_table(headers, rows):
    tbl = OxmlElement('w:tbl')
    tblPr = OxmlElement('w:tblPr')
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')
    tblW.set(qn('w:type'), 'pct')
    tblPr.append(tblW)
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000')
        tblBorders.append(border)
    tblPr.append(tblBorders)
    tbl.append(tblPr)
    tblGrid = OxmlElement('w:tblGrid')
    for _ in headers:
        gridCol = OxmlElement('w:gridCol')
        gridCol.set(qn('w:w'), str(5000 // len(headers)))
        tblGrid.append(gridCol)
    tbl.append(tblGrid)
    # Header row
    tr = OxmlElement('w:tr')
    for h in headers:
        tc = OxmlElement('w:tc')
        tcPr = OxmlElement('w:tcPr')
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '2E75B6')
        tcPr.append(shd)
        tc.append(tcPr)
        p = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        p.append(pPr)
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        b = OxmlElement('w:b')
        color_el = OxmlElement('w:color')
        color_el.set(qn('w:val'), 'FFFFFF')
        rPr.append(b)
        rPr.append(color_el)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = h
        r.append(t)
        p.append(r)
        tc.append(p)
        tr.append(tc)
    tbl.append(tr)
    for row in rows:
        tr = OxmlElement('w:tr')
        for cell in row:
            tc = OxmlElement('w:tc')
            tcPr = OxmlElement('w:tcPr')
            tc.append(tcPr)
            p = OxmlElement('w:p')
            pPr = OxmlElement('w:pPr')
            p.append(pPr)
            r = OxmlElement('w:r')
            t = OxmlElement('w:t')
            t.set(qn('xml:space'), 'preserve')
            t.text = str(cell)
            r.append(t)
            p.append(r)
            tc.append(p)
            tr.append(tc)
        tbl.append(tr)
    return tbl

# US table details for criteria
US_TABLE_DATA = {
    1: [('US#1', 'Sistema permite registro de usuarios, login con credenciales válidas'),
        ('US#2', 'Formulario con campos nombre, descripción, fechas. Validación antes de enviar')],
    2: [('US#3', 'Lista muestra nombre, estado, fecha inicio. Opción filtrar y buscar'),
        ('US#004', 'Opción editar cada proyecto. Cambios guardados correctamente')],
    3: [('US#005', 'Calendario permite entrada de fechas inicio/fin hitos. Envía recordatorios'),
        ('US#006', 'Tareas asignables a miembros del equipo. Actualización de estado')],
    4: [('US#7', 'Informes con métricas clave: % tareas completadas, hitos alcanzados'),
        ('US#08', 'Identificación, evaluación y recomendaciones de mitigación de riesgos')],
    5: [('US#09', 'Ingreso de tipo, cantidad y costo de recursos por proyecto'),
        ('US#10', 'Cálculo automático del costo total de recursos por proyecto')],
    6: [('US#11', 'Reportes con costos desglosados por tipo de recurso, exportables'),
        ('US#12', 'Límites de costo por proyecto con alertas automáticas al superarlos')],
    7: [('US#13', 'Estado de cada tarea visible, actualización en tiempo real')],
    8: [('US#14', 'Alertas automáticas cuando tareas no se completan a tiempo'),
        ('US#15', 'Programación de reuniones y generación de actas automáticas')],
    9: [('US#16', 'Informe con avance porcentual, tareas completadas y pendientes'),
        ('US#17', 'Gráficos de barras, líneas y tortas para métricas del proyecto')],
    10: [('US#18', 'Selección de métricas y formato de informes'),
         ('US#19', 'Programación de generación automática de informes periódicos')],
    11: [('US#20', 'Registro de datos, contacto, rol y nivel de interés de stakeholders'),
         ('US#21', 'Envío de mensajes y notificaciones, registro de comunicaciones')],
    12: [('US#22', 'Programación de reuniones, invitaciones y actas'),
         ('US#23', 'Encuestas de satisfacción, recopilación y análisis de respuestas')],
    13: [('US#24', 'Gestión de cambios en alcance con justificación y recursos afectados'),
         ('US#25', 'Cálculo de impacto en cronograma y presupuesto de cambios')],
    14: [('US#26', 'Flujo de aprobación con comentarios y notificación a interesados'),
         ('US#27', 'Registro completo de cambios aprobados y rechazados con consulta')],
}

doc = Document(INPUT)
body = doc.element.body
children = list(body)

# STEP 1: Remove misplaced criteria validation paragraphs from TOC area
print("\n[1/2] Removiendo validaciones de criterios del índice (TOC)...")
removed = 0
to_remove = []
for i, child in enumerate(children):
    if child.tag != f'{{{W}}}p':
        continue
    text = get_text(child)
    if 'A continuación se presenta la validación de los criterios de aceptación' in text:
        # Check if previous sibling is toc style
        if i > 0:
            prev = children[i-1]
            ppr = prev.find(f'{{{W}}}pPr')
            if ppr is not None:
                ps = ppr.find(f'{{{W}}}pStyle')
                if ps is not None and ps.get(qn('w:val')) in ('toc 2', 'toc 3'):
                    to_remove.append(child)
                    removed += 1

for el in to_remove:
    body.remove(el)
print(f"   → {removed} párrafos removidos del TOC")

# STEP 2: Insert criteria validation in body before each Registro de Pruebas
print("\n[2/2] Insertando validación de criterios en el cuerpo...")

# Re-read children after removal
children = list(body)
para_list = list(doc.paragraphs)

inserted = 0
for sprint_num in range(1, 15):
    # Find "Registro de Pruebas (Sprint N)" in body (Normal style)
    reg_idx = None
    for i, child in enumerate(children):
        if child.tag != f'{{{W}}}p':
            continue
        text = get_text(child)
        if f'Registro de Pruebas (Sprint {sprint_num})' in text:
            ppr = child.find(f'{{{W}}}pPr')
            style = None
            if ppr is not None:
                ps = ppr.find(f'{{{W}}}pStyle')
                if ps is not None:
                    style = ps.get(qn('w:val'))
            if style == 'Normal':
                reg_idx = i
                break
    
    if reg_idx is None:
        continue
    
    reg_el = children[reg_idx]
    us_data = US_TABLE_DATA.get(sprint_num, [])
    if not us_data:
        continue
    
    # Insert intro paragraph
    intro = make_para(
        f"A continuación se presenta la validación de los criterios de aceptación de las historias de usuario "
        f"trabajadas en el Sprint {sprint_num}. Cada criterio fue verificado mediante pruebas automatizadas "
        f"(unitarias, funcionales o E2E) que confirmaron el cumplimiento del requisito.",
        'Normal'
    )
    reg_el.addprevious(intro)
    
    # Insert validation table
    headers = ['Historia de Usuario', 'Criterio de Aceptación', 'Resultado']
    rows = [(us, criteria, '✅ Validado') for us, criteria in us_data]
    tbl = make_table(headers, rows)
    intro.addprevious(tbl)
    
    # Empty paragraph after table
    spacing = make_para('', 'Normal')
    tbl.addnext(spacing)
    
    inserted += 1

print(f"   → {inserted} validaciones de criterios insertadas en el cuerpo")

doc.save(INPUT)
print(f"\n✅ Documento guardado ({os.path.getsize(INPUT)} bytes)")

# Verify
doc2 = Document(INPUT)
criteria_in_toc = sum(1 for p in doc2.paragraphs[:430] if 'validación de los criterios' in p.text.lower())
criteria_in_body = sum(1 for p in doc2.paragraphs[430:] if 'validación de los criterios' in p.text.lower())
print(f"\n📊 Validaciones en TOC: {criteria_in_toc} (debe ser 0)")
print(f"📊 Validaciones en cuerpo: {criteria_in_body} (debe ser 14)")
