"""
Functional tests for EVM S-curves and Financial Summary views.

Tests:
  - evm_curves: status 200, template, chart_data_json, metrics
  - project_financial_summary: status 200, template, context
  - Permission handling for both views
"""
import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from projects.models import Project, Activity, Seguimiento


class EVMCurvesViewTest(TestCase):
    """Pruebas para la vista evm_curves."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='gestor', password='pass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.client.login(username='gestor', password='pass')

        self.today = date(2026, 6, 1)
        self.project = Project.objects.create(
            name='Proyecto EVM',
            description='Test',
            start_date=self.today - timedelta(days=30),
            end_date=self.today + timedelta(days=60),
            budget=Decimal('30000.00'),
            created_by=self.user,
        )
        self.url = reverse('evm_curves', args=[self.project.pk])

    def _create_activity(self, name, end_offset, cost, status='pending',
                         actual_cost=None, actual_end_offset=None):
        return Activity.objects.create(
            project=self.project,
            name=name,
            description='Actividad de prueba',
            start_date=self.today - timedelta(days=20),
            end_date=self.today + timedelta(days=end_offset),
            cost=Decimal(str(cost)),
            actual_cost=Decimal(str(actual_cost)) if actual_cost else None,
            status=status,
            actual_end_date=(
                self.today + timedelta(days=actual_end_offset)
                if actual_end_offset is not None else None
            ),
        )

    def _create_seguimiento(self, offset_days):
        return Seguimiento.objects.create(
            proyecto=self.project,
            fecha=self.today + timedelta(days=offset_days),
        )

    # ── GET / permissions ────────────────────────────────────────────

    def test_evm_curves_returns_200_for_authorized_user(self):
        """Usuario autorizado ve la página 200."""
        self._create_seguimiento(0)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_evm_curves_uses_correct_template(self):
        """Usa el template evm_curves.html."""
        self._create_seguimiento(0)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'projects/evm_curves.html')

    def test_evm_curves_redirects_unauthorized(self):
        """Usuario sin permiso es redirigido al dashboard."""
        other = User.objects.create_user(username='otro', password='pass')
        other.userprofile.role = 'tecnico_proyectos'
        other.userprofile.save()
        self.client.login(username='otro', password='pass')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'))

    # ── Contexto sin seguimientos ─────────────────────────────────────

    def test_evm_curves_empty_chart_data_when_no_seguimientos(self):
        """Sin seguimientos, chart_data_json tiene arrays vacíos."""
        response = self.client.get(self.url)
        chart_data = json.loads(response.context['chart_data_json'])
        self.assertEqual(chart_data, {'labels': [], 'pv': [], 'ev': [], 'ac': []})

    def test_evm_curves_empty_metrics_when_no_seguimientos(self):
        """Sin seguimientos, metrics es diccionario vacío."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['metrics'], {})

    def test_evm_curves_empty_queryset_when_no_seguimientos(self):
        """Sin seguimientos, la queryset está vacía."""
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['seguimientos']), 0)

    # ── Contexto con seguimientos ────────────────────────────────────

    def test_evm_curves_chart_data_has_correct_labels(self):
        """chart_data_json.labels = fechas ISO de los seguimientos."""
        self._create_seguimiento(-10)
        self._create_seguimiento(0)
        self._create_seguimiento(10)
        response = self.client.get(self.url)
        chart_data = json.loads(response.context['chart_data_json'])
        expected = [
            (self.today - timedelta(days=10)).isoformat(),
            self.today.isoformat(),
            (self.today + timedelta(days=10)).isoformat(),
        ]
        self.assertEqual(chart_data['labels'], expected)

    def test_evm_curves_chart_data_arrays_same_length_as_labels(self):
        """pv, ev, ac arrays tienen la misma longitud que labels."""
        for i in range(5):
            self._create_seguimiento(i * 7)
        response = self.client.get(self.url)
        chart_data = json.loads(response.context['chart_data_json'])
        n = len(chart_data['labels'])
        self.assertEqual(len(chart_data['pv']), n)
        self.assertEqual(len(chart_data['ev']), n)
        self.assertEqual(len(chart_data['ac']), n)

    def test_evm_curves_metrics_has_latest_values(self):
        """Metrics contiene sv, cv, spi, cpi del último seguimiento."""
        self._create_activity('A1', end_offset=-5, cost=2000,
                              status='completed', actual_cost=1800,
                              actual_end_offset=-2)
        self._create_seguimiento(0)
        response = self.client.get(self.url)
        metrics = response.context['metrics']
        self.assertIn('sv', metrics)
        self.assertIn('cv', metrics)
        self.assertIn('spi', metrics)
        self.assertIn('cpi', metrics)
        self.assertIn('pv', metrics)
        self.assertIn('ev', metrics)
        self.assertIn('ac', metrics)
        self.assertIn('completed', metrics)
        self.assertIn('total_activities', metrics)

    def test_evm_curves_context_has_project_and_can_edit(self):
        """Contexto incluye project y can_edit."""
        self._create_seguimiento(0)
        response = self.client.get(self.url)
        self.assertEqual(response.context['project'], self.project)
        self.assertIn('can_edit', response.context)

    # ── Financial Summary ────────────────────────────────────────────

    def test_financial_summary_returns_200(self):
        """Financial summary retorna 200 para usuario autorizado."""
        url = reverse('project_financial_summary', args=[self.project.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_financial_summary_uses_correct_template(self):
        """Usa el template financial_summary.html."""
        url = reverse('project_financial_summary', args=[self.project.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'projects/financial_summary.html')

    def test_financial_summary_context_has_all_metrics(self):
        """Contexto incluye budget, activities_cost, total_cost, variance, utilization."""
        self._create_activity('A1', end_offset=-5, cost=5000)
        url = reverse('project_financial_summary', args=[self.project.pk])
        response = self.client.get(url)
        ctx = response.context
        self.assertIn('budget', ctx)
        self.assertIn('activities_cost', ctx)
        self.assertIn('total_cost', ctx)
        self.assertIn('variance', ctx)
        self.assertIn('utilization', ctx)
        self.assertIn('activities', ctx)
        self.assertIn('traffic_light', ctx)
        self.assertEqual(ctx['project'], self.project)

    def test_financial_summary_redirects_unauthorized(self):
        """Usuario sin permiso es redirigido."""
        other = User.objects.create_user(username='otro2', password='pass')
        other.userprofile.role = 'tecnico_proyectos'
        other.userprofile.save()
        self.client.login(username='otro2', password='pass')
        url = reverse('project_financial_summary', args=[self.project.pk])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('dashboard'))

    def test_financial_summary_variance_correct_with_activities(self):
        """Variance refleja budget - activities_cost correctamente."""
        self._create_activity('A1', end_offset=-5, cost=10000)
        self._create_activity('A2', end_offset=10, cost=5000)
        url = reverse('project_financial_summary', args=[self.project.pk])
        response = self.client.get(url)
        # budget = 30000, activities_cost = 15000
        # variance = 30000 - 15000 = 15000
        self.assertEqual(response.context['variance'], Decimal('15000.00'))
