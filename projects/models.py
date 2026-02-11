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
    perspectiva = models.CharField(max_length=25, choices=PERSPECTIVA_CHOICES, verbose_name='Perspectiva CMI')
    indicador = models.CharField(max_length=200, verbose_name='Indicador', blank=True)
    valor_actual = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Actual', default=0)
    valor_objetivo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Objetivo', default=0)
    descripcion = models.TextField(verbose_name='Descripción', blank=True)
    progreso = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='Progreso (%)', default=0)

    def save(self, *args, **kwargs):
        if self.valor_objetivo != 0:
            self.progreso = (self.valor_actual / self.valor_objetivo) * 100
        else:
            self.progreso = 0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'

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

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planificación'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('on_hold', 'En Espera'),
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

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
