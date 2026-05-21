from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('jefe_departamental', 'Jefe Departamental'),
        ('tecnico_proyectos', 'Técnico de Proyectos'),
        ('gestor_proyectos', 'Gestor de Proyectos'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tecnico_proyectos')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Seguimiento(models.Model):
    PERSPECTIVA_CHOICES = [
        ('financiera', 'Financiera'),
        ('cliente', 'Cliente'),
        ('procesos_internos', 'Procesos Internos'),
        ('aprendizaje_crecimiento', 'Aprendizaje y Crecimiento'),
    ]
    proyecto = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    fecha = models.DateField(verbose_name='Fecha')
    observacion = models.TextField(verbose_name='Observación', blank=True)
    # Earned Value Management metrics
    pv = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='PV (Planned Value)', default=0)
    ev = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='EV (Earned Value)', default=0)
    ac = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='AC (Actual Cost)', default=0)
    sv = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='SV (Schedule Variance)', default=0)
    cv = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='CV (Cost Variance)', default=0)
    cpi = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='CPI (Cost Performance Index)', default=0)
    spi = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='SPI (Schedule Performance Index)', default=0)

    def _activity_total_planned(self, activity):
        """Costo planificado de una actividad (sin incluir recursos)."""
        return activity.total_planned_cost

    def _activity_total_actual(self, activity):
        """Costo real de una actividad (sin incluir recursos)."""
        return activity.total_actual_cost

    def calculate_metrics(self):
        """
        Calcula métricas EVM usando fechas reales de las actividades.
        Los costos NO incluyen recursos (son desglose del costo de actividad).

        PV (Planned Value):   Suma del costo planificado de actividades cuyo
                              fin PLANIFICADO es ≤ fecha de corte.
        EV (Earned Value):    Suma del costo planificado de actividades que
                              YA se completaron (actual_end_date ≤ fecha).
        AC (Actual Cost):     Suma del costo REAL de actividades completadas.
                              Si no tiene actual_cost, usa el planificado.
        SV (Schedule Variance):  EV - PV  (positivo = adelantado)
        CV (Cost Variance):      EV - AC  (positivo = bajo presupuesto)
        CPI:  EV / AC
        SPI:  EV / PV
        """
        from decimal import Decimal
        
        activities = self.proyecto.activity_set.all()
        
        # PV: costo planificado (actividad + recursos) de actividades cuyo fin PLANIFICADO es ≤ fecha de corte
        pv_activities = activities.filter(end_date__lte=self.fecha)
        self.pv = Decimal(str(sum(self._activity_total_planned(a) for a in pv_activities)))
        
        # EV: costo PLANIFICADO (actividad + recursos) de actividades COMPLETADAS
        ev_activities = activities.filter(
            status='completed',
            actual_end_date__lte=self.fecha
        )
        ev_fallback = activities.filter(
            status='completed',
            actual_end_date__isnull=True,
            end_date__lte=self.fecha
        )
        ev_set = ev_activities | ev_fallback
        self.ev = Decimal(str(sum(self._activity_total_planned(a) for a in ev_set.distinct())))
        
        # AC: costo REAL (actividad + recursos) de actividades completadas
        ac_total = Decimal('0')
        for a in ev_set.distinct():
            ac_total += self._activity_total_actual(a)
        self.ac = ac_total
        
        # SV = EV - PV
        self.sv = self.ev - self.pv
        
        # CV = EV - AC
        self.cv = self.ev - self.ac
        
        # CPI
        if self.ac > 0:
            self.cpi = self.ev / self.ac
        else:
            self.cpi = Decimal('0')
        
        # SPI
        if self.pv > 0:
            self.spi = self.ev / self.pv
        else:
            self.spi = Decimal('0')

    def save(self, *args, **kwargs):
        self.calculate_metrics()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Seguimiento {self.proyecto.name} - {self.fecha}"

    class Meta:
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        ordering = ['-fecha']

class Cronograma(models.Model):
    proyecto = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    actividad = models.ForeignKey('Activity', on_delete=models.CASCADE, verbose_name='Actividad')
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de Fin')

    class Meta:
        verbose_name = 'Cronograma'
        verbose_name_plural = 'Cronogramas'
        managed = False

    def __str__(self):
        return f"{self.actividad.name} - {self.proyecto.name}"

