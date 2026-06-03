"""
Integration tests for EVM S-curves end-to-end flow.

Tests the complete chain:
  1. Create project with activities at different stages
  2. Create multiple Seguimientos at different dates
  3. Verify EVM metrics evolve correctly over time
  4. Verify cumulative PV/EV/AC arrays for S-curves
"""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from projects.models import Project, Activity, Seguimiento


class EVMIntegrationTest(TestCase):
    """
    Flujo completo: proyecto → actividades con distinto avance →
    múltiples seguimientos → métricas EVM correctas en cada corte.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='gestor', password='pass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()

        # Línea de tiempo del proyecto
        self.project_start = date(2026, 1, 1)
        self.project_end = date(2026, 6, 30)

        self.project = Project.objects.create(
            name='Proyecto Integración EVM',
            description='Test integración S-curves',
            start_date=self.project_start,
            end_date=self.project_end,
            budget=Decimal('100000.00'),
            created_by=self.user,
        )

        # ── Actividades con fechas escalonadas ──
        # Actividad 1: completa, terminó temprano, costó menos
        self.act1 = Activity.objects.create(
            project=self.project, name='Investigación',
            description='Investigación inicial', cost=Decimal('20000.00'),
            start_date=date(2026, 1, 15), end_date=date(2026, 2, 15),
            status='completed',
            actual_cost=Decimal('18000.00'),
            actual_end_date=date(2026, 2, 10),
        )
        # Actividad 2: completa, terminó a tiempo, costó lo previsto
        self.act2 = Activity.objects.create(
            project=self.project, name='Diseño',
            description='Diseño del sistema', cost=Decimal('30000.00'),
            start_date=date(2026, 2, 1), end_date=date(2026, 3, 31),
            status='completed',
            actual_cost=Decimal('30000.00'),
            actual_end_date=date(2026, 3, 31),
        )
        # Actividad 3: en progreso, end_date futuro, sin costo real aún
        self.act3 = Activity.objects.create(
            project=self.project, name='Implementación',
            description='Implementación del sistema', cost=Decimal('40000.00'),
            start_date=date(2026, 3, 15), end_date=date(2026, 5, 31),
            status='in_progress',
        )
        # Actividad 4: pendiente, arranca después
        self.act4 = Activity.objects.create(
            project=self.project, name='Pruebas',
            description='Pruebas del sistema', cost=Decimal('10000.00'),
            start_date=date(2026, 5, 1), end_date=date(2026, 6, 15),
            status='pending',
        )

    def _crear_seguimiento(self, fecha):
        """Crea seguimiento y retorna el objeto refrescado de BD."""
        s = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=fecha,
            observacion=f'Corte {fecha.isoformat()}',
        )
        s.refresh_from_db()
        return s

    # ── Corte 1: 15-feb (solo Investigación debió terminar) ────────

    def test_corte_15_feb(self):
        """
        15-feb: solo Investigación (end_date=15-feb) debió terminar.
        Se completó temprano (10-feb) y costó menos.
        """
        s = self._crear_seguimiento(date(2026, 2, 15))

        # PV: Investigación(20000) + Diseño(30000)? No → end_date = 31-mar > 15-feb
        # Solo Investigación cuyo end_date ≤ 15-feb
        self.assertEqual(s.pv, Decimal('20000'))

        # EV: Investigación completada (10-feb ≤ 15-feb)
        self.assertEqual(s.ev, Decimal('20000'))

        # AC: costo real de Investigación
        self.assertEqual(s.ac, Decimal('18000'))

        # SV: 20000 - 20000 = 0 (a tiempo)
        self.assertEqual(s.sv, Decimal('0'))

        # CV: 20000 - 18000 = 2000 (bajo presupuesto)
        self.assertEqual(s.cv, Decimal('2000'))

    # ── Corte 2: 31-mar (Investigación + Diseño) ──────────────────

    def test_corte_31_mar(self):
        """
        31-mar: Investigación y Diseño debieron completarse.
        Implementación recién empezó (end_date=31-may > 31-mar, pending).
        """
        s = self._crear_seguimiento(date(2026, 3, 31))

        # PV: Investigación(20000) + Diseño(30000) = 50000
        # (Implementación end_date=31-may > 31-mar → no incluida)
        self.assertEqual(s.pv, Decimal('50000'))

        # EV: Investigación + Diseño = 50000 (ambas completadas)
        self.assertEqual(s.ev, Decimal('50000'))

        # AC: 18000 + 30000 = 48000
        self.assertEqual(s.ac, Decimal('48000'))

        # SV: 50000 - 50000 = 0
        self.assertEqual(s.sv, Decimal('0'))

        # CV: 50000 - 48000 = 2000
        self.assertEqual(s.cv, Decimal('2000'))

    # ── Corte 3: 15-may (en medio de Implementación) ─────────────

    def test_corte_15_may(self):
        """
        15-may: Investigación y Diseño completas.
        Implementación debió avanzar pero no está completa.
        """
        s = self._crear_seguimiento(date(2026, 5, 15))

        # PV: Investigación(20000) + Diseño(30000) + Implementación(40000) = 90000
        # (end_date=31-may > 15-may? No! 31-may > 15-may → NO incluida)

        # Wait, actually: Implementación end_date = 31-may, corte = 15-may
        # 31-may > 15-may → NO incluida en PV
        self.assertEqual(s.pv, Decimal('50000'))

        # EV: Investigación + Diseño = 50000 (Implementación no completada)
        self.assertEqual(s.ev, Decimal('50000'))

        # AC: 18000 + 30000 = 48000
        self.assertEqual(s.ac, Decimal('48000'))

    # ── Corte 4: 30-jun (fin del proyecto) ────────────────────────

    def test_corte_30_jun(self):
        """
        30-jun: todas las actividades debieron terminar.
        Implementación y Pruebas no están completas → atrasado.
        """
        s = self._crear_seguimiento(date(2026, 6, 30))

        # PV: Investigación(20000) + Diseño(30000) + Implementación(40000) + Pruebas(10000) = 100000
        self.assertEqual(s.pv, Decimal('100000'))

        # EV: solo Investigación + Diseño = 50000
        self.assertEqual(s.ev, Decimal('50000'))

        # AC: solo 18000 + 30000 = 48000
        self.assertEqual(s.ac, Decimal('48000'))

        # SV: 50000 - 100000 = -50000 (atrasado)
        self.assertEqual(s.sv, Decimal('-50000'))

        # CV: 50000 - 48000 = 2000
        self.assertEqual(s.cv, Decimal('2000'))

        # SPI: 50000 / 100000 = 0.5
        self.assertAlmostEqual(float(s.spi), 0.5, places=2)

        # CPI: 50000 / 48000 ≈ 1.04 (campo DecimalField places=2)
        self.assertAlmostEqual(float(s.cpi), 1.04, places=2)

    # ── Evolución temporal (S-curves) ──────────────────────────────

    def test_evm_metrics_evolve_correctly_over_time(self):
        """
        Crea múltiples seguimientos en fechas clave y verifica que
        PV, EV, AC evolucionan de forma acumulativa correcta.
        """
        s1 = self._crear_seguimiento(date(2026, 2, 15))
        s2 = self._crear_seguimiento(date(2026, 3, 31))
        s3 = self._crear_seguimiento(date(2026, 6, 30))

        # PV: debe ser no decreciente (planeado acumulado)
        self.assertGreaterEqual(s2.pv, s1.pv)
        self.assertGreaterEqual(s3.pv, s2.pv)

        # EV: debe ser no decreciente (ganado acumulado)
        self.assertGreaterEqual(s2.ev, s1.ev)
        self.assertGreaterEqual(s3.ev, s2.ev)

        # AC: debe ser no decreciente (costo real acumulado)
        self.assertGreaterEqual(s2.ac, s1.ac)
        self.assertGreaterEqual(s3.ac, s2.ac)

        # En corte 1: PV=20000, EV=20000 → SV=0
        self.assertEqual(s1.sv, Decimal('0'))
        # En corte 2: PV=50000, EV=50000 → SV=0
        self.assertEqual(s2.sv, Decimal('0'))
        # En corte 3: PV=100000, EV=50000 → SV=-50000
        self.assertEqual(s3.sv, Decimal('-50000'))

    # ── Borde: Sin actividades ─────────────────────────────────────

    def test_empty_project_has_zero_metrics(self):
        """Proyecto sin actividades: todas las métricas en 0."""
        empty_project = Project.objects.create(
            name='Vacio',
            description='Sin actividades',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            created_by=self.user,
        )
        s = Seguimiento.objects.create(
            proyecto=empty_project,
            fecha=date(2026, 3, 1),
        )
        s.refresh_from_db()
        self.assertEqual(s.pv, Decimal('0'))
        self.assertEqual(s.ev, Decimal('0'))
        self.assertEqual(s.ac, Decimal('0'))
        self.assertEqual(s.sv, Decimal('0'))
        self.assertEqual(s.cv, Decimal('0'))
        self.assertEqual(s.spi, Decimal('0'))
        self.assertEqual(s.cpi, Decimal('0'))
