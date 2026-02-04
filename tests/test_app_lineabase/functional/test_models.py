from django.test import TestCase
from lineabase.models import Cronograma, Actividad, Presupuesto, Recurso
from gestionproyecto.models import Proyecto
from datetime import date

class FuncionalidadModelosTest(TestCase):
    def setUp(self):
        self.proyecto = Proyecto.objects.create(nombre="Proyecto Funcional",
                                                descripcion="Descripción del proyecto funcional",
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2023, 12, 31),
            estado=0,
            slug="proyecto-funcional")
        self.cronograma = Cronograma.objects.create(
            costoEstimado=2000.00,
            fechaInicioProyecto=date(2023, 1, 1),
            fechaFinProyecto=date(2023, 12, 31),
            proyecto=self.proyecto,
            slug="proy-funcional"
        )
        self.presupuesto = Presupuesto.objects.create(montoTotal=3000.00)

    def test_calculo_porcentaje_completado_promedio(self):
        """Valida que el porcentaje del cronograma sea el promedio de sus actividades."""
        Actividad.objects.create(
            descripcion="A1", costoPlanificado=100, costoReal=100,
            fechaInicio=date(2023,1,1), fechaFin=date(2023,1,5),
            fechaInicioReal=date(2023,1,1), fechaFinReal=date(2023,1,5),
            slug="actividad-1",
            porcentajeCompletado=100, esHito=False, cronograma=self.cronograma, presupuesto=self.presupuesto
        )
        Actividad.objects.create(
            descripcion="A2", costoPlanificado=100, costoReal=100,
            fechaInicio=date(2023,1,6), fechaFin=date(2023,1,10),
            fechaInicioReal=date(2023,1,6), fechaFinReal=date(2023,1,10),
            slug="actividad-2",
            porcentajeCompletado=50, esHito=False, cronograma=self.cronograma, presupuesto=self.presupuesto
        )
        # El promedio de 100 y 50 es 75
        self.assertEqual(self.cronograma.porcentajeCompletado, 75)

