#!/usr/bin/env python3
"""
Reestructura sprints agrupados (1-2, 3-4, ...) en 14 sprints INDIVIDUALES
con ceremonias Scrum (Sprint Planning → Objetivo → Desarrollo → Sprint Review →
Sprint Retrospective → Registro de Pruebas).

ESTRATEGIA:
  - Para cada par, recolecta los elementos XML existentes (incluyendo imágenes).
  - Los elementos existentes se convierten en Sprint X (primer sprint del par).
  - Se insertan ceremonias nuevas (Planning, Review, Retrospective) en las
    posiciones correctas.
  - Sprint Y (segundo sprint) se construye completamente nuevo.
  - Se eliminan los elementos viejos y se insertan los nuevos en su lugar.
  - Se procesa del ÚLTIMO par al PRIMERO para mantener índices estables.
"""

import os, re
from lxml import etree
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── CONFIG ────────────────────────────────────────────────────────

BASE = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral'
# Find the actual CORREGIDO file (handle Unicode normalization)
for f in os.listdir(BASE):
    if 'CORREGIDO' in f and 'FINAL' not in f:
        INPUT = os.path.join(BASE, f)
        break
OUTPUT = INPUT  # Modificar en el mismo archivo

print(f"Input/Output: {os.path.basename(INPUT)} ({os.path.getsize(INPUT)} bytes)")

# ── HELPERS ───────────────────────────────────────────────────────

def make_para(text, style='Normal', bold=False):
    """Crea un elemento <w:p> con texto y estilo."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style)
    pPr.append(pStyle)
    p.append(pPr)
    if not text:
        return p
    r = OxmlElement('w:r')
    if bold:
        rPr = OxmlElement('w:rPr')
        b = OxmlElement('w:b')
        rPr.append(b)
        r.append(rPr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return p


def make_empty():
    return make_para('', 'Normal')


def make_heading2(text):
    return make_para(text, 'Estilo2', bold=True)


def get_estilo2_text(para_element):
    """Obtiene el texto de un elemento w:p con estilo Estilo2."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    ppr = para_element.find('w:pPr', ns)
    if ppr is not None:
        pstyle = ppr.find('w:pStyle', ns)
        if pstyle is not None and pstyle.get(qn('w:val')) == 'Estilo2':
            # Get text
            texts = para_element.findall('.//w:t', ns)
            return ''.join(t.text or '' for t in texts)
    return None


def get_para_text(para_element):
    """Obtiene el texto completo de un elemento w:p."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    texts = para_element.findall('.//w:t', ns)
    return ''.join(t.text or '' for t in texts)


def change_para_text(para_element, new_text):
    """Cambia el texto del primer run en un elemento de párrafo."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    runs = para_element.findall('.//w:r', ns)
    if runs:
        t = runs[0].find('w:t', ns)
        if t is not None:
            t.text = new_text
            return True
    # No runs: add a new run
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = new_text
    r.append(t)
    para_element.append(r)
    return True


# ── SPRINT DATA ──────────────────────────────────────────────────

SPRINT_DATA = {}