class Presupuesto(models.Model):
    proyecto = models.OneToOneField('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Total')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'

class Alcance(models.Model):
    proyecto = models.OneToOneField('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    descripcion = models.TextField(verbose_name='Descripción')
    objetivos = models.TextField(verbose_name='Objetivos')

    class Meta:
        verbose_name = 'Alcance'
        verbose_name_plural = 'Alcances'

class ActaConstitucion(models.Model):
    proyecto = models.OneToOneField('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    alcance = models.TextField(verbose_name='Alcance')
    entregables = models.TextField(verbose_name='Entregables')
    justificacion = models.TextField(verbose_name='Justificación')
    objetivos = models.TextField(verbose_name='Objetivos')

    def __str__(self):
        return f"Acta de Constitución - {self.proyecto.name}"

    class Meta:
        verbose_name = 'Acta de Constitución'
        verbose_name_plural = 'Actas de Constitución'

class Comunicacion(models.Model):
    proyecto = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    interesado = models.ForeignKey('stakeholders.Stakeholder', on_delete=models.CASCADE, verbose_name='Interesado', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    mensaje = models.TextField(verbose_name='Mensaje')
    tipo = models.CharField(max_length=50, choices=[('email', 'Email'), ('reunion', 'Reunión'), ('llamada', 'Llamada')], verbose_name='Tipo')

    class Meta:
        verbose_name = 'Comunicación'
        verbose_name_plural = 'Comunicaciones'

class AutoCertificacion(models.Model):
    proyecto = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    fecha = models.DateField(verbose_name='Fecha')
    descripcion = models.TextField(verbose_name='Descripción')
    aprobado = models.BooleanField(default=False, verbose_name='Aprobado')

    class Meta:
        verbose_name = 'Auto Certificación'
        verbose_name_plural = 'Auto Certificaciones'

class Notification(models.Model):
    ALERT_TYPES = [
        ('risk', 'Riesgo'),
        ('cost', 'Costo'),
        ('schedule', 'Cronograma'),
        ('general', 'General'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_notifications', verbose_name='Destinatario')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='Tipo de Alerta')
    message = models.TextField(verbose_name='Mensaje')
    sent = models.BooleanField(default=False, verbose_name='Enviado')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Leído en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.alert_type} - {self.project.name}"

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

class ChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Solicitado Por')
    description = models.TextField(verbose_name='Descripción del Cambio')
    justification = models.TextField(verbose_name='Justificación')
    impact = models.TextField(blank=True, verbose_name='Impacto')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_changes', verbose_name='Aprobado Por')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_impact_assessment(self):
        # Simple impact assessment
        impact = "Bajo"
        if "costo" in self.description.lower() or "tiempo" in self.description.lower():
            impact = "Medio"
        if "alcance" in self.description.lower() or "riesgo" in self.description.lower():
            impact = "Alto"
        return impact

    def __str__(self):
        return f"Cambio en {self.project.name} - {self.status}"

    class Meta:
        verbose_name = 'Solicitud de Cambio'
        verbose_name_plural = 'Solicitudes de Cambio'

class Baseline(models.Model):
    project = models.OneToOneField('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    scope_baseline = models.TextField(verbose_name='Línea Base del Alcance')
    schedule_baseline = models.TextField(verbose_name='Línea Base del Cronograma')
    cost_baseline = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Línea Base de Costo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Línea Base para {self.project.name}"

    class Meta:
        verbose_name = 'Línea Base'
        verbose_name_plural = 'Líneas Base'

class Acquisition(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE, verbose_name='Proyecto')
    item = models.CharField(max_length=200, verbose_name='Artículo')
    description = models.TextField(verbose_name='Descripción')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo Estimado')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo Real')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name='Estado')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Proveedor')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Entrega')

    def __str__(self):
        return f"Adquisición: {self.item} - {self.project.name}"

    class Meta:
        verbose_name = 'Adquisición'
        verbose_name_plural = 'Adquisiciones'

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planificación'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('on_hold', 'En Espera'),
        ('modified', 'Modificado'),
    ]
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='Estado')
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Presupuesto')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_activities_cost(self):
        """Suma de costos planificados de todas las actividades (desde resources)."""
        from django.db.models import Sum
        result = self.activity_set.aggregate(total=Sum('cost'))
        return result['total'] or 0

    total_planned_cost = total_activities_cost

    @property
    def total_resources_cost(self):
        """Suma de costos de todos los recursos del proyecto"""
        from django.db.models import Sum, F, DecimalField
        from resources.models import Resource
        result = Resource.objects.filter(
            activity__project=self
        ).aggregate(
            total=Sum(F('quantity') * F('cost_per_unit'), output_field=DecimalField())
        )
        return result['total'] or 0

    @property
    def total_actual_cost(self):
        """Costo real total del proyecto = suma de actual_cost de cada actividad."""
        from django.db.models import Sum
        result = self.activity_set.aggregate(total=Sum('actual_cost'))
        return result['total'] or 0

    @property
    def budget_variance(self):
        """Desviación del presupuesto: presupuesto - costo planificado.
        Positivo = estamos por debajo del presupuesto planificado."""
        if self.budget:
            return self.budget - self.total_planned_cost
        return None

    @property
    def planned_vs_actual_variance(self):
        """Desviación de ejecución: costo planificado - costo real.
        Positivo = gastamos menos de lo planificado."""
        return self.total_planned_cost - self.total_actual_cost

    @property
    def budget_utilization_percentage(self):
        """Porcentaje de utilización del presupuesto (costo real vs presupuesto)"""
        if self.budget and self.budget > 0 and self.total_actual_cost:
            return round((self.total_actual_cost / self.budget) * 100, 1)
        return 0

    def get_traffic_light_status(self):
        """
        Calcula el estado del semaforo CMI basado en SPI y CPI.
        Verde: SPI >= 0.95 y CPI >= 0.95
        Amarillo: SPI >= 0.85 y CPI >= 0.85
        Rojo: Cualquier otro caso
        """
        latest_seguimiento = self.seguimiento_set.order_by('-fecha').first()
        if not latest_seguimiento:
            return 'gray'
        
        spi = float(latest_seguimiento.spi or 0)
        cpi = float(latest_seguimiento.cpi or 0)
        
        if spi >= 0.95 and cpi >= 0.95:
            return 'green'
        elif spi >= 0.85 and cpi >= 0.85:
            return 'yellow'
        else:
            return 'red'

    def get_progress_percentage(self):
        """Calcula el porcentaje de avance del proyecto basado en actividades completadas"""
        total = self.activity_set.count()
        if total == 0:
            return 0
        completed = self.activity_set.filter(status='completed').count()
        return round((completed / total) * 100, 1)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

