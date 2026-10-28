#!/usr/bin/env python3
"""
Agrega al documento E4:
  1. Secciones faltantes al Apéndice A (A.6–A.10) — Manual del Sistema
  2. Apéndice D completo con el Manual de Usuario (desde MANUAL_DE_USUARIO.md)
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
import re
import os

DOCX_PATH = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral/E4_MERCHÁN_MONTALVÁN_JOSÉ_RAMIRO_FINAL.docx'
MANUAL_MD_PATH = '/mnt/c/Users/Dell/Documents/cuadroInt/webappcuadrointegral/MANUAL_DE_USUARIO.md'
BACKUP_PATH = DOCX_PATH.replace('.docx', '_BACKUP_ANTES_APENDICES.docx')

# ─── Helpers ───────────────────────────────────────────────────────────────────

def get_paragraph_style(doc, style_name):
    """Get or create a paragraph style by name."""
    try:
        return doc.styles[style_name]
    except KeyError:
        return None


def insert_element_after(ref_element, new_element):
    """Insert new_element in the XML tree right after ref_element."""
    ref_element.addnext(new_element)


def make_paragraph(doc, text='', style='Normal'):
    """Create a new paragraph element (not yet inserted)."""
    from docx.text.paragraph import Paragraph
    p = OxmlElement('w:p')
    # Create paragraph properties
    pPr = OxmlElement('w:pPr')
    if style and style != 'Normal':
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), style)
        pPr.append(pStyle)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
    return p


def add_paragraph_after(doc, ref_para, text='', style='Normal'):
    """Insert a new paragraph after the given reference paragraph."""
    new_p = make_paragraph(doc, text, style)
    insert_element_after(ref_para._element, new_p)
    return type(ref_para)(new_p, ref_para.part)


def make_list_item(doc, text, level=0):
    """Create a list paragraph element."""
    from docx.text.paragraph import Paragraph
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'List Paragraph')
    pPr.append(pStyle)
    if level > 0:
        ind = OxmlElement('w:ind')
        ind.set(qn('w:left'), str(720 + level * 360))
        pPr.append(ind)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
    return p


def add_list_item_after(doc, ref_para, text, level=0):
    """Insert a list item after ref_para."""
    p = make_list_item(doc, text, level)
    insert_element_after(ref_para._element, p)
    return type(ref_para)(p, ref_para.part)


def add_mixed_paragraph_after(doc, ref_para, parts):
    """
    Insert a paragraph with mixed formatting.
    parts is a list of dicts: [{'text': '...', 'bold': False, 'italic': False}, ...]
    """
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    p.append(pPr)
    
    for part in parts:
        text = part.get('text', '')
        if not text:
            continue
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if part.get('bold'):
            rPr.append(OxmlElement('w:b'))
        if part.get('italic'):
            rPr.append(OxmlElement('w:i'))
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
    
    insert_element_after(ref_para._element, p)
    return type(ref_para)(p, ref_para.part)


def add_empty_line_after(doc, ref_para):
    """Add an empty paragraph (spacer)."""
    return add_paragraph_after(doc, ref_para, '', 'Normal')


def add_heading_after(doc, ref_para, text, level=1):
    """Insert a heading paragraph after the reference paragraph."""
    style_map = {1: 'Heading 1', 2: 'Heading 2', 3: 'Heading 3', 4: 'Heading 4'}
    style_name = style_map.get(level, f'Heading {level}')
    return add_paragraph_after(doc, ref_para, text, style_name)


def add_table_after(doc, ref_para, headers, rows):
    """Insert a formatted table after ref_para. Returns ref_para (last para before table insertion doesn't change)."""
    tbl = OxmlElement('w:tbl')
    # Table properties
    tblPr = OxmlElement('w:tblPr')
    tblStyle = OxmlElement('w:tblStyle')
    tblStyle.set(qn('w:val'), 'Table Grid')
    tblPr.append(tblStyle)
    tblWidth = OxmlElement('w:tblW')
    tblWidth.set(qn('w:w'), '5000')
    tblWidth.set(qn('w:type'), 'pct')
    tblPr.append(tblWidth)
    tbl.append(tblPr)
    
    # Header row
    tr_h = OxmlElement('w:tr')
    for h_text in headers:
        tc = OxmlElement('w:tc')
        tcPr = OxmlElement('w:tcPr')
        tcW = OxmlElement('w:tcW')
        tcW.set(qn('w:w'), str(int(5000 / len(headers))))
        tcW.set(qn('w:type'), 'dxa')
        tcPr.append(tcW)
        # Shading
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), 'D9E2F3')
        shd.set(qn('w:val'), 'clear')
        tcPr.append(shd)
        tc.append(tcPr)
        p = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'center')
        pPr.append(jc)
        p.append(pPr)
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        b = OxmlElement('w:b')
        rPr.append(b)
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), '20')  # 10pt
        rPr.append(sz)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = h_text
        r.append(t)
        p.append(r)
        tc.append(p)
        tr_h.append(tc)
    tbl.append(tr_h)
    
    # Data rows
    for row_data in rows:
        tr = OxmlElement('w:tr')
        for c_text in row_data:
            tc = OxmlElement('w:tc')
            tcPr = OxmlElement('w:tcPr')
            tcW = OxmlElement('w:tcW')
            tcW.set(qn('w:w'), str(int(5000 / len(headers))))
            tcW.set(qn('w:type'), 'dxa')
            tcPr.append(tcW)
            tc.append(tcPr)
            p = OxmlElement('w:p')
            r = OxmlElement('w:r')
            rPr = OxmlElement('w:rPr')
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), '20')  # 10pt
            rPr.append(sz)
            r.append(rPr)
            t = OxmlElement('w:t')
            t.set(qn('xml:space'), 'preserve')
            t.text = str(c_text)
            r.append(t)
            p.append(r)
            tc.append(p)
            tr.append(tc)
        tbl.append(tr)
    
    # Insert table after ref_para's element
    insert_element_after(ref_para._element, tbl)
    return ref_para


