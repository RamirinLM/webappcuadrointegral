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

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Proyecto')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    due_date = models.DateField(verbose_name='Fecha Límite')
    completed = models.BooleanField(default=False, verbose_name='Completado')

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cost and self.cost > 10000:  # Example threshold
            Notification.objects.create(
                project=self.project,
                alert_type='cost',
                message=f'Costo de actividad elevado: {self.name} - ${self.cost}'
            )
        # Check for schedule deviation
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
