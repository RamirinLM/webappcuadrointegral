# Manual de Usuario — CMI GAD Municipal de Celica

**Sistema de Gestión Integral de Proyectos**

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 1.0 | Junio 2026 | Versión inicial |

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Interfaz General](#3-interfaz-general)
4. [Roles de Usuario](#4-roles-de-usuario)
5. [Tablero de Control](#5-tablero-de-control)
6. [Gestión de Proyectos](#6-gestión-de-proyectos)
   - 6.1. Listado de Proyectos
   - 6.2. Creación de Proyectos (Wizard de 7 Pasos)
   - 6.3. Detalle de Proyecto
   - 6.4. Edición de Proyectos
   - 6.5. Eliminación de Proyectos
7. [Acta de Constitución](#7-acta-de-constitución)
8. [Actividades](#8-actividades)
9. [Hitos](#9-hitos)
10. [Interesados (Stakeholders)](#10-interesados-stakeholders)
11. [Riesgos](#11-riesgos)
12. [Recursos](#12-recursos)
13. [Seguimiento y Valor Ganado (EVM)](#13-seguimiento-y-valor-ganado-evm)
    - 13.1. Línea Base y Seguimiento
    - 13.2. Cortes del Proyecto
    - 13.3. Curvas S
14. [Resumen Financiero](#14-resumen-financiero)
15. [Reportes](#15-reportes)
    - 15.1. Diagrama de Gantt
    - 15.2. Informe de Progreso
    - 15.3. Informe de Costos
    - 15.4. Informe de Estado
    - 15.5. Calendario
    - 15.6. Gráficos de Rendimiento
    - 15.7. Exportación CSV
16. [Solicitudes de Cambio](#16-solicitudes-de-cambio)
17. [Notificaciones](#17-notificaciones)
18. [Gestión de Usuarios](#18-gestión-de-usuarios)
19. [Glosario](#19-glosario)
20. [Solución de Problemas Comunes](#20-solución-de-problemas-comunes)

---

## 1. Introducción

**CMI Celica** (Cuadro de Mando Integral) es un sistema web desarrollado para el **GAD Municipal de Celica** que permite administrar, dar seguimiento y generar reportes de los proyectos institucionales.

El sistema está diseñado para que los funcionarios municipales puedan:

- **Planificar** proyectos desde cero con un asistente paso a paso.
- **Ejecutar** el seguimiento de actividades y costos.
- **Controlar** el avance mediante indicadores de Valor Ganado (EVM).
- **Reportar** el estado de los proyectos con gráficos, diagramas y exportaciones.

---

## 2. Acceso al Sistema

### 2.1. Iniciar Sesión

1. Abre tu navegador web (Chrome, Firefox, Edge).
2. Ingresa la dirección del sistema (ej: `http://cmi.celica.gob.ec`).
3. En la pantalla de **Inicio de Sesión**:
   - **Usuario**: tu nombre de usuario institucional.
   - **Contraseña**: tu contraseña asignada.
4. Haz clic en **Ingresar**.

> Si ves el mensaje *"Usuario o contraseña no válidos"*, verifica que tus datos sean correctos o contacta al administrador del sistema.

### 2.2. Cerrar Sesión

1. En la barra lateral izquierda, al final, encuentras el panel de usuario.
2. Haz clic en **Cerrar sesión**.

### 2.3. Recuperar Contraseña

Si olvidaste tu contraseña, contacta al **Jefe Departamental** o al administrador del sistema para que te asignen una nueva.

---

## 3. Interfaz General

Una vez que inicias sesión, el sistema se organiza en cuatro áreas principales:

### 3.1. Barra Lateral (Sidebar)

Color celeste, ubicada a la izquierda. Contiene:

- **Marca del sistema**: logotipo + "CMI Celica — Gestión integral de proyectos".
- **Sección Operación**:
  - *Tablero* — vista principal con resumen de proyectos.
  - *Proyectos* — listado completo.
  - *Nuevo proyecto* — asistente de creación.
  - *Seguimiento* — acceso a la línea base de todos los proyectos.
- **Sección Control**:
  - *Reportes* — todos los informes disponibles.
  - *Solicitudes de cambio* — gestión de cambios.
  - *Notificaciones* — centro de alertas.
  - *Usuarios* — solo visible para Jefes Departamentales.
- **Panel de usuario**: tu nombre, rol activo y botón *Cerrar sesión*.

> En pantallas angostas (menos de 992px), la barra lateral se oculta y aparece un botón **Menú** que la despliega.

### 3.2. Barra Superior (Topbar)

Color amarillo pálido translúcido. Muestra:

- **Título** de la página actual (ej: "Tablero de control").
- **Descripción breve** de la página.
- **Badges** con tu rol y la versión del sistema.

### 3.3. Área de Contenido

Ocupa el centro de la pantalla. Allí se muestran tablas, formularios, gráficos y tarjetas según la página que estés visitando.

### 3.4. Pie de Página (Footer)

Texto institucional: *"GAD Municipal de Celica | Plataforma de gestión de proyectos"*.

---

## 4. Roles de Usuario

El sistema tiene tres roles que determinan lo que puedes ver y hacer:

| Rol | Permisos |
|-----|----------|
| **Jefe Departamental** | Acceso total. Puede ver todos los proyectos, crear/editar/eliminar cualquier proyecto, gestionar usuarios, aprobar/rechazar solicitudes de cambio. |
| **Gestor de Proyectos** | Puede crear y gestionar sus propios proyectos, ver todos los proyectos, pero no puede gestionar usuarios ni aprobar cambios. |
| **Técnico de Proyectos** | Puede ver los proyectos a los que está asignado y colaborar en actividades. |

Tu rol aparece en la barra superior (badge) y en el panel inferior de la barra lateral.

---

## 5. Tablero de Control

**Ruta**: `Tablero` (primer enlace del menú lateral).

Es la pantalla principal que ves al iniciar sesión. Te da un **resumen operativo** de todos los proyectos.

### ¿Qué ves?

1. **Saludo personalizado**: "Bienvenido, [tu nombre]".
2. **Acciones rápidas**: botones *Nuevo proyecto* y *Seguimiento por proyecto*.
3. **Tarjetas de métricas** (tres indicadores):
   - *Proyectos activos* — cantidad total de proyectos en curso.
   - *Tareas pendientes* — actividades sin completar.
   - *Reportes recientes* — seguimientos registrados.
4. **Tabla "Estado de proyectos"**: cada proyecto muestra:
   - Nombre y fechas.
   - **Semáforo** 🟢🟡🔘:
     - **Verde** = proyecto en línea (SPI ≥ 0.95 y CPI ≥ 0.95).
     - **Amarillo** = necesita atención.
     - **Rojo** = crítico.
     - **Gris** = sin datos de seguimiento.
   - **Estado** del proyecto (Planificación, En Progreso, Completado, etc.).
   - **Avance** — barra de progreso con porcentaje.
   - **Presupuesto** — barra de uso presupuestario (verde ≤ 75%, amarillo 75-90%, rojo > 90%).
   - **Acciones**: botones *Detalle* y *Finanzas*.
5. **Panel lateral**:
   - *Tareas pendientes*: hasta 5 actividades sin completar.
   - *Últimos reportes*: seguimientos recientes.

---

## 6. Gestión de Proyectos

### 6.1. Listado de Proyectos

**Ruta**: `Proyectos` en el menú lateral.

Muestra todos los proyectos visibles para tu rol:

- **Jefe Departamental**: ve todos los proyectos del sistema.
- **Gestor/Técnico**: ve solo los proyectos donde participa.

Cada fila muestra: nombre (con descripción truncada), estado, fechas, creador por (solo Jefe), y acciones (Detalle, Editar, Eliminar).

Botones disponibles: **Seguimiento** (acceso rápido) y **Crear proyecto**.

### 6.2. Creación de Proyectos (Wizard de 7 Pasos)

**Ruta**: `Nuevo proyecto` en el menú lateral.

El asistente guía la creación completa de un proyecto en **7 pasos**. Puedes navegar hacia adelante y atrás sin perder datos.

> **Importante**: El proyecto se crea en la base de datos recién en el **Paso 2**. Si cancelas antes, no queda registro.

#### Paso 1: Datos del Proyecto

Completa los datos generales:

| Campo | Descripción |
|-------|-------------|
| **Nombre del Proyecto** | Nombre identificatorio (obligatorio). |
| **Descripción** | Explicación breve del proyecto. |
| **Fecha de Inicio** | Cuándo arranca el proyecto. |
| **Fecha de Fin** | Cuándo termina. |
| **Presupuesto Estimado** | Monto total disponible en dólares. |

> La fecha de inicio no puede ser posterior a la fecha de fin.

#### Paso 2: Acta de Constitución

**Acá es donde se crea el proyecto en el sistema.** Completa:

| Campo | Descripción |
|-------|-------------|
| **Alcance del Proyecto** | Qué incluye y qué excluye el proyecto. |
| **Entregables** | Productos o servicios que se entregarán. |
| **Justificación** | Por qué es necesario el proyecto. |
| **Objetivos** | Metas medibles del proyecto. |

#### Paso 3: Interesados (Stakeholders)

Identifica las personas o grupos involucrados:

1. **Selecciona interesados existentes** marcando los checkboxes.
2. **Agrega nuevos interesados** completando: Nombre, Email, Rol (Gerente de Proyecto, Miembro del Equipo, Cliente, Patrocinador, Otro), Nivel de Interés (Bajo/Medio/Alto), Nivel de Poder (Bajo/Medio/Alto), Información de Contacto.

> La **Matriz Poder-Interés** te ayuda a visualizar la estrategia de gestión para cada interesado.

#### Paso 4: Alcance Detallado

| Campo | Descripción |
|-------|-------------|
| **Descripción del Alcance** | Límites, restricciones, supuestos y criterios de aceptación. |
| **Objetivos Específicos** | Metas medibles y verificables del proyecto. |

#### Paso 5: Riesgos y Comunicación

**Riesgos**: identifica eventos que podrían afectar el proyecto:

- **Descripción** del riesgo.
- **Probabilidad** (Baja, Media, Alta).
- **Impacto** (Bajo, Medio, Alto).
- **Identificado por** — se autocompleta con tu nombre.
- **Plan de Mitigación** — qué hacer si ocurre.

**Plan de Comunicación**:

| Campo | Descripción |
|-------|-------------|
| **Tipo** | Email, Reunión, Llamada, Reporte. |
| **Frecuencia** | Diaria, Semanal, Quincenal, Mensual. |
| **Destinatario** | Nombre del interesado. |
| **Descripción** | Detalle de la comunicación. |

> Si un riesgo tiene probabilidad o impacto "Alto", se genera automáticamente una **notificación** para el creador del proyecto.

#### Paso 6: Actividades y Recursos

Agrega las actividades del proyecto:

**Datos de la actividad**:
- Nombre, Descripción, Fechas (dentro del rango del proyecto).
- **Actividad Predecesora**: selecciona qué actividad debe completarse antes.
- **Costo**: se calcula automáticamente desde los recursos.

**Recursos de la actividad**:
- Nombre, Tipo (Humano, Material, Equipo, Financiero).
- Cantidad y Costo por Unidad.
- El **Costo Total** se calcula automáticamente (cantidad × costo unitario).

> Las fechas de las actividades deben estar dentro del rango de fechas del proyecto.

#### Paso 7: Hitos

Define los hitos del proyecto:

| Campo | Descripción |
|-------|-------------|
| **Nombre del Hito** | Evento significativo. |
| **Fecha Límite** | Fecha tope. |
| **Fase** | Inicio, Planificación, Ejecución, Monitoreo y Control, Cierre. |
| **Descripción** | Detalle del hito. |
| **Es Cierre de Fase** | Marca si marca el final de una fase. |
| **Actividades Asociadas** | Selecciona las actividades relacionadas. |

Al hacer clic en **Finalizar proyecto**, el proyecto se completa y te redirige al detalle del proyecto.

### 6.3. Detalle de Proyecto

**Ruta**: haciendo clic en *Detalle* desde el listado o tablero.

Es la página más completa. Muestra:

1. **Cabecera**: nombre, semáforo, estado y botones de acción (Editar, Línea Base, Cortes, Curvas S, Resumen Financiero).
2. **Métricas** (6 tarjetas): Progreso (%), Presupuesto ($), Costo Planificado, Costo Real, Desviación de Presupuesto, Desviación de Ejecución.
3. **Información General**: estado, creador, fechas, presupuesto, costos, desviaciones, uso de presupuesto, estado CMI.
4. **Acta de Constitución**: alcance, entregables, justificación, objetivos. Puedes crear o editar el acta desde acá.
5. **Alcance Detallado** (si existe).
6. **Interesados** (si existen).
7. **Riesgos** (si existen).
8. **Plan de Comunicación** (si existe).
9. **Actividades**: tabla completa con fechas planificadas y reales, costos, variaciones y recursos.
10. **Hitos**: tabla con nombre, fase, fecha y estado.

### 6.4. Edición de Proyectos

**Ruta**: *Editar* desde el listado o *Editar proyecto* desde el detalle.

Se abre el mismo asistente de 7 pasos con todos los datos precargados. Puedes modificar cualquier paso y guardar los cambios.

### 6.5. Eliminación de Proyectos

**Ruta**: *Eliminar* desde el listado o desde el pie del detalle.

El sistema te pide confirmación antes de eliminar. **Esta acción no se puede deshacer** — se elimina el proyecto con toda su información asociada (actividades, hitos, riesgos, etc.).

---

## 7. Acta de Constitución

El acta es el **documento fundacional** del proyecto. Puedes crearla o editarla desde el detalle del proyecto.

Campos:
- **Alcance**: qué incluye y qué excluye.
- **Entregables**: productos/servicios a entregar.
- **Justificación**: propósito del proyecto.
- **Objetivos**: metas medibles.

> Cada proyecto puede tener **una sola** acta de constitución.

---

## 8. Actividades

### 8.1. Listado de Actividades

**Ruta**: desde el detalle del proyecto, sección Actividades.

Muestra todas las actividades del proyecto con: nombre, estado, fechas planificadas y reales, costos, variaciones (en días y en costo), recursos asociados.

### 8.2. Crear / Editar Actividad

**Ruta**: *Nueva actividad* o *Editar* desde el detalle.

El formulario tiene dos secciones:

1. **Planificación (Línea Base)**: datos que definen lo planificado. No cambian durante el seguimiento.
   - Nombre, Descripción, Estado, Asignado a.
   - Actividad Predecesora.
   - Fecha inicio, Fecha fin, Costo, Tiempo estimado.

2. **Ejecución Real (Seguimiento)**: datos de lo que realmente ocurrió.
   - Fecha inicio real, Fecha fin real, Costo real.

> La variación entre lo planificado y lo real se calcula automáticamente.

### 8.3. Asignar Actividad

**Ruta**: *Asignar* desde el listado de actividades.

Puedes asignar la actividad a un usuario del sistema para que quede como responsable.

---

## 9. Hitos

### 9.1. Listado de Hitos

**Ruta**: desde el detalle del proyecto, sección Hitos.

Muestra nombre, fase, fecha límite y estado (Completado/Pendiente).

### 9.2. Crear / Editar Hito

**Ruta**: *Nuevo hito* o *Editar*.

Campos:
- **Nombre**: identificador del hito.
- **Descripción**: detalle.
- **Proyecto**: se asigna automáticamente.
- **Fase**: Inicio, Planificación, Ejecución, Monitoreo y Control, Cierre.
- **Fecha Límite**: fecha tope para cumplir el hito.
- **Completado**: marca si ya se cumplió.
- **Es Cierre de Fase**: indica si marca el final de una fase.
- **Actividades Asociadas**: selecciona las actividades relacionadas.

---

## 10. Interesados (Stakeholders)

### 10.1. Listado de Interesados

**Ruta**: menú lateral (si está disponible) o desde el detalle del proyecto.

Muestra todos los interesados registrados: nombre, nivel de interés, cargo, email, y acciones (Editar, Eliminar).

### 10.2. Crear / Editar Interesado

Campos:
- **Nombre** (obligatorio)
- **Email** (obligatorio)
- **Rol**: Gerente de Proyecto, Miembro del Equipo, Cliente, Patrocinador, Otro.
- **Información de Contacto**.
- **Nivel de Interés**: Bajo, Medio, Alto.
- **Nivel de Poder**: Bajo, Medio, Alto.
- **Proyectos Asociados**: selecciona uno o más proyectos.

### 10.3. Feedback de Interesados

Puedes registrar retroalimentación de los interesados:

1. **Nuevo feedback**: selecciona el interesado, el proyecto, la calificación (1 a 5) y comentarios.
2. El listado muestra calificación, comentarios y fecha.

---

## 11. Riesgos

### 11.1. Listado de Riesgos

**Ruta**: menú lateral (si está disponible) o desde el detalle del proyecto.

Muestra todos los riesgos: descripción, proyecto, probabilidad, impacto, estado (Identificado, Mitigado, Ocurrido), y acciones.

### 11.2. Crear / Editar Riesgo

Campos:
- **Proyecto** (obligatorio).
- **Descripción**: detalle del riesgo.
- **Probabilidad**: Baja, Media, Alta.
- **Impacto**: Bajo, Medio, Alto.
- **Estado**: Identificado, Mitigado, Ocurrido.
- **Plan de Mitigación**: acciones para reducir el impacto.
- **Identificado por**: quién identificó el riesgo.

> Los riesgos con probabilidad o impacto **Alto** generan una notificación automática al creador del proyecto.

---

## 12. Recursos

### 12.1. Listado de Recursos

**Ruta**: menú lateral (si está disponible).

Muestra todos los recursos: nombre, proyecto, actividad asociada, tipo, cantidad, costo total.

### 12.2. Crear / Editar Recurso

Campos:
- **Actividad** (obligatorio): selecciona la actividad a la que pertenece.
- **Nombre**: identificador del recurso.
- **Tipo**: Humano, Material, Equipo, Financiero, Otro.
- **Cantidad**: número de unidades.
- **Costo por Unidad**: valor unitario en dólares.
- **Descripción**: detalle del recurso.

> El **costo total** se calcula automáticamente como cantidad × costo por unidad. Al guardar o eliminar un recurso, el costo de la actividad se actualiza automáticamente.

---

## 13. Seguimiento y Valor Ganado (EVM)

El sistema utiliza la metodología de **Valor Ganado (Earned Value Management — EVM)** para medir el desempeño del proyecto. Esto permite saber objetivamente si el proyecto está adelantado o atrasado, y si está por debajo o por encima del presupuesto.

### 13.1. Línea Base y Seguimiento

**Ruta**: *Línea base y seguimiento* desde el detalle del proyecto.

Esta página te permite registrar el **avance real** de las actividades en una fecha de corte determinada.

#### Cómo usarla:

1. **Selecciona la Fecha de Corte**: la fecha hasta la cual estás reportando.
2. **Completa los datos reales** de cada actividad:
   - *Fecha de inicio real*.
   - *Fecha de fin real*.
   - *Costo real*.
3. El sistema calcula automáticamente:
   - **Variación en días**: verde si terminaste antes, rojo si te atrasaste.
   - **Variación en costo**: verde si gastaste menos, rojo si gastaste más.
   - **Escenario**: "A tiempo", "Atrasado", "Adelantado", etc.
4. **Agrega observaciones** si es necesario.
5. Haz clic en **Guardar seguimiento**.

> Las actividades completadas se marcan con borde verde automáticamente al ingresar la fecha de fin real.

#### Métricas calculadas automáticamente:

| Sigla | Nombre | Qué significa |
|-------|--------|---------------|
| **PV** | Planned Value | Costo planificado de las actividades que debían estar terminadas al corte. |
| **EV** | Earned Value | Costo planificado de las actividades que YA terminaron al corte. |
| **AC** | Actual Cost | Costo REAL de las actividades completadas al corte. |
| **SV** | Schedule Variance | EV − PV. Positivo → adelantado. Negativo → atrasado. |
| **CV** | Cost Variance | EV − AC. Positivo → gastando menos. Negativo → gastando más. |
| **SPI** | Schedule Performance Index | EV / PV. ≥ 1 → vamos bien. < 1 → atrasados. |
| **CPI** | Cost Performance Index | EV / AC. ≥ 1 → vamos bien. < 1 → sobrecosto. |

### 13.2. Cortes del Proyecto

**Ruta**: *Cortes del proyecto* desde el detalle del proyecto.

Los cortes son **períodos de revisión** (semanales, quincenales, mensuales, etc.) que dividen la línea de tiempo del proyecto.

#### Cómo configurar los cortes:

1. Ingresa el **intervalo en días**:
   - 7 = semanal
   - 15 = quincenal
   - 30 = mensual
   - 90 = trimestral
2. Haz clic en **Generar cortes**.

La página muestra una tabla con cada período de revisión, incluyendo:
- Costo Planificado (PV), Valor Ganado (EV), Costo Real (AC).
- SPI y CPI con colores (verde ≥ 1, amarillo ≥ 0.85, rojo < 0.85).
- Estado del período: "En línea", "Atención" o "Crítico".

> Puedes expandir cada corte para ver el detalle de actividades. Si tienes permiso, también puedes editar o eliminar cortes.

### 13.3. Curvas S

**Ruta**: *Curvas S* desde el detalle del proyecto.

Gráfico que muestra la evolución de los costos acumulados a lo largo del tiempo:

- **PV (Planificado)**: línea azul punteada.
- **EV (Valor Ganado)**: línea verde sólida.
- **AC (Costo Real)**: línea roja sólida.

**Interpretación**:
- Si EV está **por encima** de PV → proyecto **adelantado** (vamos más rápido de lo planificado).
- Si EV está **por debajo** de PV → proyecto **atrasado**.
- Si AC está **por encima** de EV → estamos **gastando más** de lo que avanzamos.
- Si AC está **por debajo** de EV → estamos **gastando menos** de lo que avanzamos.

> El sistema genera una interpretación automática en texto debajo del gráfico.

---

## 14. Resumen Financiero

**Ruta**: *Resumen financiero* desde el detalle del proyecto.

Muestra un panel con:

1. **Tres métricas principales**:
   - Presupuesto Total.
   - Costo Planificado (actividades).
   - Costo Real ejecutado.
2. **Variación presupuestaria**: barra de consumo con color:
   - Verde ≤ 80% del presupuesto.
   - Amarillo 80–100%.
   - Rojo > 100% (sobrepresupuesto).
3. **Desglose por actividad**: tabla con costo planificado, real y variación de cada actividad.

---

## 15. Reportes

**Ruta**: `Reportes` en el menú lateral.

La página de reportes te permite acceder a **7 tipos de informes** por proyecto. Puedes filtrar por estado del proyecto, responsable y rango de fechas.

### 15.1. Diagrama de Gantt

Muestra el cronograma visual del proyecto:

- **Barras**: cada actividad como una barra coloreada según su estado (gris = pendiente, amarillo = en progreso, verde = completada).
- **Hitos**: rombos rojos o verdes.
- **Camino Crítico**: actividades críticas resaltadas con borde rojo. Si una actividad del camino crítico se atrasa, todo el proyecto se atrasa.
- **Dependencias**: flechas que conectan actividades predecesoras con sus sucesoras.
- **Línea de "Hoy"**: marca vertical roja que indica la fecha actual.

> Puedes hacer scroll horizontal para ver períodos largos y pasar el mouse sobre las barras para ver detalles.

### 15.2. Informe de Progreso

Resumen simple con tres indicadores:
- Nombre del proyecto.
- Porcentaje de avance general.
- Cantidad de actividades completadas vs total.

### 15.3. Informe de Costos

Muestra el costo total del proyecto y un detalle por actividad.

### 15.4. Informe de Estado

Panel completo con:
- **Progreso** general.
- **Costo planificado** vs **costo actual**.
- **Diferencia de tiempo** (días reales vs planificados).
- Tabla detallada por actividad con todas las métricas.

### 15.5. Calendario

Vista de calendario interactivo con **FullCalendar**:

- **Actividades**: bloques azules que abarcan desde la fecha de inicio hasta la fecha de fin.
- **Hitos**: marcadores rojos en la fecha correspondiente.

Puedes cambiar entre vista **Mes**, **Semana** y **Lista**, y navegar entre meses con los botones < >.

### 15.6. Gráficos de Rendimiento

Dos gráficos generados con **Chart.js**:

1. **Gráfico de pastel**: distribución del estado de actividades (Pendiente, En Progreso, Completada).
2. **Gráfico de barras**: costos por actividad.

### 15.7. Exportación CSV

Genera un archivo CSV (compatible con Excel) con todas las actividades del proyecto filtradas. Ideal para procesamiento externo.

---

## 16. Solicitudes de Cambio

### 16.1. Listado

**Ruta**: `Solicitudes de cambio` en el menú lateral.

Muestra todas las solicitudes de cambio con: proyecto, solicitante, descripción, estado (Pendiente/Aprobado/Rechazado), impacto y fecha.

### 16.2. Crear Solicitud de Cambio

Completa:
- **Proyecto**: al que aplica el cambio.
- **Descripción del Cambio**: qué se quiere cambiar.
- **Justificación**: por qué es necesario.
- **Impacto**: efecto esperado del cambio.

### 16.3. Aprobar / Rechazar

Solo el **Jefe Departamental** puede aprobar o rechazar solicitudes pendientes. Los botones aparecen directamente en el listado.

---

## 17. Notificaciones

### 17.1. Centro de Alertas

**Ruta**: `Notificaciones` en el menú lateral.

Muestra todas las alertas del sistema en formato de tarjetas:

- **No leídas**: tienen borde amarillo de advertencia.
- Cada tarjeta muestra: proyecto, tipo de alerta (Riesgo, Costo, Cronograma, General), mensaje completo, fecha y estado (Leída/Pendiente).

### 17.2. Detalle de Notificación

Haciendo clic en una notificación puedes:
- Ver el mensaje completo.
- **Marcar como leída**.
- Ir al proyecto relacionado.

---

## 18. Gestión de Usuarios

**Ruta**: `Usuarios` en el menú lateral (visible solo para **Jefes Departamentales**).

### 18.1. Listado de Usuarios

Muestra todos los usuarios del sistema con: nombre de usuario, nombre completo, email, rol y estado (Activo/Inactivo).

### 18.2. Crear / Editar Usuario

Puedes crear nuevos usuarios o editar los existentes. Campos principales:
- Datos personales (nombre, apellido, email).
- Credenciales de acceso (usuario, contraseña).
- **Rol**: Jefe Departamental, Gestor de Proyectos, Técnico de Proyectos.
- **Estado**: Activo o Inactivo.

> Solo el Jefe Departamental puede gestionar usuarios.

---

## 19. Glosario

| Término | Definición |
|---------|------------|
| **AC** | Actual Cost — Costo real incurrido en las actividades completadas. |
| **Acta de Constitución** | Documento formal que autoriza la existencia del proyecto. |
| **Camino Crítico** | Secuencia de actividades que determina la duración total del proyecto. Cualquier retraso en una actividad crítica retrasa todo el proyecto. |
| **CPI** | Cost Performance Index — Índice de desempeño del costo. Mide eficiencia de costos. |
| **Corte** | Período de revisión del proyecto (semanal, mensual, etc.). |
| **Curva S** | Gráfico que muestra la evolución acumulada de costos planificados vs reales. |
| **CV** | Cost Variance — Variación del costo. Diferencia entre valor ganado y costo real. |
| **EVM** | Earned Value Management — Metodología para medir desempeño del proyecto integrando alcance, tiempo y costos. |
| **EV** | Earned Value — Valor Ganado. Costo planificado del trabajo realmente completado. |
| **Hito** | Evento significativo en el proyecto, generalmente marca la finalización de una fase. |
| **Línea Base** | Plan original del proyecto (alcance, cronograma y costos) contra el que se mide el desempeño. |
| **Matriz Poder-Interés** | Herramienta para clasificar stakeholders según su nivel de poder e interés en el proyecto. |
| **PV** | Planned Value — Valor Planificado. Costo presupuestado del trabajo programado. |
| **Semáforo CMI** | Indicador visual (verde/amarillo/rojo) del estado general del proyecto basado en SPI y CPI. |
| **SPI** | Schedule Performance Index — Índice de desempeño del cronograma. Mide eficiencia del tiempo. |
| **Stakeholder** | Persona o grupo con interés en el proyecto (interesado). |
| **SV** | Schedule Variance — Variación del cronograma. Diferencia entre valor ganado y valor planificado. |
| **Wizard** | Asistente paso a paso para crear o editar proyectos. |

---

## 20. Solución de Problemas Comunes

### No puedo iniciar sesión
- Verifica que tu usuario y contraseña sean correctos.
- Si olvidaste tu contraseña, contacta al Jefe Departamental.
- El sistema distingue entre mayúsculas y minúsculas.

### No veo algunos proyectos
- Revisa tu rol en el panel de usuario. Si eres Técnico de Proyectos, solo ves los proyectos donde participas.
- Si deberías tener acceso, contacta al Jefe Departamental.

### No encuentro el botón para crear usuarios
- La gestión de usuarios solo está disponible para el rol **Jefe Departamental**.
- Si crees que deberías tener acceso, contacta al administrador.

### Los datos del wizard no se guardan
- El wizard guarda datos en tu sesión. Si cierras el navegador o pasas mucho tiempo inactivo, los datos se pierden.
- Completa el proceso sin interrupciones largas.
- El proyecto se crea definitivamente recién en el **Paso 2**.

### No aparecen las Curvas S
- Necesitas tener al menos un registro de seguimiento (Línea Base) para que el gráfico tenga datos.
- Ve a *Línea base y seguimiento* y registra al menos un corte.

### Las Curvas S se ven vacías
- El gráfico toma datos de los seguimientos registrados. Si no hay seguimientos, no hay curvas.
- Registra seguimientos en *Línea base y seguimiento* con diferentes fechas de corte.

### El semáforo está en gris
- Significa que el proyecto no tiene registros de seguimiento. El semáforo necesita datos EVM para calcular el estado.

### No puedo eliminar un proyecto
- Solo el creador del proyecto o un Jefe Departamental pueden eliminar proyectos.
- Si tienes permiso, el botón *Eliminar* aparece al final del detalle o en el listado.

### Error al guardar una actividad
- Verifica que:
  - Las fechas estén dentro del rango del proyecto.
  - La fecha de inicio no sea posterior a la fecha de fin.
  - El costo no exceda el presupuesto disponible del proyecto.
  - No se creen ciclos de dependencia (A depende de B y B depende de A).

### No se ven los reportes de un proyecto
- Los reportes se generan a partir de las actividades del proyecto. Si el proyecto no tiene actividades, los reportes estarán vacíos o mostrarán mensajes indicando la falta de datos.

### No puedo aprobar una solicitud de cambio
- Solo el **Jefe Departamental** tiene permiso para aprobar o rechazar solicitudes de cambio.
- Si tu rol es Jefe Departamental y no ves los botones, verifica que la solicitud esté en estado "Pendiente".

---

© 2026 GAD Municipal de Celica. Todos los derechos reservados.