# ─── Load original document ────────────────────────────────────────────────────

print("📄 Cargando documento...")
doc = Document(DOCX_PATH)

# Find key reference paragraphs
para_apendice_b = None
para_last_c = None
para_apendice_a_last_content = None  # Last paragraph of A.5 content

for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if text == 'Apéndice B. Plan de Capacitación.' and p.style.name == 'Estilo2':
        para_apendice_b = p
    if text == 'Apéndice C. Informes de Auditoría.' and p.style.name == 'Estilo2':
        # The last content of appendix C is the last list paragraph after C.3
        pass

# Find last paragraph before Apéndice B (end of Appendix A content)
# And find last paragraph of document (end of Appendix C)
last_para = None
for p in doc.paragraphs:
    last_para = p

# Find Apéndice B heading precisely
apendice_b_para = None
apendice_c_para = None
for p in doc.paragraphs:
    text = p.text.strip()
    style = p.style.name
    if text == 'Apéndice B. Plan de Capacitación.' and style == 'Estilo2':
        apendice_b_para = p
    if text == 'Apéndice C. Informes de Auditoría.' and style == 'Estilo2':
        apendice_c_para = p

if not apendice_b_para:
    print("❌ No se encontró 'Apéndice B. Plan de Capacitación.'")
    exit(1)
if not apendice_c_para:
    print("❌ No se encontró 'Apéndice C. Informes de Auditoría.'")
    exit(1)

print(f"✅ Apéndice B encontrado: para {apendice_b_para.text[:50]}")
print(f"✅ Apéndice C encontrado: para {apendice_c_para.text[:50]}")

# ─── PART 1: Add A.6 to A.10 to Appendix A ────────────────────────────────────

