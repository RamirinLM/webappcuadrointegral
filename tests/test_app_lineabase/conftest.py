import pytest

@pytest.fixture
def setup_test_data(db_access, test_user):
    """Configurar datos de prueba para la aplicación lineabase"""
    from gestionproyecto.models import Proyecto, Interesado, ActaConstitucion
    from lineabase.models import Cronograma, Presupuesto
    from datetime import date, timedelta
    
     # Crear interesado
    interesado = Interesado.objects.create(
        nombre='Juan',
        apellido='Perez',
        email='juan@example.com',
        rol='Cliente',
        slug='juan-perez'
    )
    
    # Crear acta
    acta = ActaConstitucion.objects.create(
        alcance='Proyecto de prueba E2E',
        objetivos='Probar funcionalidades E2E',
        entregables='Pruebas funcionales',
        justificacion='Validar integración completa',
        usuario=test_user,
        slug='acta-e2e'
    )
    
    # Crear proyecto
    proyecto = Proyecto.objects.create(
        nombre='Proyecto E2E Test',
        descripcion='Proyecto para pruebas end-to-end',
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=30),
        estado=1,
        acta_constitucion=acta,
        slug='proyecto-e2e-test'
    )
    
    proyecto.interesados.add(interesado)

    # Crear cronograma
    # IMPORTANTE: Asegúrate de que los campos coincidan exactamente con models.py
    cronograma = Cronograma.objects.create(
        costoEstimado=1500.00,
        fechaInicioProyecto=date.today(),
        fechaFinProyecto=date.today() + timedelta(days=30),
        proyecto=proyecto,
        slug='cronograma-e2e'
    )
    
    presupuesto = Presupuesto.objects.create(montoTotal=2000.00, slug='presupuesto-e2e')
   
    return {
        "proyecto": proyecto,
        "cronograma": cronograma,
        "presupuesto": presupuesto
    }