def build_data():
    global SPRINT_DATA
    
    data_list = [
        # (s1, s2, title, epic, us_s1, us_s2,
        #  plan_s1, dev_s1, review_s1, retro_s1, test_s1,
        #  plan_s2, dev_s2, review_s2, retro_s2, test_s2)
        #
        # Sprint 1-2
        (1, 2, 'Módulo de Gestión de Proyectos', 'E1',
         'US#1 (Login y Autenticación)', 'US#2 (Creación de Proyectos)',
         # Sprint 1
         'En la planificación del Sprint 1 se definió como objetivo principal implementar el módulo de autenticación y roles de usuario. Se seleccionaron las historias de usuario del Product Backlog priorizando los requisitos de seguridad y control de acceso. Se estimó el esfuerzo necesario y se asignaron las tareas correspondientes al equipo de desarrollo.',
         'Se implementó el modelo UserProfile con tres roles: Jefe Departamental, Gestor de Proyectos y Técnico de Proyectos. Cada rol tiene permisos específicos. Para la autenticación se utilizó el sistema de usuarios de Django con login basado en username y password, implementando decoradores personalizados para la verificación de roles.',
         'En la Sprint Review del Sprint 1 se presentó el sistema de autenticación funcional con los tres roles definidos. Se demostró el inicio de sesión con diferentes credenciales y la redirección según el perfil del usuario.',
         'En la retrospectiva del Sprint 1 el equipo identificó como fortaleza la implementación sólida del sistema de roles y permisos. Como área de mejora se señaló la necesidad de documentar mejor los decoradores de permisos.',
         'Se validó que el proceso de inicio de sesión sea correcto en función al nombre de usuario y contraseña ingresados. Se verificó que cada rol tenga acceso únicamente a las funcionalidades autorizadas.',
         # Sprint 2
         'En la planificación del Sprint 2 se estableció como meta completar la funcionalidad de creación y gestión de proyectos. Partiendo de la base de autenticación implementada en el Sprint 1, se definieron los campos del modelo Project y las vistas CRUD necesarias.',
         'Se implementó el modelo Project con los campos: name, description, start_date, end_date, status, budget, actual_cost, responsable y priority. Se desarrollaron las vistas para la creación, visualización, edición y eliminación de proyectos.',
         'En la Sprint Review del Sprint 2 se demostró el módulo de gestión de proyectos completo. Se presentó el dashboard de proyectos y la creación de nuevos proyectos mediante el formulario wizard.',
         'En la retrospectiva del Sprint 2 se destacó la integración exitosa del formulario wizard. Se identificó la oportunidad de mejorar los mensajes de validación.',
         'Se verificó la creación, visualización, edición y eliminación de proyectos. Se validó que los campos obligatorios del formulario funcionen correctamente.'),

        # Sprint 3-4
        (3, 4, 'Módulo de Planificación y Control', 'E2',
         'US#3 (Gestión de Actividades), US#4 (Registro de Hitos), US#5 (Asignación de Responsables)',
         'US#6 (Seguimiento de Actividades), US#7 (Gestión de Riesgos), US#8 (Matriz de Riesgos)',
         # Sprint 3
         'En la planificación del Sprint 3 se definió como objetivo implementar los modelos de Activity y Milestone para la planificación de proyectos.',
         'Se implementaron los modelos Activity y Milestone. El modelo Activity incluye campos para fechas planificadas y reales, estado, prioridad y responsable. El modelo Milestone se creó con campos para nombre, descripción, fecha objetivo, fase y estado de cumplimiento.',
         'En la Sprint Review del Sprint 3 se presentaron los modelos de Activity y Milestone funcionales, demostrando la vista de calendario de hitos.',
         'En la retrospectiva del Sprint 3 se reconoció la complejidad del modelo de actividades con fechas planificadas vs reales.',
         'Se verificó que el sistema permita crear y gestionar hitos y actividades correctamente.',
         # Sprint 4
         'En la planificación del Sprint 4 se acordó desarrollar el módulo de gestión de riesgos, incluyendo la matriz de probabilidad e impacto.',
         'Se implementó el modelo Risk con campos para descripción, probabilidad, impacto, estado, categoría, responsable y estrategia de respuesta. Se desarrollaron vistas para la matriz de probabilidad e impacto.',
         'En la Sprint Review del Sprint 4 se demostró el módulo de riesgos completo con la matriz de probabilidad e impacto.',
         'En la retrospectiva del Sprint 4 se valoró positivamente la implementación de la matriz de riesgos.',
         'Se validó el registro de riesgos con diferentes niveles de probabilidad e impacto.'),

        # Sprint 5-6
        (5, 6, 'Módulo de Gestión de Recursos y Costos', 'E3',
         'US#9 (Registrar Recurso), US#10 (Asignar Recurso a Actividad)',
         'US#11 (Control de Costos), US#12 (Alertas de Sobrecostos)',
         # Sprint 5
         'En la planificación del Sprint 5 se definió como objetivo implementar el registro de recursos y su asignación a las actividades del proyecto.',
         'Se implementó el modelo Resource con campos para nombre, tipo, cantidad, costo por unidad, actividad asociada y costo total. Se desarrollaron vistas para el registro y asignación de recursos.',
         'En la Sprint Review del Sprint 5 se presentó el módulo de recursos funcionando, demostrando la asignación de recursos a las actividades.',
         'En la retrospectiva del Sprint 5 se destacó la utilidad del módulo de recursos.',
         'Se evaluó la automatización del flujo de asignación de recursos a actividades.',
         # Sprint 6
         'En la planificación del Sprint 6 se acordó desarrollar el sistema de control de costos con alertas automáticas de sobrecostos.',
         'Se implementó el sistema de alertas de sobrecostos: cuando el costo de una actividad supera los 10,000 USD, el sistema crea automáticamente una Notificación.',
         'En la Sprint Review del Sprint 6 se demostró el sistema de alertas de sobrecostos.',
         'En la retrospectiva del Sprint 6 se identificó la necesidad de parametrizar los umbrales de alerta.',
         'Se verificó que el sistema genere alertas cuando los costos superen los umbrales establecidos.'),

        # Sprint 7-8
        (7, 8, 'Módulo de Seguimiento y Monitoreo', 'E4',
         'US#13 (Monitorear Progreso), US#14 (Notificaciones de Estado)',
         'US#15 (Gestión de Línea Base y EVM)',
         # Sprint 7
         'En la planificación del Sprint 7 se definió como objetivo implementar el sistema de seguimiento con métricas EVM.',
         'Se implementó el modelo Seguimiento (EVM Tracking) que calcula PV, EV y AC. Se desarrollaron las vistas para visualizar el progreso y el sistema de notificaciones.',
         'En la Sprint Review del Sprint 7 se presentó el dashboard de seguimiento con las curvas S de EVM.',
         'En la retrospectiva del Sprint 7 se destacó la potencia visual de las curvas S de EVM.',
         'Se validó el cálculo correcto de las métricas EVM con datos de prueba.',
         # Sprint 8
         'En la planificación del Sprint 8 se acordó desarrollar la línea base de seguimiento y los escenarios de tracking.',
         'Se implementó el modelo ProjectCut para cortes de revisión con métricas EVM. La propiedad tracking_scenario clasifica actividades en 10 escenarios. El método get_traffic_light_status() implementa el semáforo CMI.',
         'En la Sprint Review del Sprint 8 se demostró la línea base de seguimiento y el semáforo CMI.',
         'En la retrospectiva del Sprint 8 se valoró positivamente la implementación del semáforo CMI.',
         'Se verificó que el semáforo CMI cambie de color según los umbrales definidos.'),

        # Sprint 9-10
        (9, 10, 'Módulo de Generación de Informes y Análisis', 'E5',
         'US#16 (Informes de Estado), US#17 (Reporte de Costos)',
         'US#18 (Reporte de Avance), US#19 (Exportación CSV)',
         # Sprint 9
         'En la planificación del Sprint 9 se definió como objetivo implementar los reportes visuales del sistema.',
         'Se desarrolló la aplicación reports con vistas para gantt_chart, progress_report, cost_report y evm_curves. El Gantt se implementó generando SVG inline.',
         'En la Sprint Review del Sprint 9 se presentaron el diagrama de Gantt y las curvas S de EVM.',
         'En la retrospectiva del Sprint 9 se destacó la decisión de generar SVG inline para el Gantt.',
         'Se verificó que los reportes muestren las métricas correctas.',
         # Sprint 10
         'En la planificación del Sprint 10 se acordó completar los reportes de avance y costos y la exportación de datos.',
         'Se implementaron las vistas para exportación CSV de proyectos, actividades, recursos y riesgos, con filtros por estado, fechas y responsable.',
         'En la Sprint Review del Sprint 10 se demostraron los reportes completos con filtros y exportación CSV.',
         'En la retrospectiva del Sprint 10 se valoró la flexibilidad de los filtros de reportes.',
         'Se comprobó que la exportación CSV incluya todos los campos necesarios.'),

        # Sprint 11-12
        (11, 12, 'Módulo de Comunicación y Gestión de Stakeholders', 'E6',
         'US#20 (Registrar Stakeholder), US#21 (Registrar Feedback)',
         'US#22 (Encuesta de Satisfacción), US#23 (Gestión de Comunicaciones)',
         # Sprint 11
         'En la planificación del Sprint 11 se definió como objetivo implementar el registro de stakeholders y el sistema de feedback.',
         'Se implementó la aplicación stakeholders con los modelos Stakeholder y Feedback, incluyendo matriz de interés/poder y calificación del 1 al 5.',
         'En la Sprint Review del Sprint 11 se presentó el módulo de stakeholders con la matriz de interés/poder.',
         'En la retrospectiva del Sprint 11 se destacó la utilidad de la matriz interés-poder.',
         'Se validó el registro y gestión de stakeholders con sus niveles de interés y poder.',
         # Sprint 12
         'En la planificación del Sprint 12 se acordó desarrollar el módulo de comunicaciones con los stakeholders.',
         'Se implementó el modelo Comunicacion para registrar comunicaciones con fecha, mensaje, tipo y destinatario.',
         'En la Sprint Review del Sprint 12 se demostró el registro de comunicaciones con historial completo.',
         'En la retrospectiva del Sprint 12 se valoró el historial de comunicaciones.',
         'Se verificó el registro de comunicaciones con diferentes tipos y destinatarios.'),

        # Sprint 13-14
        (13, 14, 'Módulo de Gestión de Cambios y Control de Versiones', 'E7',
         'US#24 (Registrar Cambios), US#25 (Evaluar Impacto)',
         'US#26 (Aprobar/Rechazar Cambios), US#27 (Control de Versiones)',
         # Sprint 13
         'En la planificación del Sprint 13 se definió como objetivo implementar el registro de solicitudes de cambio.',
         'Se implementó el modelo ChangeRequest con campos para descripción, justificación, impacto estimado y estado.',
         'En la Sprint Review del Sprint 13 se presentó el formulario de solicitud de cambios.',
         'En la retrospectiva del Sprint 13 se destacó la claridad del formulario de solicitud de cambios.',
         'Se validó que el sistema permita registrar solicitudes de cambio correctamente.',
         # Sprint 14
         'En la planificación del Sprint 14 se acordó desarrollar el flujo de aprobación de cambios y los cortes de revisión.',
         'Se implementó el flujo de aprobación: el Técnico solicita, el Jefe Departamental aprueba o rechaza. Se implementó el modelo ProjectCut para cortes de revisión.',
         'En la Sprint Review del Sprint 14 se demostró el flujo completo de aprobación de cambios.',
         'En la retrospectiva del Sprint 14, último sprint, el equipo reflexionó sobre el proceso completo, destacando la integración exitosa de todos los módulos.',
         'Se validó que el sistema bloquee cambios no aprobados y que los cortes de revisión capturen métricas EVM.'),
    ]

    for item in data_list:
        s1, s2 = item[0], item[1]
        SPRINT_DATA[(s1, s2)] = item