# We insert before Apéndice B. So we reference the paragraph just before it.
# Actually, we'll insert right before the Apéndice B heading.
# The last content of Appendix A is the "Total: 14 tablas..." paragraph.
# We need to find it. It's the paragraph just before Apéndice B.

# Find the paragraph right before Apéndice B
ref_a = None
for i, p in enumerate(doc.paragraphs):
    if p._element is apendice_b_para._element and i > 0:
        ref_a = doc.paragraphs[i - 1]
        break

if not ref_a:
    print("❌ No se pudo encontrar el párrafo anterior a Apéndice B")
    exit(1)

print(f"✅ Insertando A.6–A.10 después del párrafo: '{ref_a.text[:60]}...'")

current = ref_a

# ─── A.6 Configuración del Servidor Web ───────────────────────────────────────

current = add_heading_after(doc, current, 'A.6 Configuración del Servidor Web', 3)
current = add_paragraph_after(doc, current, 
    'El sistema utiliza Nginx como proxy inverso y Gunicorn como servidor WSGI. '
    'A continuación se detalla la configuración de ambos componentes para el entorno de producción.')

current = add_heading_after(doc, current, 'A.6.1 Servicio Systemd de Gunicorn', 4)
current = add_paragraph_after(doc, current,
    'Gunicorn se ejecuta como un servicio systemd para garantizar su inicio automático '
    'y recuperación ante fallos. El archivo de servicio se ubica en '
    '/etc/systemd/system/cmi.service con el siguiente contenido:')

# Gunicorn service config as code block
current = add_paragraph_after(doc, current, 
    '[Unit]\n'
    'Description=CMI Gunicorn service\n'
    'After=network.target mysql.service\n\n'
    '[Service]\n'
    'Type=notify\n'
    'User=www-data\n'
    'Group=www-data\n'
    'RuntimeDirectory=cmi\n'
    'WorkingDirectory=/var/www/cmi\n'
    'ExecStart=/var/www/cmi/venv/bin/gunicorn --workers 3 --bind unix:/var/www/cmi/cmi.sock cmi_project.wsgi:application\n'
    'ExecReload=/bin/kill -s HUP $MAINPID\n'
    'Restart=always\n'
    'RestartSec=10\n\n'
    '[Install]\n'
    'WantedBy=multi-user.target',
    'Normal')

current = add_paragraph_after(doc, current, 
    'Para habilitar e iniciar el servicio se ejecutan los comandos:')
current = add_paragraph_after(doc, current,
    'sudo systemctl daemon-reload\n'
    'sudo systemctl enable cmi\n'
    'sudo systemctl start cmi\n'
    'sudo systemctl status cmi   # Verificar que esté activo',
    'Normal')

current = add_heading_after(doc, current, 'A.6.2 Configuración de Nginx', 4)
current = add_paragraph_after(doc, current,
    'Nginx actúa como proxy inverso, redirigiendo las peticiones HTTP hacia Gunicorn '
    'y sirviendo los archivos estáticos directamente. El archivo de configuración del '
    'sitio se ubica en /etc/nginx/sites-available/cmi:')

current = add_paragraph_after(doc, current,
    'server {\n'
    '    listen 80;\n'
    '    server_name cmi.gadcilica.gob.ec;\n\n'
    '    location /static/ {\n'
    '        alias /var/www/cmi/staticfiles/;\n'
    '    }\n\n'
    '    location /media/ {\n'
    '        alias /var/www/cmi/media/;\n'
    '    }\n\n'
    '    location / {\n'
    '        include proxy_params;\n'
    '        proxy_pass http://unix:/var/www/cmi/cmi.sock;\n'
    '    }\n'
    '}',
    'Normal')

current = add_paragraph_after(doc, current,
    'Para activar la configuración: sudo ln -s /etc/nginx/sites-available/cmi /etc/nginx/sites-enabled/ '
    'y sudo nginx -t para verificar la sintaxis antes de reiniciar con sudo systemctl restart nginx.')

