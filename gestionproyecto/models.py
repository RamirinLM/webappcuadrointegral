from django.db import models
from django.contrib.auth.models import User

ESTADO = [
    (0, 'Iniciado'),
    (1, 'En Progreso'),
    (2, 'Completado'),
    (3, 'Cancelado'), 
]

# Create your models here.
class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    class Meta:
        abstract = True

class Interesado(Persona):
    rol = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

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
