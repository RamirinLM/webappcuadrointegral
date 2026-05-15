"""
Población comprensiva de datos de prueba para todos los modelos y flujos.
Cubre: usuarios, proyectos, actas, actividades, hitos, seguimiento EVM,
stakeholders, feedback, recursos, riesgos, comunicaciones, solicitudes de
cambio, línea base, adquisiciones, cronograma, presupuesto y más.

Uso:
    ./manage.py populate_test_data
    ./manage.py populate_test_data --force   (limpia todo primero)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from projects.models import (
    Project, Activity, Milestone, UserProfile, ActaConstitucion,
    ProjectCut, Seguimiento, ChangeRequest, Baseline, Acquisition,
    Cronograma, Presupuesto, Alcance, Comunicacion, AutoCertificacion,
    Notification,
)
from projects.services import generate_project_cuts
from stakeholders.models import Stakeholder, Feedback
from resources.models import Resource
from risks.models import Risk
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba comprensivos"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Limpia datos existentes primero")

    # ── helpers ──────────────────────────────────────────────────────────

    def _create_user(self, username, password, first_name, last_name, email, role):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        if not created:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
        user.set_password(password)
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        self.log(f"Usuario {'creado' if created else 'actualizado'}: {username} / {password} (rol: {role})", "SUCCESS")
        return user

    def log(self, msg, style="SUCCESS"):
        getattr(self.style, style, self.style.SUCCESS)
        self.stdout.write(getattr(self.style, style, self.style.SUCCESS)(msg))

    # ── main ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]

        if force:
            self.stdout.write("Limpiando datos existentes...")
            # Orden inverso por dependencias
            Notification.objects.all().delete()
            Seguimiento.objects.all().delete()
            Resource.objects.all().delete()
            Risk.objects.all().delete()
            Feedback.objects.all().delete()
            ChangeRequest.objects.all().delete()
            Comunicacion.objects.all().delete()
            AutoCertificacion.objects.all().delete()
            Acquisition.objects.all().delete()
            Baseline.objects.all().delete()
            Cronograma.objects.all().delete()
            Presupuesto.objects.all().delete()
            Alcance.objects.all().delete()
            Milestone.objects.all().delete()
            Activity.objects.all().delete()
            ActaConstitucion.objects.all().delete()
            Stakeholder.objects.all().delete()
            Project.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        else:
            self.stdout.write("Usando --force para limpiar datos previos si es necesario.")
            Project.objects.filter(name__icontains="Prueba CMI").delete()
            Project.objects.filter(name__icontains="Planificacion").delete()
            Project.objects.filter(name__icontains="Ejemplo A").delete()
            Project.objects.filter(name__icontains="Ejemplo B").delete()

        # ═════════════════════════════════════════════════════════════════
        #  1. USUARIOS
        # ═════════════════════════════════════════════════════════════════
        # Usuario admin por defecto (rol jefe) — existe si se creó con createsuperuser
        admin = User.objects.filter(username="admin").first()
        if admin:
            profile, _ = UserProfile.objects.get_or_create(user=admin)
            profile.role = "jefe_departamental"
            profile.save()
            admin.set_password("password123")
            admin.save()
            self.log(f"Usuario existente 'admin' actualizado: rol=jefe_departamental", "SUCCESS")
        else:
            admin = self._create_user("admin", "password123", "Admin", "Sistema",
                                      "admin@example.com", "jefe_departamental")

        jefe = self._create_user("jefe", "password123", "Jefe", "Departamental",
                                 "jefe@example.com", "jefe_departamental")
        gestor = self._create_user("gestor", "password123", "Gestor", "Proyectos",
                                   "gestor@example.com", "gestor_proyectos")
        tecnico = self._create_user("tecnico", "password123", "Técnico", "Proyectos",
                                    "tecnico@example.com", "tecnico_proyectos")

        today = date.today()

        # ═════════════════════════════════════════════════════════════════
        #  2. PROYECTO A — EN EJECUCIÓN (con seguimiento EVM real)
        # ═════════════════════════════════════════════════════════════════
        p1_start = today - timedelta(days=60)
        p1_end = today + timedelta(days=120)

        p1 = Project.objects.create(
            name="Proyecto de Prueba CMI — Sistema de Gestión",
            description="Proyecto integral para desarrollar un sistema de gestión "
                        "de proyectos con seguimiento EVM, línea base y reportes.",
            start_date=p1_start, end_date=p1_end,
            status="in_progress", budget=85000.00, created_by=gestor,
        )

        # Acta
        ActaConstitucion.objects.create(
            proyecto=p1,
            alcance="Desarrollo completo de sistema de gestión de proyectos con "
                    "módulos de planificación, seguimiento EVM, reportes y riesgos.",
            entregables="Sistema web, API REST, documentación técnica, "
                        "manuales de usuario, datos de prueba.",
            justificacion="La organización necesita una herramienta centralizada "
                          "para gestionar su portafolio de proyectos.",
            objetivos="Implementar un sistema que permita planificar, hacer "
                      "seguimiento y reportar el estado de proyectos.",
        )

        self.log("Proyecto A creado: Sistema de Gestión", "SUCCESS")

        # ── Actividades del Proyecto A ─────────────────────────────
        acts_a = []
        defs_a = [
            # (nombre, offset_inicio, duración_días, estado, costo, inicio_real, fin_real, costo_real)
            ("Análisis de Requisitos",      0,  12, "completed",   5000,  p1_start,           p1_start + timedelta(days=13), 5200),
            ("Diseño de Arquitectura",     12,  15, "completed",   8000,  p1_start + timedelta(days=13), p1_start + timedelta(days=28), 7800),
            ("Desarrollo Frontend",        27,  30, "completed",  15000,  p1_start + timedelta(days=28), p1_start + timedelta(days=60), 16000),
            ("Desarrollo Backend",         30,  35, "in_progress", 20000,  p1_start + timedelta(days=35), None,  None),
            ("Pruebas Unitarias",          60,  12, "in_progress",  3500,  None, None, None),
            ("Pruebas de Integración",     72,  15, "pending",      4500,  None, None, None),
            ("Despliegue en Producción",   87,  10, "pending",      2500,  None, None, None),
            ("Capacitación de Usuarios",   97,   8, "pending",      3000,  None, None, None),
            ("Documentación Final",       105,  10, "pending",      2000,  None, None, None),
            # Actividad sin costo (para probar null handling)
            ("Revisión de Calidad",         60,   5, "pending",      None,  None, None, None),
        ]

        for idx, (name, off, dur, status, cost, a_start, a_end, a_cost) in enumerate(defs_a):
            act = Activity.objects.create(
                project=p1,
                name=name,
                description=f"Actividad: {name}",
                start_date=p1_start + timedelta(days=off),
                end_date=p1_start + timedelta(days=off + dur),
                status=status,
                cost=cost,
                actual_start_date=a_start,
                actual_end_date=a_end,
                actual_cost=a_cost,
                # Asignar usuarios
                assigned_to=tecnico if idx % 2 == 0 else gestor,
            )
            acts_a.append(act)

        # Predecesoras (cadena lineal + la revisión depende de pruebas unitarias)
        for i in range(1, 8):  # 1..7 dependen de la anterior
            acts_a[i].predecessor = acts_a[i - 1]
            acts_a[i].save()
        # Revisión de Calidad depende de Pruebas Unitarias
        acts_a[9].predecessor = acts_a[4]
        acts_a[9].save()

        # ── Hitos del Proyecto A ───────────────────────────────────
        milestones_a = [
            ("Inicio del Proyecto",         p1_start,                                             True,  "initiation", True),
            ("Req. Aprobados",              p1_start + timedelta(days=12),                        True,  "planning",   True),
            ("Diseño Completado",           p1_start + timedelta(days=27),                        True,  "planning",   True),
            ("Frontend Listo",              p1_start + timedelta(days=58),                        True,  "execution",  False),
            ("Backend Listo",               p1_start + timedelta(days=65),                        False, "execution",  False),
            ("Cierre de Sprint 1",          p1_start + timedelta(days=70),                        False, "execution",  True),
            ("Entrega a Producción",        p1_start + timedelta(days=97),                        False, "closure",    True),
            ("Cierre del Proyecto",         p1_end,                                              False, "closure",    True),
        ]
        for name, due, completed, phase, is_gate in milestones_a:
            m = Milestone.objects.create(
                project=p1, name=name, description=f"Hito: {name}",
                due_date=due, completed=completed, phase=phase, is_phase_gate=is_gate,
            )
            # Asociar actividades relevantes al hito
            if "Req" in name:
                m.activities.add(acts_a[0])
            elif "Diseño" in name:
                m.activities.add(acts_a[1])
            elif "Frontend" in name:
                m.activities.add(acts_a[2])
            elif "Backend" in name:
                m.activities.add(acts_a[3])

        self.log("Actividades y hitos del Proyecto A creados", "SUCCESS")

        # ── Seguimientos con EVM (se crean ANTES de actualizar fechas reales
        #    para que calculate_metrics() compute valores coherentes) ──
        seg_dates = [
            p1_start + timedelta(days=10),   # día 10
            p1_start + timedelta(days=20),   # día 20
            p1_start + timedelta(days=35),   # día 35
            p1_start + timedelta(days=50),   # día 50
            today,                            # hoy
        ]
        segments = []
        for sd in seg_dates:
            seg = Seguimiento(proyecto=p1, fecha=sd,
                              observacion=f"Seguimiento quincenal del {sd.strftime('%d/%m/%Y')}")
            seg.save()  # calculate_metrics() se llama automáticamente
            segments.append(seg)
            self.log(f"  Seguimiento {sd}: PV={seg.pv} EV={seg.ev} AC={seg.ac} "
                     f"SV={seg.sv} CV={seg.cv} SPI={seg.spi} CPI={seg.cpi}", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  3. PROYECTO B — EN PLANIFICACIÓN (sin seguimiento, para probar
        #     el estado "gray" del semáforo)
        # ═════════════════════════════════════════════════════════════════
        p2_start = today + timedelta(days=30)
        p2_end = p2_start + timedelta(days=180)

        p2 = Project.objects.create(
            name="Proyecto de Planificación — Nueva Sede",
            description="Proyecto en fase de planificación para la construcción "
                        "y equipamiento de una nueva sede operativa.",
            start_date=p2_start, end_date=p2_end,
            status="planning", budget=250000.00, created_by=gestor,
        )

        ActaConstitucion.objects.create(
            proyecto=p2,
            alcance="Planificación completa incluyendo estudio de factibilidad, "
                    "diseño arquitectónico, selección de terreno y presupuesto detallado.",
            entregables="Estudio de factibilidad, planos, presupuesto, cronograma maestro.",
            justificacion="La capacidad actual es insuficiente para la demanda proyectada.",
            objetivos="Completar la planificación para la nueva sede en 6 meses.",
        )

        # Actividades del proyecto B (solo planificadas, ninguna iniciada)
        acts_b = []
        for i, (name, offset, dur, cost) in enumerate([
            ("Estudio de Factibilidad",     0,  30,  15000),
            ("Selección de Terreno",       30,  20,   5000),
            ("Diseño Arquitectónico",      50,  45,  25000),
            ("Permisos Municipales",       95,  30,   3000),
            ("Licitación de Obra",        125,  25,   2000),
            ("Plan de Mudanza",           150,  20,   1000),
        ]):
            act = Activity.objects.create(
                project=p2,
                name=name,
                description=f"Actividad de planificación: {name}",
                start_date=p2_start + timedelta(days=offset),
                end_date=p2_start + timedelta(days=offset + dur),
                status="pending",
                cost=cost,
                assigned_to=tecnico,
            )
            acts_b.append(act)
        for i in range(1, len(acts_b)):
            acts_b[i].predecessor = acts_b[i - 1]
            acts_b[i].save()

        # Hitos del proyecto B
        for name, due, phase, is_gate in [
            ("Inicio Planificación",       p2_start,                  "initiation", True),
            ("Factibilidad Lista",         p2_start + timedelta(days=30), "planning", True),
            ("Diseño Aprobado",            p2_start + timedelta(days=95), "planning", True),
            ("Planificación Completa",     p2_end,                    "planning", True),
        ]:
            Milestone.objects.create(
                project=p2, name=name, description=f"Hito: {name}",
                due_date=due, completed=False, phase=phase, is_phase_gate=is_gate,
            )

        self.log("Proyecto B creado: Nueva Sede (planificación)", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  4. STAKEHOLDERS (compartidos entre proyectos)
        # ═════════════════════════════════════════════════════════════════
        stakeholders_data = [
            ("Juan Pérez",       "juan@example.com",    "manager",    "0987654321",  "high", "high"),
            ("María García",     "maria@example.com",   "team_member","0981122334",  "high", "medium"),
            ("Carlos López",     "carlos@example.com",  "client",     "0998877665",  "medium", "high"),
            ("Ana Martínez",     "ana@example.com",     "sponsor",    "0977766554",  "high", "high"),
            ("Luis Torres",      "luis@example.com",    "other",      "0966544332",  "low",  "low"),
        ]
        stakeholders = []
        for name, email, role, contact, interest, power in stakeholders_data:
            sh = Stakeholder.objects.create(
                name=name, email=email, role=role,
                contact_info=contact,
                interest_level=interest, power_level=power,
            )
            sh.projects.add(p1)
            sh.projects.add(p2)  # todos visibles en ambos proyectos
            stakeholders.append(sh)
            self.log(f"  Stakeholder: {name}", "SUCCESS")

        # ── Feedback ───────────────────────────────────────────────
        for sh, rating, comments in [
            (stakeholders[0], 4, "Buena comunicación, el equipo responde rápido."),
            (stakeholders[2], 5, "Muy satisfecho con el avance del proyecto."),
            (stakeholders[3], 3, "Esperaba más reportes de avance detallados."),
        ]:
            Feedback.objects.create(
                stakeholder=sh, project=p1, rating=rating, comments=comments,
            )
        self.log("Feedbacks creados", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  5. RECURSOS
        # ═════════════════════════════════════════════════════════════════
        resource_defs = [
            ("Desarrollador Frontend",  "human",     2,  50.00, acts_a[2]),
            ("Desarrollador Backend",   "human",     2,  55.00, acts_a[3]),
            ("Servidor de Desarrollo",  "equipment",  1, 200.00, acts_a[2]),
            ("Licencia IDE",            "material",   3,  30.00, acts_a[3]),
            ("Analista QA",             "human",      1,  45.00, acts_a[4]),
            ("Curso de Capacitación",   "financial",  1, 500.00, acts_a[7]),
            # Recurso sin actividad asociada (activity=None)
            ("Material de Oficina",     "material",  10,   5.00, None),
        ]
        for name, rtype, qty, cpu, activity in resource_defs:
            Resource.objects.create(
                name=name, type=rtype, quantity=qty,
                cost_per_unit=cpu, activity=activity,
                description=f"Recurso: {name}",
            )
        self.log("Recursos creados", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  6. RIESGOS
        # ═════════════════════════════════════════════════════════════════
        for desc, prob, impact, plan, status in [
            ("Retraso en entregas de terceros",  "medium", "high",
             "Monitoreo semanal y buffer de 5 días", "identified"),
            ("Cambios en requisitos del cliente", "high", "medium",
             "Reuniones de revisión cada 15 días", "identified"),
            ("Fuga de personal clave",            "low",   "high",
             "Documentación de conocimiento y backup", "mitigated"),
            ("Problemas de rendimiento en backend","medium","medium",
             "Pruebas de carga tempranas", "identified"),
            ("Corte de servicios en la nube",     "low",   "medium",
             "Plan de contingencia con servidor local", "mitigated"),
            # Riesgo ocurrido para probar status=occurred
            ("Retraso en licencias de software",  "medium", "low",
             "Se gestionó licencia temporal", "occurred"),
        ]:
            Risk.objects.create(
                project=p1, description=desc, probability=prob,
                impact=impact, mitigation_plan=plan, status=status,
                identified_by=gestor.username if prob == "high" else tecnico.username,
            )
        self.log("Riesgos creados", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  7. COMUNICACIONES
        # ═════════════════════════════════════════════════════════════════
        for tipo, msg, sh in [
            ("email",   "Envío de informe de avance semanal.",           stakeholders[2]),
            ("reunion", "Reunión de revisión de requisitos.",           stakeholders[0]),
            ("llamada", "Llamada para confirmar entregables.",          stakeholders[3]),
            ("email",   "Notificación de cambio de cronograma.",        stakeholders[1]),
        ]:
            Comunicacion.objects.create(
                proyecto=p1, interesado=sh, tipo=tipo, mensaje=msg,
            )
        self.log("Comunicaciones creadas", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  8. SOLICITUDES DE CAMBIO
        # ═════════════════════════════════════════════════════════════════
        ChangeRequest.objects.create(
            project=p1, requested_by=gestor,
            description="Agregar módulo de reportes comparativos multi-proyecto.",
            justification="El cliente solicita visión consolidada de todos los proyectos.",
            impact="Alto: requiere 2 semanas adicionales de desarrollo.",
            status="pending",
        )
        ChangeRequest.objects.create(
            project=p1, requested_by=tecnico,
            description="Actualizar librería de gráficos a versión 4.x.",
            justification="La versión actual tiene vulnerabilidades de seguridad.",
            impact="Medio: puede requerir actualización de dependencias.",
            status="approved",
        )
        self.log("Solicitudes de cambio creadas", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  9. LÍNEA BASE, ADQUISICIONES, CRONOGRAMA, PRESUPUESTO, ALCANCE
        # ═════════════════════════════════════════════════════════════════
        Baseline.objects.create(
            project=p1,
            scope_baseline="Alcance: sistema de gestión con módulos de proyecto, "
                           "actividad, seguimiento EVM, reportes, riesgos y recursos.",
            schedule_baseline=f"Cronograma: {p1_start} a {p1_end} (180 días calendario).",
            cost_baseline=85000.00,
        )
        self.log("Línea base creada", "SUCCESS")

        Acquisition.objects.create(
            project=p1, item="Servidor de Producción",
            description="Servidor dedicado para despliegue del sistema.",
            quantity=1, estimated_cost=3000.00, status="planned",
        )
        Acquisition.objects.create(
            project=p1, item="Licencias Anuales",
            description="Licencias de software corporativo.",
            quantity=5, estimated_cost=2500.00, actual_cost=2400.00,
            status="completed", supplier="Software Corp.",
        )
        self.log("Adquisiciones creadas", "SUCCESS")

        Cronograma.objects.create(
            proyecto=p1, actividad=acts_a[0],
            fecha_inicio=p1_start, fecha_fin=p1_start + timedelta(days=12),
        )
        Cronograma.objects.create(
            proyecto=p1, actividad=acts_a[2],
            fecha_inicio=p1_start + timedelta(days=27),
            fecha_fin=p1_start + timedelta(days=58),
        )
        self.log("Cronogramas creados", "SUCCESS")

        Presupuesto.objects.create(
            proyecto=p1, monto_total=85000.00,
            descripcion="Presupuesto total aprobado para el proyecto.",
        )
        self.log("Presupuesto creado", "SUCCESS")

        Alcance.objects.create(
            proyecto=p1,
            descripcion="Alcance detallado: desarrollo full-stack con Django + Bootstrap, "
                        "incluyendo autenticación, CRUD de proyectos, seguimiento EVM.",
            objetivos="OA1: Gestión de proyectos. OA2: Seguimiento de actividades. "
                      "OA3: Reportes y dashboard.",
        )
        self.log("Alcance detallado creado", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        # 10. AUTO-CERTIFICACIONES Y NOTIFICACIONES
        # ═════════════════════════════════════════════════════════════════
        AutoCertificacion.objects.create(
            proyecto=p1, fecha=today - timedelta(days=5),
            descripcion="Auto-certificación del módulo de frontend completado.",
            aprobado=True,
        )
        AutoCertificacion.objects.create(
            proyecto=p1, fecha=today,
            descripcion="Pendiente: revisión de pruebas unitarias.",
            aprobado=False,
        )
        self.log("Auto-certificaciones creadas", "SUCCESS")

        # Notification (Automatically created by Activity.save() for high-cost and overdue)
        # Also create one manually for testing
        Notification.objects.create(
            project=p1, recipient=gestor, alert_type="general",
            message="Bienvenido al sistema de gestión de proyectos CMI.",
        )
        self.log("Notificaciones creadas", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        # 11. CORTES DEL PROYECTO (períodos de revisión)
        # ═════════════════════════════════════════════════════════════════
        p1_cuts = generate_project_cuts(p1, interval_days=90)
        self.log(f"Cortes generados para '{p1.name}': {len(p1_cuts)} períodos", "SUCCESS")
        for c in p1_cuts:
            self.log(f"  {c.name}: {c.start_date} - {c.end_date} | "
                     f"{c.planned_count} acts, PV=${c.pv} EV=${c.ev} AC=${c.ac} "
                     f"SPI={c.spi} CPI={c.cpi} Estado={c.status_label}", "SUCCESS")

        p2_cuts = generate_project_cuts(p2, interval_days=90)
        self.log(f"Cortes generados para '{p2.name}': {len(p2_cuts)} períodos", "SUCCESS")
        for c in p2_cuts:
            self.log(f"  {c.name}: {c.start_date} - {c.end_date} | "
                     f"{c.planned_count} acts, PV=${c.pv} EV=${c.ev} AC=${c.ac} "
                     f"SPI={c.spi} CPI={c.cpi} Estado={c.status_label}", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        # 12. PROYECTO DE EJEMPLO A — 12 MESES, TODO BIEN
        # ═════════════════════════════════════════════════════════════════
        self.log("—" * 60, "NOTICE")
        self.log("PROYECTO EJEMPLO A: 12 meses — Gestión Exitosa", "SUCCESS")
        self.log("—" * 60, "NOTICE")

        p3_start = today - timedelta(days=365)
        p3_end = today

        p3 = Project.objects.create(
            name="Proyecto Ejemplo A — Implementación ERP Exitosa",
            description="EJEMPLO: Proyecto de 12 meses donde TODO SALIÓ BIEN. "
                        "Todas las actividades se completaron en tiempo y costo. "
                        "Útil para analizar cortes con métricas EVM saludables.",
            start_date=p3_start, end_date=p3_end,
            status="completed", budget=130000.00, created_by=gestor,
        )

        ActaConstitucion.objects.create(
            proyecto=p3,
            alcance="Implementación completa de sistema ERP incluyendo "
                    "levantamiento, configuración, migración, pruebas y despliegue.",
            entregables="ERP configurado, datos migrados, usuarios capacitados, "
                        "sistema en producción.",
            justificacion="Modernizar la gestión empresarial con un ERP integral.",
            objetivos="Implementar ERP en 12 meses, dentro del presupuesto y sin desvíos.",
        )

        self.log("  Proyecto Ejemplo A creado", "SUCCESS")

        # ── Actividades: todas completadas en tiempo y costo ──────
        acts_p3 = []
        defs_p3 = [
            ("Levantamiento de Requisitos",  0,  20,  8000),
            ("Análisis de Procesos",        20,  15,  5000),
            ("Diseño de Solución",          35,  25, 12000),
            ("Configuración Inicial",       60,  30, 15000),
            ("Migración de Datos",          90,  20, 10000),
            ("Personalización de Módulos", 110,  40, 25000),
            ("Pruebas de Aceptación",      150,  20,  8000),
            ("Capacitación de Usuarios",   170,  25, 12000),
            ("Despliegue en Producción",   195,  15,  7000),
            ("Soporte Post-Lanzamiento",   210,  60, 18000),
            ("Cierre Formal",              270,  15,  5000),
        ]
        total_cost_p3 = sum(c for _, _, _, c in defs_p3)
        self.log(f"  Costo planificado total: ${total_cost_p3:,}", "SUCCESS")

        for name, off, dur, cost in defs_p3:
            s = p3_start + timedelta(days=off)
            e = s + timedelta(days=dur)
            act = Activity.objects.create(
                project=p3, name=name,
                description=f"Actividad: {name}",
                start_date=s, end_date=e,
                status="completed",
                cost=cost,
                actual_start_date=s,
                actual_end_date=e,
                actual_cost=cost,
                assigned_to=gestor,
            )
            acts_p3.append(act)

        # Predecesoras en cadena
        for i in range(1, len(acts_p3)):
            acts_p3[i].predecessor = acts_p3[i - 1]
            acts_p3[i].save()

        # ── Hitos ──────────────────────────────────────────────
        hito_defs_p3 = [
            ("Proyecto Iniciado",         0,   True,  "initiation", True),
            ("Requisitos Aprobados",     20,   True,  "planning",   True),
            ("Diseño Completado",        35,   True,  "planning",   True),
            ("ERP Configurado",          90,   True,  "execution",  False),
            ("Migración Finalizada",    110,   True,  "execution",  True),
            ("Pruebas Superadas",       170,   True,  "execution",  True),
            ("Despliegue Completado",   210,   True,  "execution",  True),
            ("Proyecto Cerrado",        285,   True,  "closure",    True),
        ]
        for name, offset, completed, phase, is_gate in hito_defs_p3:
            m = Milestone.objects.create(
                project=p3, name=name,
                description=f"Hito: {name}",
                due_date=p3_start + timedelta(days=offset),
                completed=completed, phase=phase, is_phase_gate=is_gate,
            )

        # ── Seguimientos mensuales (12 seguimientos, 1 por mes) ──
        seg_p3 = []
        for mes in range(1, 13):
            fecha = p3_start + timedelta(days=mes * 30)
            if fecha > today:
                fecha = today
            seg = Seguimiento(proyecto=p3, fecha=fecha,
                              observacion=f"Seguimiento Mes {mes} — Todo en línea.")
            seg.save()
            seg_p3.append(seg)
            self.log(f"  Seguimiento Mes {mes} ({fecha}): "
                     f"PV=${seg.pv} EV=${seg.ev} AC=${seg.ac} "
                     f"SPI={seg.spi} CPI={seg.cpi}", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        # 13. PROYECTO DE EJEMPLO B — 12 MESES, CON DESVÍOS
        # ═════════════════════════════════════════════════════════════════
        self.log("—" * 60, "NOTICE")
        self.log("PROYECTO EJEMPLO B: 12 meses — Con Retrasos y Sobrecostos", "WARNING")
        self.log("—" * 60, "NOTICE")

        # ── MISMA definición de actividades que Proyecto A ──
        #    La diferencia son los retrasos y sobrecostos en los datos reales.
        defs_p4 = [
            ("Levantamiento de Requisitos",  0,  20,  8000),
            ("Análisis de Procesos",        20,  15,  5000),
            ("Diseño de Solución",          35,  25, 12000),
            ("Configuración Inicial",       60,  30, 15000),
            ("Migración de Datos",          90,  20, 10000),
            ("Personalización de Módulos", 110,  40, 25000),
            ("Pruebas de Aceptación",      150,  20,  8000),
            ("Capacitación de Usuarios",   170,  25, 12000),
            ("Despliegue en Producción",   195,  15,  7000),
            ("Soporte Post-Lanzamiento",   210,  60, 18000),
            ("Cierre Formal",              270,  15,  5000),
        ]

        # Retraso en inicio real (días), extensión de duración (días),
        # multiplicador de costo real, estado
        #   (start_delay, dur_extension, cost_mult, status)
        desvios_p4 = [
            ( 0,  2,  1.00, "completed"),   # Levantamiento — ok, +2d
            ( 3,  5,  1.20, "completed"),   # Análisis — +3d inicio, +5d duración, +20%
            ( 5,  8,  1.15, "completed"),   # Diseño — +5d inicio, +8d duración, +15%
            (12, 15,  1.25, "completed"),   # Configuración — +12d, +15d, +25%
            (18, 22,  1.10, "completed"),   # Migración — +18d, +22d, +10%
            (30, 35,  1.30, "completed"),   # Personalización — +30d, +35d, +30%
            (35, 32,  1.15, "completed"),   # Pruebas — +35d, +32d, +15%
            (42, 30,  1.00, "completed"),   # Capacitación — +42d, +30d, ok costo
            (50, 25,  1.30, "completed"),   # Despliegue — +50d, +25d, +30%
            (55, None, None,  "in_progress"), # Soporte — empezó +55d tarde, en curso
            (None, None, None, "pending"),    # Cierre — pendiente
        ]

        p4_start = today - timedelta(days=365)
        # El proyecto se extendió por los retrasos acumulados
        p4_end = today + timedelta(days=180)  # 6 meses de extensión

        p4 = Project.objects.create(
            name="Proyecto Ejemplo B — Implementación ERP con Desvíos",
            description="EJEMPLO: Proyecto de 12 meses donde HUBO RETRASOS Y SOBREPRECIO. "
                        "MISMAS actividades que Ejemplo A, pero con ejecución demorada "
                        "y sobrecostos. Útil para comparar cortes EVM sanos vs. críticos.",
            start_date=p4_start, end_date=p4_end,
            status="in_progress", budget=130000.00, created_by=gestor,
        )

        ActaConstitucion.objects.create(
            proyecto=p4,
            alcance="MISMO alcance que Proyecto A: implementación ERP completa.",
            entregables="ERP configurado, datos migrados, usuarios capacitados.",
            justificacion="Misma justificación que Proyecto A, pero ejecución con problemas.",
            objetivos="Implementar ERP, aunque con desvíos esperados en cronograma y costo.",
        )

        self.log("  Proyecto Ejemplo B creado", "SUCCESS")

        acts_p4 = []
        for (name, off, dur, cost), (d_start, d_ext, c_mult, status) in zip(defs_p4, desvios_p4):
            planned_start = p4_start + timedelta(days=off)
            planned_end = planned_start + timedelta(days=dur)

            if status == "pending":
                a_start = a_end = a_cost = None
            elif status == "in_progress":
                a_start = planned_start + timedelta(days=d_start) if d_start is not None else None
                a_end = None
                a_cost = None
            else:  # completed
                a_start = planned_start + timedelta(days=d_start) if d_start is not None else None
                # actual_end = actual_start + dur + extension
                dur_total = dur + (d_ext or 0)
                a_end = a_start + timedelta(days=dur_total) if a_start else None
                a_cost = round(cost * c_mult) if c_mult else cost

            act = Activity.objects.create(
                project=p4, name=name,
                description=f"Actividad: {name}",
                start_date=planned_start,
                end_date=planned_end,
                status=status,
                cost=cost,
                actual_start_date=a_start,
                actual_end_date=a_end,
                actual_cost=a_cost,
                assigned_to=gestor,
            )
            acts_p4.append(act)

        # Predecesoras
        for i in range(1, len(acts_p4)):
            if acts_p4[i].status != 'pending':  # solo si ya empezó
                acts_p4[i].predecessor = acts_p4[i - 1]
                acts_p4[i].save()

        # ── Hitos ──────────────────────────────────────────────
        hito_defs_p4 = [
            ("Proyecto Iniciado",         0,   True,  "initiation", True),
            ("Requisitos Aprobados",     20,   True,  "planning",   True),
            ("Diseño Completado",        35,   True,  "planning",   True),
            ("ERP Configurado",          90,   True,  "execution",  False),
            ("Migración Finalizada",    110,   True,  "execution",  True),
            ("Pruebas Superadas",       170,   True,  "execution",  True),
            ("Despliegue en Producción",210,   False, "execution",  True),
            ("Proyecto Cerrado",        285,   False, "closure",    True),
        ]
        for name, offset, completed, phase, is_gate in hito_defs_p4:
            Milestone.objects.create(
                project=p4, name=name,
                description=f"Hito: {name}",
                due_date=p4_start + timedelta(days=offset),
                completed=completed, phase=phase, is_phase_gate=is_gate,
            )

        # ── Seguimientos mensuales ────────────────────────────
        for mes in range(1, 13):
            fecha = p4_start + timedelta(days=mes * 30)
            if fecha > today:
                fecha = today
            seg = Seguimiento(proyecto=p4, fecha=fecha,
                              observacion=f"Seguimiento Mes {mes} — Se detectan desvíos.")
            seg.save()
            self.log(f"  Seguimiento Mes {mes} ({fecha}): "
                     f"PV=${seg.pv} EV=${seg.ev} AC=${seg.ac} "
                     f"SV={seg.sv} CV={seg.cv} "
                     f"SPI={seg.spi} CPI={seg.cpi}", "WARNING" if seg.sv < 0 or seg.cv < 0 else "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        # 14. CORTES PARA PROYECTOS DE EJEMPLO
        # ═════════════════════════════════════════════════════════════════
        for proy, nombre in [(p3, "Ejemplo A (éxito)"), (p4, "Ejemplo B (desvíos)")]:
            cortes = generate_project_cuts(proy, interval_days=90)
            self.log(f"Cortes generados para '{nombre}': {len(cortes)} períodos", "SUCCESS")
            for c in cortes:
                self.log(f"  {c.name}: {c.start_date} - {c.end_date} | "
                         f"{c.planned_count} acts, PV=${c.pv} EV=${c.ev} AC=${c.ac} "
                         f"SPI={c.spi} CPI={c.cpi} Estado={c.status_label}", "SUCCESS")

        # ═════════════════════════════════════════════════════════════════
        #  RESUMEN FINAL
        # ═════════════════════════════════════════════════════════════════
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("  ¡BASE DE DATOS POBLADA EXITOSAMENTE!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Usuarios:     {User.objects.filter(is_superuser=False).count()}")
        self.stdout.write(f"  Proyectos:    {Project.objects.count()}")
        self.stdout.write(f"  Actividades:  {Activity.objects.count()}")
        self.stdout.write(f"  Hitos:        {Milestone.objects.count()}")
        self.stdout.write(f"  Seguimientos: {Seguimiento.objects.count()}")
        self.stdout.write(f"  Stakeholders: {Stakeholder.objects.count()}")
        self.stdout.write(f"  Feedbacks:    {Feedback.objects.count()}")
        self.stdout.write(f"  Recursos:     {Resource.objects.count()}")
        self.stdout.write(f"  Riesgos:      {Risk.objects.count()}")
        self.stdout.write(f"  Solic. Cambio:{ChangeRequest.objects.count()}")
        self.stdout.write(f"  Notificaciones:{Notification.objects.count()}")
        self.stdout.write("-" * 60)
        self.stdout.write(self.style.WARNING("  Credenciales:"))
        self.stdout.write("    jefe     / password123  (Jefe Departamental)")
        self.stdout.write("    gestor   / password123  (Gestor de Proyectos)")
        self.stdout.write("    tecnico  / password123  (Técnico de Proyectos)")
        self.stdout.write("-" * 60)