current = add_heading_after(doc, current, 'A.6.3 Configuración de HTTPS con Let\'s Encrypt', 4)
current = add_paragraph_after(doc, current,
    'La comunicación segura se habilita mediante Certbot y Let\'s Encrypt. '
    'Ejecutar el siguiente comando para obtener y configurar el certificado SSL:')
current = add_paragraph_after(doc, current,
    'sudo certbot --nginx -d cmi.gadcilica.gob.ec',
    'Normal')
current = add_paragraph_after(doc, current,
    'Certbot modifica automáticamente la configuración de Nginx para incluir las directivas SSL '
    'y la redirección HTTP → HTTPS. La renovación automática se configura mediante un timer de systemd: '
    'sudo systemctl enable certbot.timer && sudo systemctl start certbot.timer.')
current = add_paragraph_after(doc, current,
    'La configuración generada por Certbot incluye los certificados en /etc/letsencrypt/live/ '
    'y las directivas ssl_certificate y ssl_certificate_key en el bloque server de Nginx.')

# ─── A.7 Seguridad ─────────────────────────────────────────────────────────────

current = add_heading_after(doc, current, 'A.7 Configuración de Seguridad', 3)
current = add_paragraph_after(doc, current,
    'El sistema implementa múltiples capas de seguridad tanto a nivel de aplicación como de servidor.')

current = add_heading_after(doc, current, 'A.7.1 Seguridad a Nivel de Aplicación', 4)
current = add_paragraph_after(doc, current,
    'Las siguientes protecciones están configuradas en Django:')

sec_items = [
    'CSRF: Activado mediante CsrfViewMiddleware en todos los formularios del sistema.',
    'XSS: Auto-escaping de templates de Django. Todas las variables en templates se escapan por defecto.',
    'SQL Injection: Prevenido mediante el ORM de Django que parametriza todas las consultas.',
    'Sesiones: SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SECURE=True en producción.',
    'Headers de seguridad: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Secure HSTS por 1 año.',
    'Autenticación: Passwords hasheados con PBKDF2, validadores de complejidad activados.',
]
for item in sec_items:
    current = add_list_item_after(doc, current, item)

current = add_heading_after(doc, current, 'A.7.2 Seguridad a Nivel de Servidor', 4)
current = add_paragraph_after(doc, current,
    'Configuraciones recomendadas para el servidor Ubuntu:')

server_sec = [
    'Firewall UFW: habilitar solo los puertos 80 (HTTP), 443 (HTTPS) y 22 (SSH). Comando: sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable.',
    'Fail2ban: instalar y configurar para proteger contra ataques de fuerza bruta en SSH: sudo apt install fail2ban -y.',
    'Automatización de actualizaciones de seguridad: sudo apt install unattended-upgrades -y && sudo dpkg-reconfigure --priority=low unattended-upgrades.',
    'Deshabilitar root login en SSH: editar /etc/ssh/sshd_config, establecer PermitRootLogin no, reiniciar sudo systemctl restart sshd.',
]
for item in server_sec:
    current = add_list_item_after(doc, current, item)

current = add_heading_after(doc, current, 'A.7.3 Configuración de Variables de Entorno', 4)
current = add_paragraph_after(doc, current,
    'El archivo .env contiene las variables sensibles del sistema y NO debe incluirse en el repositorio. '
    'Las variables requeridas son:')

