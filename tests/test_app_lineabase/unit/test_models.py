from django.test import TestCase
from lineabase.models import Cronograma, Actividad, Recurso, Presupuesto
from datetime import date, timedelta
from django.contrib.auth.models import User

class LineaBaseModelTest(TestCase):
    def setUp(self):
        # Necesitamos un objeto Proyecto simulado o real dependiendo de la estructura
        # Para este ejemplo, asumimos que existe la relación.
        from gestionproyecto.models import Proyecto
        self.proyecto = Proyecto.objects.create(nombre="Proyecto Test",
            descripcion="Descripción del proyecto test",
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2023, 12, 31),
            estado=0,
            slug="proyecto-test")
        
        self.cronograma = Cronograma.objects.create(
            costoEstimado=1000.00,
            fechaInicioProyecto=date(2023, 1, 1),
            fechaFinProyecto=date(2023, 12, 31),
            proyecto=self.proyecto,
            slug="test-cronograma"
        )
        
        self.presupuesto = Presupuesto.objects.create(montoTotal=5000.00)
        
        self.recurso = Recurso.objects.create(
            nombre="Laptop", cantidad=2, costoUnitario=500.00, slug="recurso-1"
        )

    def test_calculo_costo_real_total(self):
        """Valida que el costo real del cronograma sume sus actividades."""
        Actividad.objects.create(
            descripcion="Actividad 1", costoPlanificado=500, costoReal=400,
            fechaInicio=date(2023, 1, 1), fechaFin=date(2023, 1, 10),
            fechaInicioReal=date(2023, 1, 1), fechaFinReal=date(2023, 1, 10),
            porcentajeCompletado=100, esHito=False, cronograma=self.cronograma,
            presupuesto=self.presupuesto
        )
        self.assertEqual(self.cronograma.costoRealTotal, 400.00)

    def test_diferencia_tiempo_actividad(self):
        """Valida el cálculo de días de diferencia entre fin planificado y real."""
        actividad = Actividad.objects.create(
            descripcion="Retraso", costoPlanificado=100, costoReal=100,
            fechaInicio=date(2023, 1, 1), fechaFin=date(2023, 1, 10),
            fechaInicioReal=date(2023, 1, 1), fechaFinReal=date(2023, 1, 15), # 5 días tarde
            porcentajeCompletado=100, esHito=False, cronograma=self.cronograma,
            presupuesto=self.presupuesto
        )
        # 10 - 15 = -5
        self.assertEqual(actividad.diferenciaTiempo, -5)