build_data()


# ── BUILD SPRINT Y CONTENT ────────────────────────────────────────

def build_sprint_y(s2, data):
    """Construye lista de elementos XML para Sprint Y (segundo sprint del par)."""
    (_, _, title, epic, _, us_s2,
     _, _, _, _, _,
     plan_s2, dev_s2, review_s2, retro_s2, test_s2) = data

    els = []
    els.append(make_heading2(f'Sprint {s2}: {title} - Parte 2 ({epic})'))
    els.append(make_empty())
    els.append(make_heading2('Sprint Planning'))
    els.append(make_para(plan_s2))
    els.append(make_empty())
    els.append(make_heading2('Objetivo'))
    els.append(make_para(f'El Sprint {s2} tuvo como objetivo implementar {us_s2} como parte de la {epic}.'))
    els.append(make_empty())
    els.append(make_heading2('Desarrollo de código'))
    els.append(make_para(dev_s2))
    els.append(make_empty())
    els.append(make_heading2('Sprint Review'))
    els.append(make_para(review_s2))
    els.append(make_empty())
    els.append(make_heading2('Sprint Retrospective'))
    els.append(make_para(retro_s2))
    els.append(make_empty())
    els.append(make_heading2(f'Registro de Pruebas (Sprint {s2})'))
    els.append(make_para(test_s2))
    els.append(make_empty())
    return els


