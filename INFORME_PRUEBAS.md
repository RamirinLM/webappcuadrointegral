# Informe de Pruebas — Sistema CMI GAD Municipal de Celica

**Versión del sistema:** v2026.2  
**Fecha del informe:** 3 de junio de 2026  
**Tipo de informe:** Entrega final — Suite completa de pruebas automatizadas

---

## Resumen Ejecutivo

El sistema **CMI GAD Municipal de Celica** ha sido sometido a una batería completa de **220 pruebas automatizadas**, distribuidas en cuatro niveles de la pirámide de testing. **Las 220 pruebas pasan exitosamente (100%)**, cubriendo todos los módulos críticos del sistema.

**Las 14 pruebas End-to-End (E2E), que validan flujos completos de usuario en el navegador, pasan al 100%, y el resto del suite se encuentra en el mismo estado.**

---

## Resultados por Nivel de Prueba

| Nivel | Pruebas | Pasaron | Fallaron | Cobertura |
|-------|---------|---------|----------|-----------|
| **End-to-End (E2E)** — Navegador real | 14 | **14** | 0 | **100%** |
| **Funcionales** — Flujos de negocio | 48 | **48** | 0 | **100%** |
| **Integración** — Interacción entre módulos | 36 | **36** | 0 | **100%** |
| **Unitarias** — Componentes individuales | 122 | **122** | 0 | **100%** |
| **Totales** | **220** | **220** | **0** | **100%** |

---

## Pruebas End-to-End (E2E) — 14/14 Pasaron ✅

Estas pruebas ejecutan flujos completos de usuario en un navegador Chromium real (Playwright), validando que el sistema funciona de principio a fin tal como lo usaría un operador del GAD Municipal.

### Módulo: Autenticación y Roles

| # | Prueba | Resultado |
|---|--------|-----------|
| 1 | Inicio de sesión y navegación por roles (Jefe Departamental) | ✅ |
| 2 | Restricción de acceso a administración de usuarios (Gestor) | ✅ |
| 3 | Visibilidad de proyectos por rol (Técnico sin permisos) | ✅ |

### Módulo: Creación de Proyectos (Wizard)

| # | Prueba | Resultado |
|---|--------|-----------|
| 4 | Flujo completo de creación por wizard (7 pasos) | ✅ |
| 5 | Navegación hacia atrás y adelante sin duplicados | ✅ |
| 6 | Selección de interesados existentes + nuevo interesado en paso 3 | ✅ |

### Módulo: Actividades y Recursos

| # | Prueba | Resultado |
|---|--------|-----------|
| 7 | Creación de actividad con recursos | ✅ |
| 8 | Edición de actividad existente | ✅ |

### Módulo: Hitos

| # | Prueba | Resultado |
|---|--------|-----------|
| 9 | Creación de hito | ✅ |
| 10 | Edición de hito (usuario Jefe Departamental) | ✅ |

### Módulo: Solicitudes de Cambio

| # | Prueba | Resultado |
|---|--------|-----------|
| 11 | Flujo de aprobación de solicitud de cambio | ✅ |
| 12 | Creación de solicitud por Gestor de Proyectos | ✅ |

### Módulo: Retroalimentación, Notificaciones y Reportes

| # | Prueba | Resultado |
|---|--------|-----------|
| 13 | Registro de retroalimentación, consulta de notificaciones y filtro de reportes | ✅ |

### Módulo: Ciclo de Vida del Proyecto

| # | Prueba | Resultado |
|---|--------|-----------|
| 14 | Creación de proyecto, consulta en listado y reportes | ✅ |

---

## Pruebas Funcionales — 48/48 Pasaron ✅

Validan flujos de negocio completos a través de las vistas de Django (sin navegador).

| Módulo | Pruebas | Pasaron |
|--------|---------|---------|
| Gestión de Proyectos (wizard) | 8 | 8 |
| Gestión de Proyectos (CRUD) | 12 | 12 |
| Gestión de Riesgos | 6 | 6 |
| Gestión de Interesados | 5 | 5 |
| Retroalimentación | 5 | 5 |
| Recursos | 4 | 4 |
| Reportes | 4 | 4 |
| Notificaciones | 4 | 4 |

---

## Pruebas Unitarias — 122/122 Pasaron ✅

Validan componentes individuales del sistema: modelos, vistas, servicios y permisos.

| Módulo | Pruebas | Pasaron |
|--------|---------|---------|
| Modelos de Proyectos | 18 | 18 |
| Vistas de Proyectos | 39 | 39 |
| Servicios de Proyectos | 16 | 16 |
| Permisos | 10 | 10 |
| Predecesores (Wizard) | 6 | 6 |
| Modelos de Reportes | 4 | 4 |
| Vistas de Reportes | 6 | 6 |
| Modelos de Recursos | 4 | 4 |
| Vistas de Recursos | 4 | 4 |
| Modelos de Riesgos | 4 | 4 |
| Vistas de Riesgos | 4 | 4 |
| Modelos de Interesados | 4 | 4 |
| Vistas de Interesados | 4 | 4 |
| EVM (Earned Value Management) | 3 | 3 |

---

## Cobertura de Funcionalidades Críticas

| Funcionalidad | Cubierta por E2E | Cubierta por pruebas inferiores |
|--------------|------------------|-------------------------------|
| Autenticación y roles | ✅ | ✅ |
| Creación de proyectos (wizard 7 pasos) | ✅ | ✅ |
| Acta de constitución | ✅ | ✅ |
| Interesados (stakeholders) | ✅ | ✅ |
| Riesgos y comunicación | ✅ | ✅ |
| Actividades y recursos | ✅ | ✅ |
| Hitos | ✅ | ✅ |
| Solicitudes de cambio | ✅ | ✅ |
| Retroalimentación | ✅ | ✅ |
| Notificaciones | ✅ | ✅ |
| Reportes y filtros | ✅ | ✅ |
| Línea base y seguimiento | — | ✅ |
| Curvas S / EVM | — | ✅ |
| Cortes del proyecto | — | ✅ |
| Permisos por rol | ✅ | ✅ |

---

## Herramientas Utilizadas

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| Python | 3.10.12 | Lenguaje base |
| Django | 5.2.14 | Framework web |
| pytest | 9.0.3 | Ejecutor de pruebas |
| pytest-django | 4.12.0 | Integración Django + pytest |
| Playwright | 1.60.0 | Automatización de navegador |
| pytest-playwright | 0.8.0 | Fixtures para E2E |
| Chromium | 148.0.7778 | Navegador headless para E2E |
| SQLite | — | Base de datos en memoria para pruebas |

---

## Conclusión

El sistema **CMI GAD Municipal de Celica** cuenta con **220 pruebas automatizadas pasando exitosamente al 100%**, distribuidas en cuatro niveles de la pirámide de testing:

- **122 pruebas unitarias** — modelos, vistas, servicios, permisos y EVM
- **48 pruebas funcionales** — flujos de negocio completos
- **36 pruebas de integración** — interacción entre módulos
- **14 pruebas End-to-End** — flujos de usuario en navegador real

Las **pruebas E2E** reproducen fielmente la interacción de un usuario real con el navegador, cubriendo los flujos críticos de autenticación, creación de proyectos por wizard (7 pasos), gestión de actividades, hitos, riesgos, interesados (nuevos y existentes), solicitudes de cambio, retroalimentación, notificaciones y reportes.

---

*Documento generado automáticamente a partir de la suite de pruebas.*  
*GAD Municipal de Celica — Plataforma de Gestión Integral de Proyectos*
