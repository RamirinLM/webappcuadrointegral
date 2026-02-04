import pytest
from datetime import date, timedelta
from gestionproyecto.models import Proyecto, ActaConstitucion
from lineabase.models import Cronograma, Presupuesto, Actividad
from seguimiento.models import Seguimiento

@pytest.fixture
def setup_test_data(db_access, test_user):
    """Configura el entorno completo para pruebas de Seguimiento (EVM)"""
    # 1. Crear Estructura de Proyecto
    acta = ActaConstitucion.objects.create(
        alcance='Pruebas Seguimiento', objetivos='Objetivos', 
        entregables='Entregables', justificacion='Justificación',
        usuario=test_user, slug='acta-seg'
    )
    proyecto = Proyecto.objects.create(
        nombre='Proyecto E2E Test', fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=30), 
        acta_constitucion=acta, slug='proy-seg'
    )

    # 2. Crear Línea Base (Necesaria para CPI/SPI/EV)
    presupuesto = Presupuesto.objects.create(montoTotal=1000.00)
    cronograma = Cronograma.objects.create(
        costoEstimado=1000.00, fechaInicioProyecto=date.today(),
        fechaFinProyecto=date.today() + timedelta(days=30),
        proyecto=proyecto, slug='cron-seg'
    )
    
    # Crear una actividad para que costoRealTotal > 0
    Actividad.objects.create(
        descripcion="Actividad Test", costoPlanificado=500, costoReal=500,
        fechaInicio=date.today(), fechaFin=date.today(),
        fechaInicioReal=date.today(), fechaFinReal=date.today(),
        porcentajeCompletado=50, esHito=False, 
        cronograma=cronograma, presupuesto=presupuesto
    )

    # 3. Crear el Seguimiento
    # Añadimos el objeto Seguimiento vinculado al proyecto
    seguimiento = Seguimiento.objects.create(
        observacion="Seguimiento inicial E2E",
        fecha=date.today(),
        proyecto=proyecto,
        slug="seguimiento-e2e"
    )

    return {
        "proyecto": proyecto,
        "cronograma": cronograma,
        "seguimiento": seguimiento
    }