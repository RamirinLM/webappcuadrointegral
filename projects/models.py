from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    apellido = models.CharField(max_length=200, verbose_name='Apellido')
    email = models.EmailField(verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

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
    cpi = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='CPI (Cost Performance Index)', default=0)
    spi = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='SPI (Schedule Performance Index)', default=0)

    def calculate_metrics(self):
        # PV: Planned Value - budgeted cost of work scheduled
        # For simplicity, PV is the sum of costs of activities that should be completed by this date
        from datetime import date
        activities = self.proyecto.activity_set.all()
        total_budget = sum(activity.cost or 0 for activity in activities)
        completed_activities = activities.filter(end_date__lte=self.fecha)
        pv = sum(activity.cost or 0 for activity in completed_activities)
        self.pv = pv

        # EV: Earned Value - budgeted cost of work performed
        # Assuming completed activities are 100% earned
        completed_activities_actual = activities.filter(status='completed')
        ev = sum(activity.cost or 0 for activity in completed_activities_actual)
        self.ev = ev

        # AC: Actual Cost - actual cost incurred
        # For simplicity, AC is the sum of costs of completed activities (assuming cost = actual cost)
        ac = sum(activity.cost or 0 for activity in completed_activities_actual)
        self.ac = ac

        # CPI = EV / AC if AC > 0 else 0
        self.cpi = self.ev / self.ac if self.ac > 0 else 0

        # SPI = EV / PV if PV > 0 else 0
        self.spi = self.ev / self.pv if self.pv > 0 else 0

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
    interesado = models.ForeignKey('stakeholders.Stakeholder', on_delete=models.CASCADE, verbose_name='Interesado')
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
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='Tipo de Alerta')
    message = models.TextField(verbose_name='Mensaje')
    sent = models.BooleanField(default=False, verbose_name='Enviado')
    created_at = models.DateTimeField(auto_now_add=True)

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
        """Suma de costos de todas las actividades del proyecto"""
        from django.db.models import Sum
        result = self.activity_set.aggregate(total=Sum('cost'))
        return result['total'] or 0

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
        """Costo real total del proyecto (actividades + recursos)"""
        return self.total_activities_cost + self.total_resources_cost

    @property
    def budget_variance(self):
        """Diferencia entre presupuesto y costo real (positivo = bajo presupuesto)"""
        if self.budget:
            return self.budget - self.total_actual_cost
        return None

    @property
    def budget_utilization_percentage(self):
        """Porcentaje de utilización del presupuesto"""
        if self.budget and self.budget > 0:
            return round((self.total_actual_cost / self.budget) * 100, 1)
        return 0

    def get_traffic_light_status(self):
        """
        Calcula el estado del semáforo CMI basado en SPI y CPI.
        Verde: SPI >= 0.95 y CPI >= 0.95
        Amarillo: SPI >= 0.85 y CPI >= 0.85
        Rojo: Cualquier otro caso
        """
        try:
            latest_seguimiento = self.seguimiento_set.first()
            if not latest_seguimiento:
                return 'gray'  # Sin datos
            
            spi = latest_seguimiento.spi or 0
            cpi = latest_seguimiento.cpi or 0
            
            if spi >= 0.95 and cpi >= 0.95:
                return 'green'
            elif spi >= 0.85 and cpi >= 0.85:
                return 'yellow'
            else:
                return 'red'
        except:
            return 'gray'

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
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Asignado A')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo')
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
            Notification.objects.create(
                project=self.project,
                alert_type='cost',
                message=f'Costo de actividad elevado: {self.name} - ${self.cost}'
            )
        
        # Notificaciones de desviación de cronograma
        from datetime import date
        today = date.today()
        if self.end_date and self.end_date < today and self.status != 'completed':
            Notification.objects.create(
                project=self.project,
                alert_type='schedule',
                message=f'Desviación en cronograma: {self.name} - Fecha límite {self.end_date}'
            )

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
