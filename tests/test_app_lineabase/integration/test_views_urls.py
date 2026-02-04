from django.test import TestCase, Client
from django.urls import reverse
from lineabase.models import Cronograma, Actividad, Presupuesto
from datetime import date
import json

# Es vital heredar de django.test.TestCase para tener self.client
class LineaBaseIntegrationTest(TestCase):
    def setUp(self):
        # El cliente se inicializa solo en django.test.TestCase, 
        # pero puedes asegurarlo así:
        self.client = Client()
        
        # Debemos crear la data mínima para que la vista no lance 404
        # Nota: Asegúrate de que el modelo Proyecto exista si es FK obligatoria
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
        
        self.presupuesto = Presupuesto.objects.create(montoTotal=500.0)

    def test_gantt_chart_json_data(self):
        """Verifica que la vista del Gantt entregue datos JSON válidos."""
        # Esta URL requiere el slug definido en urls.py
        url = reverse('gantt_chart', kwargs={'slug': 'test-cronograma'})
        
        # Ahora self.client funcionará correctamente
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('actividades_json', response.context)
        
        # Validamos que el JSON sea una lista (aunque esté vacía)
        data = json.loads(response.context['actividades_json'])
        self.assertIsInstance(data, list)