# ── MAIN REESTRUCTURING ──────────────────────────────────────────

def process_sprint_pair(doc, sec_start, sec_end, s1, s2, data):
    """
    Transforma el par de sprints (sec_start..sec_end) en dos sprints individuales.
    
    Retorna (nuevo_start, nuevo_end) o None si falla.
    """
    (_, _, title, epic, us_s1, _,
     plan_s1, dev_s1, review_s1, retro_s1, test_s1,
     *_) = data

    body = doc.element.body
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # ── 1. Collect existing paragraph elements ──
    all_body_children = list(body)
    
    # Find the actual indexes in the body (accounting for non-paragraph elements like tables)
    # We need to find the body children that correspond to sec_start..sec_end paragraphs
    # This is tricky because doc.paragraphs counts only w:p elements, while body has
    # other element types too.
    
    # Better approach: find elements by iterating and matching paragraph elements
    para_els = []
    para_count = 0
    first_para_idx = None
    last_para_idx = None
    
    for body_idx, child in enumerate(all_body_children):
        if child.tag == qn('w:p'):
            if para_count == sec_start:
                first_para_idx = body_idx
            if para_count == sec_end:
                last_para_idx = body_idx
                break
            para_count += 1
    
    if first_para_idx is None or last_para_idx is None:
        print(f"    ⚠️  No se encontraron índices en body para Sprint {s1}-{s2}")
        return None
    
    # Collect all body children in the range (may include tables, not just paragraphs)
    existing_elements = all_body_children[first_para_idx:last_para_idx + 1]
    
    # ── 2. Analyze existing elements ──
    # Find key headings within the section
    objetivo_idx = None
    desarrollo_idx = None
    registro_idx = None
    
    for i, el in enumerate(existing_elements):
        if el.tag != qn('w:p'):
            continue
        text = get_estilo2_text(el)
        if not text:
            continue
        if 'Objetivo' in text and not any(x in text for x in ['Importancia', 'Fundamentos']):
            objetivo_idx = i
        elif 'Desarrollo de código' in text:
            desarrollo_idx = i
        elif 'Registro de Pruebas' in text:
            registro_idx = i
    
    if None in (objetivo_idx, desarrollo_idx, registro_idx):
        print(f"    ⚠️  Subsecciones no encontradas en Sprint {s1}-{s2}")
        return None
    
    # ── 3. Build Sprint X (modified existing section) ──
    sprint_x = []
    
    # New heading
    sprint_x.append(make_heading2(f'Sprint {s1}: {title} - Parte 1 ({epic})'))
    sprint_x.append(make_empty())
    
    # Sprint Planning (NEW)
    sprint_x.append(make_heading2('Sprint Planning'))
    sprint_x.append(make_para(plan_s1))
    sprint_x.append(make_empty())
    
    # Objetivo: keep existing heading + content
    # Find all elements from Objetivo heading to before Desarrollo heading
    for el in existing_elements[objetivo_idx:desarrollo_idx]:
        sprint_x.append(el)
    sprint_x.append(make_empty())
    
    # Desarrollo: keep existing heading + content (up to Registro de Pruebas)
    for el in existing_elements[desarrollo_idx:registro_idx]:
        sprint_x.append(el)
    sprint_x.append(make_empty())
    
    # Sprint Review (NEW)
    sprint_x.append(make_heading2('Sprint Review'))
    sprint_x.append(make_para(review_s1))
    sprint_x.append(make_empty())
    
    # Sprint Retrospective (NEW)
    sprint_x.append(make_heading2('Sprint Retrospective'))
    sprint_x.append(make_para(retro_s1))
    sprint_x.append(make_empty())
    
    # Registro de Pruebas: modify heading + keep existing content
    # Change the heading text
    reg_heading = existing_elements[registro_idx]
    change_para_text(reg_heading, f'Registro de Pruebas (Sprint {s1})')
    
    # Keep remaining elements
    for el in existing_elements[registro_idx:]:
        sprint_x.append(el)
    
    # ── 4. Build Sprint Y ──
    sprint_y = build_sprint_y(s2, data)
    
    # ── 5. Replace old section with new content ──
    # Sprint X primero, luego Sprint Y (en orden directo)
    all_new = sprint_x + sprint_y
    
    # Get the element after the section (if any)
    after_section = None
    if last_para_idx + 1 < len(all_body_children):
        after_section = all_body_children[last_para_idx + 1]
    
    # Remove old elements from body
    for el in existing_elements:
        try:
            body.remove(el)
        except ValueError:
            pass  # Already removed
    
    # Insert new elements
    # Insertar antes del elemento que estaba después de la sección.
    # addprevious inserta inmediatamente antes del elemento de referencia.
    # Iterando en orden forward (x1, x2, ..., y1, y2, ...), cada elemento
    # se inserta justo antes de `after_section`, resultando en el orden:
    # x1, x2, ..., xM, y1, y2, ..., yN, after_section.
    if after_section is not None:
        for el in all_new:
            after_section.addprevious(el)
    else:
        for el in all_new:
            body.append(el)
    
    print(f"    ✅ Sprint {s1} (modificado, {len(sprint_x)} elem.) + Sprint {s2} (nuevo, {len(sprint_y)} elem.)")
    return True


# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("📄 Cargando documento...")
    doc = Document(INPUT)
    
    print("🔍 Detectando secciones de sprints...")
    sections = []
    current = None
    
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        style = p.style.name
        m = re.match(r'Sprint (\d+) \- (\d+):', text)
        if m:
            if current:
                current['end'] = i - 1
                sections.append(current)
            current = {'s1': int(m.group(1)), 's2': int(m.group(2)),
                       'start': i, 'end': None}
        elif current and current['end'] is None:
            if style == 'Heading 1' or re.match(r'^\d+\.\d', text):
                current['end'] = i - 1
                sections.append(current)
                current = None
    
    if current and current['end'] is None:
        current['end'] = len(doc.paragraphs) - 1
        sections.append(current)
    
    print(f"   → {len(sections)} pares encontrados.")
    for s in sections:
        print(f"      Sprint {s['s1']}-{s['s2']}: párrafos {s['start']}-{s['end']}")
    
    # Process BOTTOM-UP
    print("\n🔄 Reestructurando (del último al primero)...")
    sections.sort(key=lambda s: s['start'], reverse=True)
    
    for sec in sections:
        key = (sec['s1'], sec['s2'])
        if key not in SPRINT_DATA:
            print(f"   ⚠️  Saltando Sprint {sec['s1']}-{sec['s2']}")
            continue
        process_sprint_pair(doc, sec['start'], sec['end'],
                           sec['s1'], sec['s2'], SPRINT_DATA[key])
    
    print("\n💾 Guardando...")
    doc.save(OUTPUT)
    print(f"✅ Guardado: {OUTPUT}")
