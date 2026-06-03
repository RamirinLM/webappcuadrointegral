"""
Unit tests for EVM (Earned Value Management) metrics calculation.

Tests Seguimiento.calculate_metrics() in isolation:
  - PV (Planned Value)
  - EV (Earned Value)
  - AC (Actual Cost)
  - SV (Schedule Variance)
  - CV (Cost Variance)
  - SPI / CPI
  - Edge cases: no activities, zero costs, no completed activities
"""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from projects.models import Project, Activity, Seguimiento


class EVMMetricsCalculationTest(TestCase):
    """Verifica los cálculos de métricas EVM en Seguimiento."""

    def setUp(self):
        self.user = User.objects.create_user(username='gestor', password='pass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.today = date(2026, 6, 1)

        self.project = Project.objects.create(
            name='Proyecto EVM Test',
            description='Test de métricas',
            start_date=self.today - timedelta(days=30),
            end_date=self.today + timedelta(days=60),
            budget=Decimal('50000.00'),
            created_by=self.user,
        )

    def _create_activity(self, name, end_date_offset, cost, status='pending',
                         actual_cost=None, actual_end_date_offset=None):
        """Helper para crear actividades con fechas relativas a self.today."""
        return Activity.objects.create(
            project=self.project,
            name=name,
            description='Actividad de prueba',
            start_date=self.today - timedelta(days=20),
            end_date=self.today + timedelta(days=end_date_offset),
            cost=Decimal(str(cost)),
            actual_cost=Decimal(str(actual_cost)) if actual_cost is not None else None,
            status=status,
            actual_end_date=(
                self.today + timedelta(days=actual_end_date_offset)
                if actual_end_date_offset is not None else None
            ),
        )

    def _create_seguimiento(self, fecha_offset=0):
        """Crea un seguimiento y retorna sus métricas calculadas."""
        s = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=self.today + timedelta(days=fecha_offset),
            observacion='Test',
        )
        s.refresh_from_db()
        return s

    # ── PV (Planned Value) ──────────────────────────────────────────

    def test_pv_includes_activities_whose_plan_end_is_before_cutoff(self):
        """PV suma el costo planificado de actividades con end_date ≤ fecha."""
        self._create_activity('A1', end_date_offset=-5, cost=1000, status='pending')
        self._create_activity('A2', end_date_offset=10, cost=2000, status='pending')
        s = self._create_seguimiento(fecha_offset=0)  # fecha = self.today

        # A1: end_date = today - 5 ≤ today → incluida
        # A2: end_date = today + 10 > today → NO incluida
        self.assertEqual(s.pv, Decimal('1000'))

    def test_pv_is_zero_when_no_activities_end_before_cutoff(self):
        """PV = 0 si ninguna actividad tiene end_date ≤ fecha."""
        self._create_activity('A1', end_date_offset=5, cost=1000)
        s = self._create_seguimiento(fecha_offset=0)
        self.assertEqual(s.pv, Decimal('0'))

    def test_pv_with_multiple_activities_before_cutoff(self):
        """PV suma todas las actividades cuyo end_date ≤ fecha."""
        self._create_activity('A1', end_date_offset=-10, cost=1000)
        self._create_activity('A2', end_date_offset=-5, cost=2000)
        self._create_activity('A3', end_date_offset=10, cost=4000)
        s = self._create_seguimiento(fecha_offset=0)
        self.assertEqual(s.pv, Decimal('3000'))

    # ── EV (Earned Value) ───────────────────────────────────────────

    def test_ev_includes_completed_activities_with_actual_end_before_cutoff(self):
        """EV suma el costo planificado de actividades completadas."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=1000,
            status='completed', actual_end_date_offset=-2,
        )
        self._create_activity('A2', end_date_offset=10, cost=2000)
        s = self._create_seguimiento(fecha_offset=0)

        # A1: completed, actual_end ≤ today → EV incluye
        # A2: pending → NO incluida
        self.assertEqual(s.ev, Decimal('1000'))

    def test_ev_uses_fallback_when_actual_end_date_is_null(self):
        """Si completed pero sin actual_end_date, usa end_date como fallback."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=1500,
            status='completed', actual_end_date_offset=None,
        )
        s = self._create_seguimiento(fecha_offset=0)

        # A1: completed, sin actual_end_date, end_date (today-5) ≤ fecha → incluida
        self.assertEqual(s.ev, Decimal('1500'))

    def test_ev_excludes_completed_outside_cutoff_without_actual_end_date(self):
        """Fallback NO incluye si end_date > fecha."""
        self._create_activity(
            'A1', end_date_offset=5, cost=1500,
            status='completed', actual_end_date_offset=None,
        )
        s = self._create_seguimiento(fecha_offset=0)

        # A1: completed, sin actual_end_date, end_date (today+5) > fecha → NO incluida
        self.assertEqual(s.ev, Decimal('0'))

    # ── AC (Actual Cost) ────────────────────────────────────────────

    def test_ac_sums_actual_cost_of_completed_activities(self):
        """AC suma el costo REAL de actividades completadas."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=1000,
            status='completed', actual_cost=800, actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=0)

        self.assertEqual(s.ac, Decimal('800'))

    def test_ac_falls_back_to_planned_cost_when_no_actual_cost(self):
        """Si completed pero sin actual_cost, AC usa el planificado."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=1000,
            status='completed', actual_cost=None, actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=0)

        self.assertEqual(s.ac, Decimal('1000'))  # fallback a cost planificado

    # ── SV (Schedule Variance) ──────────────────────────────────────

    def test_sv_positive_when_ahead_of_schedule(self):
        """SV = EV - PV; positivo = adelantado."""
        self._create_activity(
            'A1', end_date_offset=10, cost=2000,
            status='completed', actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=0)

        # PV: 0 (ninguna actividad con end_date ≤ fecha)
        # EV: 2000 (A1 completada antes de la fecha)
        # SV = 2000 - 0 = 2000
        self.assertEqual(s.sv, Decimal('2000'))

    def test_sv_negative_when_behind_schedule(self):
        """SV negativo = atrasado."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=2000,
            status='pending',
        )
        s = self._create_seguimiento(fecha_offset=0)

        # PV: 2000 (end_date ≤ fecha)
        # EV: 0 (ninguna completada)
        # SV = 0 - 2000 = -2000
        self.assertEqual(s.sv, Decimal('-2000'))

    # ── CV (Cost Variance) ──────────────────────────────────────────

    def test_cv_positive_when_under_budget(self):
        """CV = EV - AC; positivo = bajo presupuesto."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=2000,
            status='completed', actual_cost=1500, actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=0)

        # EV: 2000 (planificado)
        # AC: 1500 (real)
        # CV = 2000 - 1500 = 500
        self.assertEqual(s.cv, Decimal('500'))

    def test_cv_negative_when_over_budget(self):
        """CV negativo = sobre presupuesto."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=2000,
            status='completed', actual_cost=2500, actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=0)

        # EV: 2000, AC: 2500
        # CV = 2000 - 2500 = -500
        self.assertEqual(s.cv, Decimal('-500'))

    # ── SPI / CPI ──────────────────────────────────────────────────

    def test_spi_greater_than_one_when_ahead(self):
        """SPI = EV/PV > 1 = adelantado."""
        self._create_activity(
            'A1', end_date_offset=-5, cost=2000,
            status='completed', actual_end_date_offset=-2,
        )
        s = self._create_seguimiento(fecha_offset=-10)

        # Fecha = today - 10. A1 end_date = today - 5 > fecha
        # PV = 0, EV = 0 (A1 end_date > fecha, no fallback)
        # SPI = 0 / 0 = 0 (protección división por cero)
        self.assertEqual(s.spi, Decimal('0'))

    def test_cpi_zero_when_ac_is_zero(self):
        """CPI = 0 cuando AC = 0 (protección división por cero)."""
        s = self._create_seguimiento(fecha_offset=0)
        self.assertEqual(s.cpi, Decimal('0'))

    def test_spi_zero_when_pv_is_zero(self):
        """SPI = 0 cuando PV = 0 (protección división por cero)."""
        s = self._create_seguimiento(fecha_offset=0)
        self.assertEqual(s.spi, Decimal('0'))

    # ── Escenarios completos ────────────────────────────────────────

    def test_full_scenario_with_multiple_activities(self):
        """Escenario completo con múltiples actividades en distintos estados."""
        # Actividad completada a tiempo (end_date ≤ fecha, completed)
        self._create_activity(
            'Completada', end_date_offset=-5, cost=3000,
            status='completed', actual_cost=2800, actual_end_date_offset=-3,
        )
        # Actividad completada temprano (end_date > fecha, pero completada antes)
        self._create_activity(
            'Temprana', end_date_offset=10, cost=2000,
            status='completed', actual_cost=1800, actual_end_date_offset=-2,
        )
        # Actividad pendiente con end_date antes de fecha (retrasada)
        self._create_activity(
            'Retrasada', end_date_offset=-3, cost=1500,
            status='pending',
        )
        # Actividad futura (end_date > fecha, pending)
        self._create_activity(
            'Futura', end_date_offset=20, cost=4000,
            status='pending',
        )

        s = self._create_seguimiento(fecha_offset=0)

        # PV: Completada(3000) + Retrasada(1500) = 4500 (end_date ≤ fecha)
        self.assertEqual(s.pv, Decimal('4500'))

        # EV: Completada(3000) + Temprana(2000) = 5000
        self.assertEqual(s.ev, Decimal('5000'))

        # AC: Completada(2800) + Temprana(1800) = 4600
        self.assertEqual(s.ac, Decimal('4600'))

        # SV: 5000 - 4500 = 500 (adelantado)
        self.assertEqual(s.sv, Decimal('500'))

        # CV: 5000 - 4600 = 400 (bajo presupuesto)
        self.assertEqual(s.cv, Decimal('400'))

        # SPI: 5000 / 4500 ≈ 1.11 (campo DecimalField places=2)
        self.assertAlmostEqual(float(s.spi), 1.11, places=2)

        # CPI: 5000 / 4600 ≈ 1.09 (campo DecimalField places=2)
        self.assertAlmostEqual(float(s.cpi), 1.09, places=2)
