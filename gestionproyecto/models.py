from django.db import models
from django.contrib.auth.models import User

ESTADO = [
    (0, 'Iniciado'),
    (1, 'En Progreso'),
    (2, 'Completado'),
    (3, 'Cancelado'), 
]

# Create your models here.
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.IntegerField(choices=ESTADO, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.nombre
    
class ActaConstitucion(models.Model):
    alcance = models.TextField()
    objetivos = models.TextField()
    entregables = models.TextField()
    justificacion = models.TextField()
    proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()

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
    proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"Comunicación con {self.interesado.nombre} para el proyecto {self.proyecto.nombre}"

class Riesgo(models.Model):
    descripcion = models.TextField()
    probabilidad = models.FloatField()
    impacto = models.FloatField()
    estrategia_mitigacion = models.TextField()
    proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Riesgo para el proyecto {self.proyecto.nombre}"

class Alcance(models.Model):
    descripcion = models.TextField()
    metas = models.TextField()
    tiempo = models.IntegerField()
    proyecto = models.ForeignKey(to=Proyecto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alcance del proyecto {self.proyecto.nombre}"