class Milestone(models.Model):
    PHASE_CHOICES = [
        ('initiation', 'Inicio'),
        ('planning', 'Planificación'),
        ('execution', 'Ejecución'),
        ('monitoring', 'Monitoreo y Control'),
        ('closure', 'Cierre'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Proyecto')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    due_date = models.DateField(verbose_name='Fecha Límite')
    completed = models.BooleanField(default=False, verbose_name='Completado')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='execution', verbose_name='Fase')
    is_phase_gate = models.BooleanField(default=False, verbose_name='Es Cierre de Fase', help_text="Marca el final de una fase del proyecto")
    activities = models.ManyToManyField('Activity', blank=True, verbose_name='Actividades Asociadas')

    def check_completion(self):
        """Verifica si todas las actividades asociadas están completas"""
        return not self.activities.filter(status__in=['pending', 'in_progress']).exists()

    def get_progress_percentage(self):
        """Calcula el porcentaje de avance basado en actividades asociadas"""
        total = self.activities.count()
        if total == 0:
            return 0
        completed = self.activities.filter(status='completed').count()
        return round((completed / total) * 100, 1)

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    class Meta:
        verbose_name = 'Hito'
        verbose_name_plural = 'Hitos'

class Activity(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Proyecto')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    # ── Fechas planificadas (línea base) ──
    start_date = models.DateField(verbose_name='Fecha de Inicio Planificada')
    end_date = models.DateField(verbose_name='Fecha de Fin Planificada')
    # ── Fechas reales (seguimiento) ──
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Inicio Real')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Fin Real')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Asignado A')
    # ── Costos ──
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo Planificado')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo Real')
    time_estimate = models.PositiveIntegerField(help_text="Horas estimadas", null=True, blank=True, verbose_name='Estimación de Tiempo')
    predecessor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Actividad Predecesora',
        related_name='successors',
        help_text="Actividad que debe completarse antes de iniciar esta"
    )

    def clean(self):
        """
        Validaciones de negocio para la actividad:
        1. Fechas dentro del rango del proyecto
        2. Fecha de inicio anterior a fecha de fin
        3. Costo dentro del presupuesto disponible
        4. Sin ciclos de dependencia
        """
        from django.core.exceptions import ValidationError
        from django.db.models import Sum
        errors = {}

        # Validación 1: Fechas dentro del rango del proyecto
        if self.start_date and self.project and self.project.start_date:
            if self.start_date < self.project.start_date:
                errors['start_date'] = f'La fecha de inicio no puede ser anterior al inicio del proyecto ({self.project.start_date.strftime("%d/%m/%Y")})'

        if self.end_date and self.project and self.project.end_date:
            if self.end_date > self.project.end_date:
                errors['end_date'] = f'La fecha de fin no puede ser posterior al fin del proyecto ({self.project.end_date.strftime("%d/%m/%Y")})'

        # Validación 2: Fecha inicio < Fecha fin
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['start_date'] = 'La fecha de inicio no puede ser posterior a la fecha de fin'

        # Validación 2b: Fechas reales dentro del rango del proyecto
        if self.actual_start_date and self.project and self.project.start_date:
            if self.actual_start_date < self.project.start_date:
                errors['actual_start_date'] = f'La fecha de inicio real no puede ser anterior al inicio del proyecto ({self.project.start_date.strftime("%d/%m/%Y")})'

        if self.actual_end_date and self.project and self.project.end_date:
            if self.actual_end_date > self.project.end_date:
                errors['actual_end_date'] = f'La fecha de fin real no puede ser posterior al fin del proyecto ({self.project.end_date.strftime("%d/%m/%Y")})'

        if self.actual_start_date and self.actual_end_date:
            if self.actual_start_date > self.actual_end_date:
                errors['actual_start_date'] = 'La fecha de inicio real no puede ser posterior a la fecha de fin real'

        # Validación 3: Costo dentro del presupuesto disponible
        if self.cost and self.project and self.project.budget:
            total_activities_cost = Activity.objects.filter(
                project=self.project
            ).exclude(pk=self.pk).aggregate(
                total=Sum('cost')
            )['total'] or 0

            if total_activities_cost + self.cost > self.project.budget:
                disponible = self.project.budget - total_activities_cost
                errors['cost'] = f'Costo excede el presupuesto disponible. Presupuesto total: ${self.project.budget:,.2f}, Disponible: ${disponible:,.2f}'

        # Validación 4: Sin ciclos de dependencia
        if self.predecessor:
            visited = set()
            current = self.predecessor
            while current:
                if current.pk == self.pk:
                    errors['predecessor'] = 'No se pueden crear ciclos de dependencia. Esta actividad no puede ser predecesora de sí misma.'
                    break
                if current.pk in visited:
                    break
                visited.add(current.pk)
                current = current.predecessor

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Notificaciones de costo elevado
        if self.cost and self.cost > 10000:
            Notification.objects.get_or_create(
                project=self.project,
                recipient=self.project.created_by,
                alert_type='cost',
                message=f'Costo de actividad elevado: {self.name} - ${self.cost}'
            )
        
        # Notificaciones de desviación de cronograma
        from datetime import date
        today = date.today()
        if self.end_date and self.end_date < today and self.status != 'completed':
            Notification.objects.get_or_create(
                project=self.project,
                recipient=self.project.created_by,
                alert_type='schedule',
                message=f'Desviación en cronograma: {self.name} - Fecha límite {self.end_date}'
            )

    # ── Escenario de seguimiento ─────────────────────────────────────────

    @property
    def tracking_scenario(self):
        """
        Clasifica el escenario de seguimiento segun fechas planificadas vs reales.
        Retorna un dict: {'code': str, 'label': str, 'color': str, 'detail': str}
        """
        from datetime import date as dt_date
        p_start = self.start_date
        p_end = self.end_date
        a_start = self.actual_start_date
        a_end = self.actual_end_date

        if not a_start and not a_end:
            return {'code': 'sin_datos', 'label': 'Sin seguimiento', 'color': 'secondary', 'detail': 'Aun no se registraron datos reales.'}

        # Comparar inicios
        if a_start and p_start:
            if a_start < p_start:
                start_status = 'temprano'
            elif a_start > p_start:
                start_status = 'tardio'
            else:
                start_status = 'a_tiempo'
        else:
            start_status = 'desconocido'

        # Comparar fines
        if a_end and p_end:
            if a_end < p_end:
                end_status = 'temprano'
            elif a_end > p_end:
                end_status = 'tardio'
            else:
                end_status = 'a_tiempo'
        elif a_end is None and self.status == 'completed':
            end_status = 'sin_fecha_real'
        else:
            end_status = 'pendiente'

        # Determinar escenario
        if end_status == 'tardio':
            if start_status == 'tardio':
                return {'code': 'atrasado_inicio_fin', 'label': 'Atrasado', 'color': 'danger',
                        'detail': f'Inicio tardio ({(a_start - p_start).days} dia(s)) y finalizacion tardia ({(a_end - p_end).days} dia(s)).'}
            elif start_status == 'a_tiempo':
                return {'code': 'atrasado_fin', 'label': 'Atrasado', 'color': 'danger',
                        'detail': f'Inicio a tiempo pero finalizacion tardia ({(a_end - p_end).days} dia(s) de atraso).'}
            else:
                return {'code': 'atrasado_fin', 'label': 'Atrasado', 'color': 'danger',
                        'detail': f'Finalizacion tardia ({(a_end - p_end).days} dia(s) de atraso).'}

        if end_status == 'temprano':
            if start_status == 'temprano':
                return {'code': 'adelantado_inicio_fin', 'label': 'Adelantado', 'color': 'success',
                        'detail': f'Inicio temprano ({(p_start - a_start).days} dia(s)) y finalizacion anticipada ({(p_end - a_end).days} dia(s)).'}
            elif start_status == 'a_tiempo':
                return {'code': 'adelantado_fin', 'label': 'Adelantado', 'color': 'success',
                        'detail': f'Inicio a tiempo y finalizacion anticipada ({(p_end - a_end).days} dia(s)).'}
            else:
                return {'code': 'adelantado_fin', 'label': 'Adelantado', 'color': 'success',
                        'detail': f'Finalizacion anticipada ({(p_end - a_end).days} dia(s)).'}

        if end_status == 'a_tiempo':
            if start_status == 'tardio':
                return {'code': 'recuperado', 'label': 'Recuperado', 'color': 'warning',
                        'detail': f'Inicio tardio pero recuperado: finalizo a tiempo.'}
            elif start_status == 'temprano':
                return {'code': 'ventaja_perdida', 'label': 'Sin cambio neto', 'color': 'info',
                        'detail': f'Inicio temprano pero finalizo en fecha planificada.'}
            else:
                return {'code': 'en_linea', 'label': 'En linea', 'color': 'success',
                        'detail': 'Cumplido exactamente en fecha planificada.'}

        # Para actividades en progreso sin fecha real de fin
        if self.status == 'in_progress':
            today = dt_date.today()
            if today > p_end:
                return {'code': 'en_curso_atrasado', 'label': 'En curso (atrasado)', 'color': 'warning',
                        'detail': f'Actividad en progreso y ya pasó su fecha planificada de fin ({(today - p_end).days} dia(s) de atraso).'}
            return {'code': 'en_curso', 'label': 'En curso', 'color': 'info',
                    'detail': 'Actividad en progreso dentro del plazo planificado.'}

        return {'code': 'pendiente', 'label': 'Pendiente', 'color': 'secondary', 'detail': 'Actividad pendiente de ejecucion.'}

    # ── Propiedades de varianza ──────────────────────────────────────────

    @property
    def schedule_variance_days(self):
        """
        Días de diferencia entre lo planificado y lo real.
        Negativo = atrasado, Positivo = adelantado.
        Usa actual_end_date si está completa; si no, compara con hoy.
        """
        planned_end = self.end_date
        if not planned_end:
            return None
        actual_end = self.actual_end_date
        if not actual_end and self.status == 'completed':
            actual_end = self.end_date  # si se completó pero sin fecha real, asumimos planificada
        if not actual_end:
            from datetime import date
            actual_end = date.today()  # en progreso: contra hoy
        return (planned_end - actual_end).days

    # ── Costos totales incluyendo recursos ────────────────────────────

    @property
    def total_planned_cost(self):
        """Costo planificado = suma de recursos de la actividad (quantity * cost_per_unit).
        Si no tiene recursos, usa self.cost como fallback para datos existentes."""
        from resources.models import Resource
        res = Resource.objects.filter(activity=self).aggregate(
            total=models.Sum('total_cost')
        )['total'] or 0
        if res:
            return res
        return self.cost or 0  # fallback: actividades sin recursos

    def update_cost_from_resources(self):
        """Sincroniza self.cost con la suma de recursos."""
        from resources.models import Resource
        total = Resource.objects.filter(activity=self).aggregate(
            total=models.Sum('total_cost')
        )['total'] or 0
        if total:
            # Evitar recursión: guardar sin full_clean(), solo el campo cost
            Activity.objects.filter(pk=self.pk).update(cost=total)
            self.cost = total
        return self.cost or 0

    @property
    def total_actual_cost(self):
        """Costo real de la actividad.
        Usa actual_cost si existe, sino usa el costo planificado (que = suma de recursos)."""
        if self.actual_cost is not None:
            return self.actual_cost
        return self.cost or 0

    @property
    def cost_variance(self):
        """
        Diferencia entre costo planificado y real de la actividad.
        Positivo = gasté menos de lo planificado (bajo presupuesto).
        Negativo = gasté más de lo planificado (sobrepresupuesto).
        """
        planned = self.total_planned_cost
        actual = self.total_actual_cost
        if planned is None:
            return None
        return planned - actual

    @property
    def is_behind_schedule(self):
        sv = self.schedule_variance_days
        if sv is None:
            return False
        return sv < 0

    @property
    def is_over_budget(self):
        cv = self.cost_variance
        if cv is None:
            return False
        return cv < 0

    # ── Fin propiedades de varianza ──────────────────────────────────────

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'


