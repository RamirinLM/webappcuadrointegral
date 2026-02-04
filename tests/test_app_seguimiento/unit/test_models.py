import pytest
from decimal import Decimal
from datetime import date, timedelta
from seguimiento.models import Seguimiento, CostPerformanceIndexCPI, PlannedValuePV, EarnedValueEV, ShedulePerformanceIndexSPI

@pytest.mark.django_db
class TestSeguimientoLogic:
    def test_cpi_calculation_and_status(self, setup_test_data):
        """Valida el cálculo del CPI y su estado (Bueno/Aceptable/Malo)."""
        # Obtenemos el seguimiento del fixture compartido
        seguimiento = setup_test_data["proyecto"].seguimiento_set.first()
        
        # Creamos un registro de CPI
        cpi = CostPerformanceIndexCPI.objects.create(
            fecha=date.today(),
            seguimiento=seguimiento,
            slug="cpi-test"
        )
        
        # costoPlanificado (costoEstimado) = 1500, costoRealTotal = sum(actividades)
        # Basado en la lógica del modelo
        if cpi.costoReal > 0:
            expected_cpi = cpi.costoPlanificado / cpi.costoReal
            assert cpi.valorCPI == expected_cpi
            assert cpi.estado in ['Bueno', 'Aceptable', 'Malo']

    def test_spi_performance_index(self, setup_test_data):
        """Valida que el SPI relacione correctamente EV y PV."""
        seguimiento = setup_test_data["proyecto"].seguimiento_set.first()
        
        # Creamos los componentes necesarios para el SPI
        ev = EarnedValueEV.objects.create(fecha=date.today(), seguimiento=seguimiento, slug="ev-test")
        pv = PlannedValuePV.objects.create(fecha=date.today(), seguimiento=seguimiento, slug="pv-test")
        spi = ShedulePerformanceIndexSPI.objects.create(fecha=date.today(), seguimiento=seguimiento, slug="spi-test")
        
        if pv.valor > 0:
            assert spi.valor == (ev.valor / pv.valor)
            assert spi.estado in ['Adelantado', 'A tiempo', 'Retrasado']