current = add_table_after(doc, current,
    ['Variable', 'Descripción', 'Ejemplo'],
    [
        ['DJANGO_SECRET_KEY', 'Clave secreta de Django', 'django-insecure-...'],
        ['DJANGO_DEBUG', 'Modo depuración (False en prod)', 'False'],
        ['DJANGO_ALLOWED_HOSTS', 'Hosts permitidos', 'localhost,cmi.gadcilica.gob.ec'],
        ['DJANGO_DB_ENGINE', 'Motor de base de datos', 'django.db.backends.mysql'],
        ['DJANGO_DB_NAME', 'Nombre de la base de datos', 'cmi_gad_celica'],
        ['DJANGO_DB_USER', 'Usuario de base de datos', 'cmi_user'],
        ['DJANGO_DB_PASSWORD', 'Contraseña de base de datos', '••••••••'],
        ['DJANGO_DB_HOST', 'Host de base de datos', 'localhost'],
        ['DJANGO_DB_PORT', 'Puerto de base de datos', '3306'],
        ['DJANGO_SECURE_COOKIES', 'Cookies seguras (True en prod)', 'True'],
        ['DJANGO_LOG_LEVEL', 'Nivel de logging', 'INFO'],
    ]
)

# ─── A.8 Respaldo y Restauración ───────────────────────────────────────────────

current = add_heading_after(doc, current, 'A.8 Respaldo y Restauración', 3)

current = add_heading_after(doc, current, 'A.8.1 Respaldo de la Base de Datos', 4)
current = add_paragraph_after(doc, current,
    'Se recomienda realizar respaldos periódicos de la base de datos MySQL. '
    'El siguiente comando genera un respaldo completo:')
current = add_paragraph_after(doc, current,
    'mysqldump -u cmi_user -p cmi_gad_celica > /var/backups/cmi/cmi_$(date +%Y%m%d_%H%M%S).sql',
    'Normal')
current = add_paragraph_after(doc, current,
    'Para automatizar los respaldos diarios, crear el script /usr/local/bin/respaldar_cmi.sh con el siguiente contenido:')

current = add_paragraph_after(doc, current,
    '#!/bin/bash\n'
    'BACKUP_DIR="/var/backups/cmi"\n'
    'DB_NAME="cmi_gad_celica"\n'
    'DB_USER="cmi_user"\n'
    'mkdir -p "$BACKUP_DIR"\n'
    'mysqldump -u "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_DIR/cmi_$(date +%Y%m%d_%H%M%S).sql.gz"\n'
    'find "$BACKUP_DIR" -name "cmi_*.sql.gz" -mtime +30 -delete',
    'Normal')

current = add_paragraph_after(doc, current,
    'Luego agregar una entrada en crontab para ejecución diaria a las 3:00 AM:')
current = add_paragraph_after(doc, current,
    '0 3 * * * /usr/local/bin/respaldar_cmi.sh',
    'Normal')

current = add_heading_after(doc, current, 'A.8.2 Restauración de la Base de Datos', 4)
current = add_paragraph_after(doc, current,
    'Para restaurar la base de datos desde un respaldo:')
current = add_paragraph_after(doc, current,
    'gunzip -c /var/backups/cmi/cmi_20260101_030000.sql.gz | mysql -u cmi_user -p cmi_gad_celica',
    'Normal')
current = add_paragraph_after(doc, current,
    'Importante: la restauración sobrescribe todos los datos existentes. '
    'Se recomienda realizar un respaldo previo antes de restaurar.')

current = add_heading_after(doc, current, 'A.8.3 Respaldo de Archivos Estáticos y Multimedia', 4)
current = add_paragraph_after(doc, current,
    'Además de la base de datos, se deben respaldar los archivos subidos y la configuración:')
current = add_paragraph_after(doc, current,
    'tar -czf /var/backups/cmi/cmi_files_$(date +%Y%m%d).tar.gz /var/www/cmi/media/ /var/www/cmi/.env',
    'Normal')
current = add_paragraph_after(doc, current,
    'Se recomienda almacenar los respaldos en una ubicación externa al servidor '
    '(almacenamiento en la nube, servidor remoto o dispositivo extraíble).')

# ─── A.9 Monitoreo ─────────────────────────────────────────────────────────────

current = add_heading_after(doc, current, 'A.9 Monitoreo, Logs y Mantenimiento', 3)

current = add_heading_after(doc, current, 'A.9.1 Logs del Sistema', 4)
current = add_paragraph_after(doc, current,
    'El sistema registra eventos en múltiples ubicaciones:')

