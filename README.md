# Sistema de Gestión de Proyectos - GAD Célica y CMI

Aplicación web para el **Sistema de Gestión de Proyectos del GAD Municipal de Célica** (cuadro de mando integral). Tema visual: **azul, amarillo y blanco**.

## Requerimientos implementados

### Gestión del proyecto (REQ-001, REQ-002)
- Registro y gestión de proyectos del Sistema de Gestión GAD Célica y CMI.
- Módulo de **interesados** con **matriz de poder/interés** (niveles Alto, Medio, Bajo).

### Autenticación (REQ-003)
- Acceso con usuario y contraseña en `/cuenta/entrar/`.
- Cierre de sesión en `/cuenta/salir/`.
- Vistas protegidas: solo usuarios autenticados acceden a Gestión de Proyectos, Línea Base, Seguimiento, Dashboard, Informes, Matriz, Alertas.

### Funcionales
- **REQ-004** Hitos: listado de hitos del proyecto (actividades marcadas como hito).
- **REQ-005 / REQ-016 / REQ-019** Costos y tiempos en actividades (cronograma, línea base).
- **REQ-006** Asignación de recursos a actividades (modelo y admin).
- **REQ-007** Líneas base: cronogramas por proyecto.
- **REQ-008** Riesgos del proyecto (registro y listado).
- **REQ-009** Informes: página de indicadores y estado del proyecto.
- **REQ-010** Plan de comunicación: interesados y registro de comunicaciones.
- **REQ-011** Seguimiento del progreso (app seguimiento, CPI/SPI, EVM).
- **REQ-012** Visualización de indicadores en Dashboard e Informes.
- **REQ-013** Adquisiciones: modelo y listado de seguimiento de adquisiciones.
- **REQ-014** Feedback de interesados: modelo y listado.
- **REQ-015** Alertas de riesgos: modelo y vista de alertas.

### No funcionales
- **RNF001** Seguridad: autenticación y control de acceso.
- **RNF002** Usabilidad: formularios y navegación con tema GAD (azul/amarillo/blanco).
- **RNF003–RNF006** Base para rendimiento, escalabilidad y mantenibilidad (Django estándar).
- **RNF007** Documentación: este README y comentarios en código.
- **RNF008** Accesibilidad: estilos de focus y contraste en `static/css/theme_gad_celica.css`.

## Cómo ejecutar

1. Activar el entorno con Django instalado.
2. Aplicar migraciones (incluye nuevos modelos y campos de interesados):
   ```bash
   python manage.py migrate
   ```
3. Crear un superusuario si no existe:
   ```bash
   python manage.py createsuperuser
   ```
4. Arrancar el servidor:
   ```bash
   python manage.py runserver
   ```
5. Abrir en el navegador: `http://127.0.0.1:8000/`
6. Entrar con el usuario creado en `/cuenta/entrar/` (o desde el enlace «Entrar» en la barra).

## Estructura de la aplicación

- **cuadrointegralsite**: configuración del proyecto, URLs globales, login/logout.
- **gestionproyecto**: proyectos, interesados (con poder/interés), actas, comunicaciones, riesgos, alcance, adquisiciones, feedback, alertas de riesgos.
- **lineabase**: cronogramas, actividades, recursos, hitos, líneas base.
- **seguimiento**: seguimiento por proyecto, CPI, SPI, valor ganado.
- **dashboard**: indicadores, proyectos, vista financiera.
- **static/css/theme_gad_celica.css**: hoja de estilos del tema GAD (azul, amarillo, blanco).

## Migración nueva (0002)

La migración `gestionproyecto/migrations/0002_interesado_nivel_adquisicion_feedback_alerta.py` añade:

- Campos `nivel_poder` y `nivel_interes` en **Interesado**.
- Modelos **Adquisicion**, **FeedbackInteresado**, **AlertaRiesgo**.

Si ya existían migraciones 0002, 0003, etc. en tu entorno, puede que tengas que renombrar esta migración (por ejemplo a 0005) para evitar conflictos de numeración.