class ActivityAssignment(models.Model):
    """
    Modelo para asignar múltiples responsables a una actividad.
    Permite la gestión de recursos humanos por actividad.
    """
    ROLE_CHOICES = [
        ('responsable', 'Responsable Principal'),
        ('colaborador', 'Colaborador'),
        ('revisor', 'Revisor'),
        ('aprobador', 'Aprobador'),
    ]
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='Actividad', related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Responsable')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='colaborador', verbose_name='Rol en la Actividad')
    hours_assigned = models.PositiveIntegerField(default=0, verbose_name='Horas Asignadas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Asignación')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.activity.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Asignación de Actividad'
        verbose_name_plural = 'Asignaciones de Actividades'
        unique_together = ['activity', 'user']


class ProjectCut(models.Model):
    """
    Define un período de revisión (corte/trimestre) dentro de un proyecto.
    Las métricas se computan dinámicamente desde las actividades del proyecto.
    """
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='cuts',
        verbose_name='Proyecto'
    )
    name = models.CharField(
        max_length=100, verbose_name='Nombre del corte',
        help_text='Ej: Trimestre 1, Corte 2, Q1 2026...'
    )
    start_date = models.DateField(verbose_name='Fecha de inicio del período')
    end_date = models.DateField(verbose_name='Fecha de fin del período')
    sort_order = models.PositiveIntegerField(
        default=0, verbose_name='Orden',
        help_text='Orden de aparición (1, 2, 3...)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Corte del Proyecto'
        verbose_name_plural = 'Cortes del Proyecto'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'sort_order'],
                name='unique_cut_order_per_project'
            ),
        ]

    def __str__(self):
        return f"{self.name} — {self.project.name}"

    # ── Actividades del período ──────────────────────────────────────────

    @property
    def activities_in_period(self):
        """
        Actividades del proyecto cuya fecha de fin PLANIFICADA cae dentro
        del rango del corte. Esto define qué actividades "pertenecen" a
        este período según la planificación.
        """
        return self.project.activity_set.filter(
            end_date__gte=self.start_date,
            end_date__lte=self.end_date,
        )

    # ── Métricas planificadas ────────────────────────────────────────────

    @property
    def planned_count(self) -> int:
        """Cantidad de actividades planificadas en este período."""
        return self.activities_in_period.count()

    @property
    def planned_cost(self):
        """Suma del costo planificado de las actividades del período (sin recursos)."""
        from decimal import Decimal
        total = Decimal('0')
        for act in self.activities_in_period:
            total += act.total_planned_cost
        return total

    @property
    def pv(self):
        """PV (Planned Value) = planned_cost (alias semántico EVM)."""
        return self.planned_cost

    # ── Métricas reales ──────────────────────────────────────────────────

    @property
    def completed_activities(self):
        """Actividades del período que ya están completadas."""
        return self.activities_in_period.filter(status='completed')

    @property
    def completed_count(self) -> int:
        """Cuántas actividades del período se completaron realmente."""
        return self.completed_activities.count()

    @property
    def ev(self):
        """
        EV (Earned Value) = suma del costo PLANIFICADO
        de las actividades del período que YA fueron completadas.
        """
        from decimal import Decimal
        total = Decimal('0')
        for act in self.completed_activities:
            total += act.total_planned_cost
        return total

    @property
    def ac(self):
        """
        AC (Actual Cost) = suma del costo REAL
        de las actividades del período que fueron completadas.
        """
        from decimal import Decimal
        total = Decimal('0')
        for act in self.completed_activities:
            total += act.total_actual_cost
        return total

    # ── Variaciones ──────────────────────────────────────────────────────

    @property
    def sv(self):
        """
        SV (Schedule Variance) = EV - PV.
        Positivo = adelantado (hicimos más de lo planificado).
        Negativo = atrasado (hicimos menos de lo planificado).
        """
        return self.ev - self.pv

    @property
    def cv(self):
        """
        CV (Cost Variance) = EV - AC.
        Positivo = gastamos menos de lo presupuestado.
        Negativo = gastamos más de lo presupuestado.
        """
        return self.ev - self.ac

    @property
    def spi(self):
        """SPI (Schedule Performance Index). >= 1.0 = buen ritmo."""
        from decimal import Decimal
        if self.pv > 0:
            return self.ev / self.pv
        return Decimal('0')

    @property
    def cpi(self):
        """CPI (Cost Performance Index). >= 1.0 = eficiente en costos."""
        from decimal import Decimal
        if self.ac > 0:
            return self.ev / self.ac
        return Decimal('0')

    # ── Indicadores de estado ────────────────────────────────────────────

    @property
    def schedule_variance_count(self) -> int:
        """
        Diferencia en cantidad de actividades:
        Negativo = completamos menos de lo planificado (atrasado).
        """
        return self.completed_count - self.planned_count

    @property
    def progress_percentage(self) -> float:
        """Porcentaje de avance: completadas / planificadas."""
        if self.planned_count == 0:
            return 0.0
        return round((self.completed_count / self.planned_count) * 100, 1)

    @property
    def has_any_tracking(self) -> bool:
        """True si al menos una actividad del período tiene datos reales cargados."""
        from django.db.models import Q
        return self.activities_in_period.filter(
            Q(actual_start_date__isnull=False) |
            Q(actual_end_date__isnull=False) |
            Q(actual_cost__isnull=False)
        ).exists()

    @property
    def status(self):
        """
        Semáforo del período basado en SPI y CPI.
        - Verde:     SPI >= 0.95 y CPI >= 0.95  (todo bien)
        - Amarillo:  SPI >= 0.85 y CPI >= 0.85  (alerta, desviaciones menores)
        - Rojo:      cualquier otro caso con datos (crítico, desviaciones graves)
        - Sin info:  no hay NINGUNA actividad con datos reales cargados
        """
        if self.planned_count == 0:
            return 'no_data'

        # Si ninguna actividad del período tiene datos reales → sin información
        if not self.has_any_tracking:
            return 'no_data'

        spi_val = float(self.spi)
        cpi_val = float(self.cpi)

        if spi_val >= 0.95 and cpi_val >= 0.95:
            return 'green'
        elif spi_val >= 0.85 and cpi_val >= 0.85:
            return 'yellow'
        else:
            return 'red'

    @property
    def status_label(self):
        labels = {
            'green': 'En línea',
            'yellow': 'En alerta',
            'red': 'Crítico',
            'no_data': 'Sin información',
        }
        return labels.get(self.status, 'Desconocido')