current = add_table_after(doc, current,
    ['Componente', 'Ubicación del Log', 'Propósito'],
    [
        ['Gunicorn', 'journalctl -u cmi.service', 'Logs del servidor WSGI'],
        ['Nginx acceso', '/var/log/nginx/access.log', 'Peticiones HTTP entrantes'],
        ['Nginx error', '/var/log/nginx/error.log', 'Errores del proxy inverso'],
        ['Django', 'Consola (vía Gunicorn)', 'Logs de la aplicación Django'],
        ['MySQL', '/var/log/mysql/error.log', 'Errores de base de datos'],
        ['Certbot', '/var/log/letsencrypt/', 'Renovación de certificados SSL'],
    ]
)

current = add_paragraph_after(doc, current,
    'Para monitorear los logs en tiempo real: sudo journalctl -u cmi.service -f')

current = add_heading_after(doc, current, 'A.9.2 Monitoreo de Recursos', 4)
current = add_paragraph_after(doc, current,
    'Se recomienda monitorear periódicamente el estado del servidor:')
mon_items = [
    'Uso de disco: df -h — verificar que /var/www/cmi/media/ no sature el disco.',
    'Memoria RAM: free -h — Gunicorn con 3 workers consume aproximadamente 300-500 MB.',
    'CPU: top o htop — verificar que el uso no supere el 80% sostenido.',
    'Conexiones a BD: mysqladmin status -u cmi_user -p — verificar número de conexiones activas.',
    'Certificados SSL: sudo certbot certificates — verificar fecha de expiración.',
]
for item in mon_items:
    current = add_list_item_after(doc, current, item)

current = add_heading_after(doc, current, 'A.9.3 Tareas de Mantenimiento Programado', 4)

current = add_table_after(doc, current,
    ['Frecuencia', 'Tarea', 'Comando/Acción'],
    [
        ['Diaria', 'Respaldo de BD', 'Automático vía cron (A.8.1)'],
        ['Semanal', 'Rotación de logs', 'Configurado en /etc/logrotate.d/'],
        ['Mensual', 'Limpieza de respaldos antiguos', 'Automático (>30 días)'],
        ['Trimestral', 'Renovación SSL', 'Automático vía certbot.timer'],
        ['Trimestral', 'Optimización de tablas MySQL', 'mysqlcheck -o cmi_gad_celica'],
        ['Anual', 'Actualización del sistema', 'sudo apt update && sudo apt upgrade'],
    ]
)

# ─── A.10 Solución de Problemas Técnicos ───────────────────────────────────────

current = add_heading_after(doc, current, 'A.10 Solución de Problemas Técnicos', 3)

current = add_heading_after(doc, current, 'A.10.1 El servicio no arranca', 4)
current = add_paragraph_after(doc, current,
    'Si el sitio no responde, verificar el estado de los servicios:')
current = add_paragraph_after(doc, current,
    'sudo systemctl status cmi.service\n'
    'sudo systemctl status nginx\n'
    'sudo systemctl status mysql',
    'Normal')
current = add_paragraph_after(doc, current,
    'Revisar los logs con journalctl -u cmi.service -n 50 --no-pager para identificar el error.')

current = add_heading_after(doc, current, 'A.10.2 Error 502 (Bad Gateway)', 4)
current = add_paragraph_after(doc, current,
    'Este error indica que Nginx no puede comunicarse con Gunicorn. Causas posibles:')
err_items = [
    'Gunicorn no está corriendo: sudo systemctl restart cmi.service.',
    'El socket Unix no existe o tiene permisos incorrectos: verificar /var/www/cmi/cmi.sock.',
    'El usuario www-data no tiene permisos sobre el directorio del proyecto: sudo chown -R www-data:www-data /var/www/cmi.',
]
for item in err_items:
    current = add_list_item_after(doc, current, item)

