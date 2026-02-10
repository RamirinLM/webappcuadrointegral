from django.db import models
from django.contrib.auth.models import User

ESTADO = [
    (0, 'Iniciado'),
    (1, 'En Progreso'),
    (2, 'Completado'),
    (3, 'Cancelado'),
]

NIVEL_PODER = [(1, 'Alto'), (2, 'Medio'), (3, 'Bajo')]
NIVEL_INTERES = [(1, 'Alto'), (2, 'Medio'), (3, 'Bajo')]

ROLES = [
    ('admin', 'Administrador'),
    ('gestor', 'Gestor de proyectos'),
    ('consultor', 'Consultor (solo lectura)'),
]


class PerfilUsuario(models.Model):
    """Perfil de usuario para control de acceso por rol."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='consultor')

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == 'admin'

    @property
    def puede_editar(self):
        return self.rol in ('admin', 'gestor')

    @property
    def puede_eliminar(self):
        return self.rol == 'admin'


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    class Meta:
        abstract = True


class Interesado(Persona):
    rol = models.CharField(max_length=100)
    nivel_poder = models.IntegerField(choices=NIVEL_PODER, default=2, verbose_name='Nivel de poder')
    nivel_interes = models.IntegerField(choices=NIVEL_INTERES, default=2, verbose_name='Nivel de interés')

    def __str__(self):
        return self.nombre + " " + self.apellido

class Comunicacion(models.Model):
    observaciones = models.TextField()
    fecha = models.DateField()
    interesado = models.ForeignKey(to=Interesado, on_delete=models.CASCADE)
    #proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return self.observaciones

class Riesgo(models.Model):
    descripcion = models.TextField()
    probabilidad = models.FloatField()
    impacto = models.FloatField()
    estrategia_mitigacion = models.TextField()
    #proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return f"Riesgo para el proyecto {self.descripcion}"

class Alcance(models.Model):
    descripcion = models.TextField()
    metas = models.TextField()
    tiempo = models.IntegerField()
    #proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return f"Alcance del proyecto {self.descripcion}"

class ActaConstitucion(models.Model):
    alcance = models.TextField()
    objetivos = models.TextField()
    entregables = models.TextField()
    justificacion = models.TextField()
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return self.alcance
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.IntegerField(choices=ESTADO, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    acta_constitucion = models.OneToOneField(to='gestionproyecto.ActaConstitucion', on_delete=models.CASCADE, null=True, blank=True)
    interesados = models.ManyToManyField(to=Interesado, blank=True)
    comunicaciones = models.ManyToManyField(to=Comunicacion, blank=True)
    riesgos = models.ManyToManyField(to=Riesgo, blank=True)
    alcances = models.ManyToManyField(to=Alcance, blank=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return self.nombre


class Adquisicion(models.Model):
    """Seguimiento de adquisiciones del proyecto (REQ-013)."""
    proyecto = models.ForeignKey(to='Proyecto', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    proveedor = models.CharField(max_length=200, blank=True)
    monto_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente')  # Pendiente, En proceso, Recibido, Cancelado
    fecha_limite = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return f"{self.descripcion} - {self.proyecto.nombre}"


class FeedbackInteresado(models.Model):
    """Recolección de feedback de interesados (REQ-014)."""
    proyecto = models.ForeignKey(to='Proyecto', on_delete=models.CASCADE)
    interesado = models.ForeignKey(to=Interesado, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    valoracion = models.IntegerField(null=True, blank=True, help_text='1-5')
    comentario = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return f"Feedback {self.interesado} - {self.fecha}"


class AlertaRiesgo(models.Model):
    """Sistema de alertas para riesgos del proyecto (REQ-015)."""
    riesgo = models.ForeignKey(to=Riesgo, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(to='Proyecto', on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.CharField(max_length=255)
    fecha_generada = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def __str__(self):
        return self.mensaje
