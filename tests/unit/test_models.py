import pytest
from django.test import TestCase
from gestionproyecto.models import Proyecto
from seguimiento.models import Seguimiento

@pytest.mark.django_db
class TestProyectoModel:
    def test_crear_proyecto(self):
        proyecto = Proyecto.objects.create(
            nombre="Proyecto Test",
            descripcion="Descripción de prueba"
        )
        assert proyecto.nombre == "Proyecto Test"
        assert str(proyecto) == "Proyecto Test"
    
    def test_proyecto_estado_default(self):
        proyecto = Proyecto.objects.create(nombre="Test")
        assert proyecto.estado == "pendiente"

@pytest.mark.django_db
class TestSeguimientoModel:
    def test_crear_seguimiento(self, proyecto):
        seguimiento = Seguimiento.objects.create(
            proyecto=proyecto,
            avance=50,
            comentarios="Avance parcial"
        )
        assert seguimiento.avance == 50
        assert seguimiento.proyecto == proyecto