current = add_heading_after(doc, current, 'A.10.3 Error 500 (Internal Server Error)', 4)
current = add_paragraph_after(doc, current,
    'Error interno del servidor. Revisar los logs de Django y Gunicorn. '
    'Si DEBUG=False en producción, Django no muestra detalles del error — '
    'revisar journalctl -u cmi.service -n 30.')

current = add_heading_after(doc, current, 'A.10.4 Error de conexión a la base de datos', 4)
current = add_paragraph_after(doc, current,
    'Verificar que MySQL esté corriendo: sudo systemctl status mysql. '
    'Verificar credenciales en el archivo .env. '
    'Probar conexión manual: mysql -u cmi_user -p -h localhost cmi_gad_celica.')

current = add_heading_after(doc, current, 'A.10.5 Certificado SSL expirado', 4)
current = add_paragraph_after(doc, current,
    'Ejecutar renovación manual: sudo certbot renew. '
    'Verificar el timer automático: sudo systemctl status certbot.timer. '
    'Si el timer no está activo: sudo systemctl enable certbot.timer && sudo systemctl start certbot.timer.')

current = add_heading_after(doc, current, 'A.10.6 Espacio en disco insuficiente', 4)
current = add_paragraph_after(doc, current,
    'Verificar uso: df -h. Limpiar respaldos antiguos si es necesario. '
    'Revisar el directorio /var/backups/cmi/ para eliminar respaldos obsoletos. '
    'Los archivos multimedia subidos por usuarios se almacenan en /var/www/cmi/media/.')

print("✅ Secciones A.6 a A.10 agregadas al Apéndice A")

# ─── PART 2: Add Appendix D with User Manual ─────────────────────────────────

# Find the last paragraph of Appendix C (should be the very last paragraph)
last_c_para = None
for p in doc.paragraphs:
    last_c_para = p

# But we should also check for any empty trailing paragraphs
# Let's find the last content paragraph (non-empty, after Apéndice C)
apendice_c_heading = None
for p in doc.paragraphs:
    if p.text.strip() == 'Apéndice C. Informes de Auditoría.' and p.style.name == 'Estilo2':
        apendice_c_heading = p
        break

# Find the last non-empty paragraph
last_content = None
for p in doc.paragraphs:
    if p.text.strip():
        last_content = p

print(f"✅ Último párrafo del documento: '{last_content.text[:60]}...'")

# Now insert Appendix D after the last paragraph of Appendix C
current_d = last_content

# Apéndice D heading
current_d = add_paragraph_after(doc, current_d, '', 'Normal')
current_d = add_heading_after(doc, current_d, 'Apéndice D. Manual de Usuario.', 1)

current_d = add_paragraph_after(doc, current_d, 
    'A continuación se presenta el manual de usuario del Sistema de Gestión Integral de Proyectos '
    'y Cuadro de Mando Integral (CMI) del GAD Municipal de Celica. Este manual describe todas las '
    'funcionalidades del sistema desde la perspectiva del usuario final, incluyendo capturas de pantalla '
    'referenciales, instrucciones paso a paso y solución de problemas comunes.',
    'Normal')

current_d = add_empty_line_after(doc, current_d)

# ─── Read and parse MANUAL_DE_USUARIO.md ─────────────────────────────────────

print("📖 Leyendo MANUAL_DE_USUARIO.md...")
with open(MANUAL_MD_PATH, 'r', encoding='utf-8') as f:
    md_lines = f.readlines()

def parse_md_to_docx(doc, start_para, lines):
    """Parse markdown content and add to docx after start_para."""
    current = start_para
    i = 0
    in_code_block = False
    code_buffer = []
    in_table = False
    table_headers = []
    table_rows = []
    
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block - dump buffer as normal paragraph
                if code_buffer:
                    code_text = '\n'.join(code_buffer)
                    current = add_paragraph_after(doc, current, code_text, 'Normal')
                    code_buffer = []
                in_code_block = False
                i += 1
                continue
            else:
                in_code_block = True
                i += 1
                continue
        
        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue
        
        # Skip the main title (# Manual de Usuario) and version table - they're in the doc intro
        if line.strip().startswith('# Manual de Usuario'):
            i += 1
            continue
        if line.strip().startswith('| Versión |'):
            # Skip version table header and separator
            i += 1
            if i < len(lines) and lines[i].strip().startswith('|---'):
                i += 1
            if i < len(lines) and lines[i].strip().startswith('|'):
                i += 1
            continue
        # Skip the index section
        if line.strip() == '## Índice':
            i += 1
            # Skip until next heading or ---
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith('## ') or next_line == '---' or next_line.startswith('# '):
                    break
                i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            current = add_empty_line_after(doc, current)
            i += 1
            continue
        
        # Headers
        if line.strip().startswith('#### '):
            text = line.strip().replace('#### ', '').strip()
            current = add_empty_line_after(doc, current)
            current = add_heading_after(doc, current, text, 4)
            i += 1
            continue
        
        if line.strip().startswith('### '):
            text = line.strip().replace('### ', '').strip()
            current = add_empty_line_after(doc, current)
            current = add_heading_after(doc, current, text, 3)
            i += 1
            continue
        
        if line.strip().startswith('## '):
            text = line.strip().replace('## ', '').strip()
            current = add_empty_line_after(doc, current)
            # Level 2 heading - map to Heading 2
            current = add_heading_after(doc, current, text, 2)
            i += 1
            continue
        
        if line.strip().startswith('# '):
            text = line.strip().replace('# ', '').strip()
            current = add_empty_line_after(doc, current)
            current = add_heading_after(doc, current, text, 1)
            i += 1
            continue
        
        # Tables
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # Check if it's a table separator row
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                i += 1
                continue
            
            # It's a data row
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            
            if not in_table:
                # First row is header
                table_headers = cells
                in_table = True
            else:
                table_rows.append(cells)
            
            i += 1
            # Check if next line is also a table row
            if i >= len(lines) or not (lines[i].strip().startswith('|') and lines[i].strip().endswith('|')):
                # End of table - render it
                if table_headers:
                    current = add_empty_line_after(doc, current)
                    current = add_table_after(doc, current, table_headers, table_rows)
                    current = add_empty_line_after(doc, current)
                table_headers = []
                table_rows = []
                in_table = False
            continue
        
        # Blockquotes
        if line.strip().startswith('> '):
            text = line.strip()[2:].strip()
            # Accumulate blockquote lines
            bq_lines = [text]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('> '):
                bq_lines.append(lines[i].strip()[2:].strip())
                i += 1
            combined = ' '.join(bq_lines)
            current = add_paragraph_after(doc, current, f'➤ {combined}', 'Normal')
            continue
        
        # Unordered lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:].strip()
            # Handle bold in list items
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # remove bold markers
            current = add_list_item_after(doc, current, text)
            i += 1
            continue
        
        # Ordered lists
        if re.match(r'^\d+\.\s', line.strip()):
            text = re.sub(r'^\d+\.\s+', '', line.strip())
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            current = add_list_item_after(doc, current, text)
            i += 1
            continue
        
        # Empty line
        if line.strip() == '':
            current = add_empty_line_after(doc, current)
            i += 1
            continue
        
        # Regular paragraph - handle inline formatting
        text = line.strip()
        if text:
            # Handle bold
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            current = add_paragraph_after(doc, current, text, 'Normal')
        
        i += 1
    
    return current

print("🔄 Convirtiendo Manual de Usuario a formato DOCX...")
current_d = parse_md_to_docx(doc, current_d, md_lines)

print("✅ Apéndice D agregado correctamente")

# ─── Save ──────────────────────────────────────────────────────────────────────

print(f"💾 Guardando documento...")
doc.save(DOCX_PATH)
print("✅ Documento guardado exitosamente")
print(f"   {DOCX_PATH}")
