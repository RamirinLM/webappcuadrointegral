"""
Functional tests for the wizard project creation flow.
Verifies:
1. Full create flow forward through all 7 steps
2. Back-navigate from step 7 → step 6, resubmit → no duplicate activities
3. Back-navigate from step 6 → step 5, resubmit → expected duplicate behavior documented
"""
import json
from datetime import date, timedelta

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from decimal import Decimal
from projects.models import Project, Activity, Milestone, Comunicacion, ActaConstitucion
from resources.models import Resource
from risks.models import Risk
from stakeholders.models import Stakeholder


class WizardCreateFlowTestCase(TestCase):
    """Prueba el flujo completo de creación del wizard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='gestor_test', password='testpass123'
        )
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.client.login(username='gestor_test', password='testpass123')

    # ─── helpers ────────────────────────────────────────────────────

    def _post_step(self, step, data):
        """Hace POST a un paso del wizard y retorna la response."""
        return self.client.post(reverse('wizard_step', args=[step]), data)

    def _get_step(self, step):
        """Hace GET a un paso del wizard."""
        return self.client.get(reverse('wizard_step', args=[step]))

    def _assert_redirect_to_step(self, response, expected_step):
        """Verifica que la response redirige al paso esperado."""
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/wizard/step/{expected_step}/', response.url)

    def _session_step(self):
        """Retorna el paso actual guardado en sesión (como entero)."""
        return int(self.client.session['project_wizard']['step'])

    def _session_data(self):
        """Retorna todos los datos del wizard en sesión."""
        return self.client.session.get('project_wizard', {})

    # ─── tests ──────────────────────────────────────────────────────

    def test_full_create_flow_forward(self):
        """
        Crea un proyecto completo navegando hacia adelante por los 7 pasos.
        Verifica que cada paso redirige al siguiente y que los datos se
        persisten en DB al finalizar.
        """
        # Step 0: iniciar wizard → redirect a step 1
        response = self.client.get(reverse('project_wizard'))
        self._assert_redirect_to_step(response, 1)

        # ---- Step 1: Datos del Proyecto ----
        response = self._post_step(1, {
            'name': 'Proyecto Test Forward',
            'description': 'Descripción del proyecto',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'budget': '50000',
        })
        self._assert_redirect_to_step(response, 2)
        self.assertEqual(self._session_step(), 2)

        # ---- Step 2: Acta de Constitución ----
        response = self._post_step(2, {
            'alcance': 'Alcance del proyecto forward',
            'entregables': 'Entregable 1, Entregable 2',
            'justificacion': 'Justificación del proyecto',
            'objetivos': 'Objetivo general y específicos',
        })
        self._assert_redirect_to_step(response, 3)
        self.assertEqual(self._session_step(), 3)

        # Verificar que se creó el proyecto y el acta
        session = self._session_data()
        project_id = session.get('project_id')
        self.assertIsNotNone(project_id)
        project = Project.objects.get(id=project_id)
        self.assertEqual(project.name, 'Proyecto Test Forward')
        self.assertTrue(hasattr(project, 'actaconstitucion'))
        self.assertEqual(project.actaconstitucion.alcance, 'Alcance del proyecto forward')

        # ---- Step 3: Stakeholders ----
        response = self._post_step(3, {
            'stakeholders': [],
            'new_stakeholders': json.dumps([]),
        })
        self._assert_redirect_to_step(response, 4)
        self.assertEqual(self._session_step(), 4)

        # ---- Step 4: Alcance Detallado ----
        response = self._post_step(4, {
            'descripcion': 'Alcance técnico detallado forward',
            'objetivos': 'Objetivos específicos medibles',
        })
        self._assert_redirect_to_step(response, 5)
        self.assertEqual(self._session_step(), 5)

        # Verificar alcance en DB
        project.refresh_from_db()
        self.assertTrue(hasattr(project, 'alcance'))

        # ---- Step 5: Riesgos y Comunicación ----
        risks = json.dumps([{
            'description': 'Riesgo de presupuesto',
            'probability': 'medium',
            'impact': 'high',
            'mitigation_plan': 'Monitorear gastos semanalmente',
            'identified_by': 'gestor_test',
        }])
        communications = json.dumps([{
            'type': 'email',
            'description': 'Reporte semanal de avance',
            'recipient': '',
        }])
        response = self._post_step(5, {
            'risks': risks,
            'communications': communications,
        })
        self._assert_redirect_to_step(response, 6)
        self.assertEqual(self._session_step(), 6)

        # Verificar riesgo y comunicación en DB
        self.assertEqual(Risk.objects.filter(project=project).count(), 1)
        self.assertEqual(Comunicacion.objects.filter(proyecto=project).count(), 1)

        # ---- Step 6: Actividades y Recursos ----
        activities = json.dumps([
            {
                'id': 'act_0',
                'name': 'Análisis de requisitos',
                'description': 'Relevar y documentar requisitos',
                'start_date': '2026-02-01',
                'end_date': '2026-03-01',
                'cost': '5000',
                'predecessor': None,
                'resources': [
                    {
                        'name': 'Analista',
                        'type': 'human',
                        'quantity': 1,
                        'cost_per_unit': '3000',
                    }
                ],
            },
            {
                'id': 'act_1',
                'name': 'Desarrollo',
                'description': 'Implementar solución',
                'start_date': '2026-03-02',
                'end_date': '2026-06-01',
                'cost': '15000',
                'predecessor': None,
                'resources': [],
            },
        ])
        response = self._post_step(6, {'activities': activities})
        self._assert_redirect_to_step(response, 7)
        self.assertEqual(self._session_step(), 7)

        # Verificar actividades en DB (2)
        self.assertEqual(Activity.objects.filter(project=project).count(), 2)

        # ---- Step 7: Hitos ----
        # Obtener IDs reales de las actividades desde la sesión
        session = self._session_data()
        act_id_0 = session['activities'][0]['id']
        act_id_1 = session['activities'][1]['id']

        milestones = json.dumps([
            {
                'id': 'mile_0',
                'name': 'Hito de análisis',
                'description': 'Análisis completado',
                'due_date': '2026-03-01',
                'phase': 'planning',
                'is_phase_gate': True,
                'activities': [act_id_0],
            },
            {
                'id': 'mile_1',
                'name': 'Hito de desarrollo',
                'description': 'Desarrollo completado',
                'due_date': '2026-06-01',
                'phase': 'execution',
                'is_phase_gate': False,
                'activities': [act_id_1],
            },
        ])
        response = self._post_step(7, {'milestones': milestones})
        self.assertEqual(response.status_code, 302)
        # Redirige a project_detail
        self.assertIn(f'/projects/{project_id}/', response.url)

        # Verificar estado final
        project.refresh_from_db()
        self.assertEqual(project.name, 'Proyecto Test Forward')

        # 2 actividades en DB (sin duplicados)
        self.assertEqual(Activity.objects.filter(project=project).count(), 2)

        # 2 hitos en DB
        self.assertEqual(Milestone.objects.filter(project=project).count(), 2)

        # 1 riesgo, 1 comunicación
        self.assertEqual(Risk.objects.filter(project=project).count(), 1)
        self.assertEqual(Comunicacion.objects.filter(proyecto=project).count(), 1)

        # Wizard data debe estar limpia
        self.assertNotIn('project_wizard', self.client.session)

    def test_back_navigate_step7_to_step6_no_duplicates(self):
        """
        Navegar de step 7 hacia atrás a step 6 y reenviar actividades
        NO debe duplicarlas. Verifica la lógica de existing_activities
        que ahora funciona en create mode (no solo edit mode).
        """
        # Completar wizard hasta POST de step 6 → redirige a step 7
        self._complete_wizard_up_to(6)

        # Verificar: 3 actividades en DB antes del back-navigate
        session = self._session_data()
        self.assertEqual(self._session_step(), 7)
        project_id = session['project_id']
        project = Project.objects.get(id=project_id)
        self.assertEqual(Activity.objects.filter(project=project).count(), 3)

        # GET a step 6 (simula back-navigate del usuario)
        response = self._get_step(6)
        self.assertEqual(response.status_code, 200)

        # Las actividades en sesión deben tener IDs reales (pueden venir como string
        # porque serialize_form_data convierte integers a string, pero int() los resuelve)
        session = self._session_data()
        current_activities = session.get('activities', [])
        for act in current_activities:
            raw_id = act['id']
            try:
                int(raw_id)
            except (ValueError, TypeError):
                self.fail(
                    f"ID debe ser convertible a entero, se obtuvo {type(raw_id)}: {raw_id}"
                )

        # Reenviar step 6 con las mismas actividades
        response = self._post_step(6, {
            'activities': json.dumps(current_activities),
        })
        self._assert_redirect_to_step(response, 7)

        # VERIFICACIÓN CLAVE: NO deben haber duplicados
        self.assertEqual(
            Activity.objects.filter(project=project).count(),
            3,
            "Se crearon actividades duplicadas al reenviar step 6 "
            "después de navegar hacia atrás desde step 7"
        )

        # Completar el wizard
        milestones = json.dumps([
            {
                'id': 'mile_0',
                'name': 'Hito final',
                'description': 'Proyecto completado',
                'due_date': '2026-06-30',
                'phase': 'closure',
                'is_phase_gate': True,
                'activities': [],
            },
        ])
        response = self._post_step(7, {'milestones': milestones})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('project_wizard', self.client.session)

        # Estado final: 3 actividades (sin duplicados)
        self.assertEqual(Activity.objects.filter(project=project).count(), 3)

    def test_back_navigate_step6_to_step5_no_duplicates(self):
        """
        Navegar de step 6 hacia atrás a step 5 y reenviar riesgos/comunicaciones
        NO debe duplicarlos. Verifica la lógica de update-or-create agregada.
        """
        # Completar wizard hasta step 6 (el helper POSTea step 5 internamente)
        self._complete_wizard_up_to(6)

        session = self._session_data()
        project_id = session['project_id']
        project = Project.objects.get(id=project_id)

        # Verificar estado inicial después de la primera vez por step 5
        initial_risk_count = Risk.objects.filter(project=project).count()
        initial_comm_count = Comunicacion.objects.filter(proyecto=project).count()
        self.assertGreaterEqual(initial_risk_count, 1)
        self.assertGreaterEqual(initial_comm_count, 1)

        # Los riesgos/comms en sesión ya tienen IDs reales (números serializados como str)
        session_risks = session.get('risks', [])
        session_comms = session.get('communications', [])
        for r in session_risks:
            self.assertTrue(str(r.get('id', '')).isdigit(),
                            f"Risk ID debe ser numérico después de 1er POST: {r.get('id')}")
        for c in session_comms:
            self.assertTrue(str(c.get('id', '')).isdigit(),
                            f"Comm ID debe ser numérico después de 1er POST: {c.get('id')}")

        # GET a step 5 (simula back-navigate del usuario)
        response = self._get_step(5)
        self.assertEqual(response.status_code, 200)

        # Reenviar step 5 con los mismos riesgos/comunicaciones
        session = self._session_data()
        risks = json.dumps(session.get('risks', []))
        communications = json.dumps(session.get('communications', []))
        response = self._post_step(5, {
            'risks': risks,
            'communications': communications,
        })
        self._assert_redirect_to_step(response, 6)

        # VERIFICACIÓN: NO deben haber duplicados
        self.assertEqual(
            Risk.objects.filter(project=project).count(),
            initial_risk_count,
            "Riesgos duplicados al reenviar step 5 después del fix"
        )
        self.assertEqual(
            Comunicacion.objects.filter(proyecto=project).count(),
            initial_comm_count,
            "Comunicaciones duplicadas al reenviar step 5 después del fix"
        )

    def test_back_navigate_step5_to_step3_no_duplicate_stakeholders(self):
        """
        Navegar de step 5 hacia atrás a step 3 y reenviar no debe crear
        stakeholders duplicados.
        """
        # Completar wizard hasta step 5 (steps 1-4, step 5 queda sin POSTear)
        self.client.get(reverse('project_wizard'))

        self._post_step(1, {
            'name': 'Proyecto Step3 Test',
            'description': 'Test stakeholders back-navigate',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'budget': '50000',
        })
        self._post_step(2, {
            'alcance': 'Alcance test',
            'entregables': 'Entregables test',
            'justificacion': 'Justificación test',
            'objetivos': 'Objetivos test',
        })
        project = Project.objects.get(name='Proyecto Step3 Test')
        project_id = project.id

        # Step 3 — agregar un stakeholder nuevo vía AJAX
        response = self.client.post(
            reverse('wizard_add_stakeholder'),
            {
                'name': 'Nuevo Stakeholder',
                'email': 'nuevo@test.com',
                'role': 'client',
                'interest_level': 'high',
                'power_level': 'high',
                'contact_info': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # POST step 3
        session = self._session_data()
        response = self._post_step(3, {
            'stakeholders': [],
            'new_stakeholders': json.dumps(session.get('new_stakeholders', [])),
        })
        self._assert_redirect_to_step(response, 4)

        # Verificar: 1 stakeholder en el proyecto
        self.assertEqual(
            project.stakeholders.count(), 1,
            "Debe haber 1 stakeholder después del primer POST a step 3"
        )

        # POST step 4 (alcance)
        self._post_step(4, {
            'descripcion': 'Alcance detallado',
            'objetivos': 'Objetivos específicos',
        })

        # GET step 3 (back-navigate)
        response = self._get_step(3)
        self.assertEqual(response.status_code, 200)

        # Reenviar step 3 con los mismos datos
        session = self._session_data()
        response = self._post_step(3, {
            'stakeholders': [],
            'new_stakeholders': json.dumps(session.get('new_stakeholders', [])),
        })
        self._assert_redirect_to_step(response, 4)

        # VERIFICACIÓN: NO debe haber duplicado de stakeholder
        self.assertEqual(
            project.stakeholders.count(), 1,
            "Stakeholder duplicado al reenviar step 3 después del fix"
        )

    def test_back_navigate_step7_to_step6_preserves_milestone_data(self):
        """
        Simula: usuario llega a step 7, agrega hitos, navega atrás a step 6,
        modifica actividades, vuelve a step 7.
        Los hitos no deben perder sus referencias a IDs de actividades.
        """
        # Llegar hasta step 7 después de POSTear step 6
        self._complete_wizard_up_to(6)

        session = self._session_data()
        self.assertEqual(self._session_step(), 7)
        project_id = session['project_id']
        project = Project.objects.get(id=project_id)

        original_activity_count = Activity.objects.filter(project=project).count()
        self.assertEqual(original_activity_count, 3)

        # Usar el endpoint AJAX para agregar un hito (más realista que manipular sesión)
        response = self.client.post(
            reverse('wizard_add_milestone'),
            {
                'name': 'Hito diseño',
                'description': 'Diseño completado',
                'due_date': '2026-04-01',
                'phase': 'planning',
                'is_phase_gate': True,
                'activities': [session['activities'][1]['id']],  # act_1 DB ID
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verificar que el hito está en sesión
        session = self._session_data()
        self.assertIn('milestones', session)
        self.assertEqual(len(session['milestones']), 1)

        # GET a step 6 (simula back-navigate del usuario)
        response = self._get_step(6)
        self.assertEqual(response.status_code, 200)

        session = self._session_data()
        activities = session.get('activities', [])
        milestones_after_get = session.get('milestones', [])
        self.assertEqual(
            len(milestones_after_get), 1,
            "Los hitos deben persistir en sesión al volver a step 6"
        )

        # Modificar: cambiar nombre de primera actividad + agregar nueva
        activities[0]['name'] = 'Actividad Modificada'
        activities.append({
            'id': 'act_new_temp',
            'name': 'Actividad Nueva',
            'description': 'Agregada al volver atrás',
            'start_date': '2026-07-01',
            'end_date': '2026-08-01',
            'cost': '3000',
            'predecessor': None,
            'resources': [],
        })

        # Reenviar step 6 con actividades modificadas
        response = self._post_step(6, {
            'activities': json.dumps(activities),
        })
        self._assert_redirect_to_step(response, 7)

        # Verificar: actividad existente actualizada, nueva creada
        self.assertTrue(
            Activity.objects.filter(project=project, name='Actividad Modificada').exists()
        )
        self.assertEqual(
            Activity.objects.filter(project=project).count(),
            original_activity_count + 1
        )

        # Al volver a step 7, las actividades deben tener IDs convertibles a enteros
        session = self._session_data()
        for act in session.get('activities', []):
            if act['name'] == 'Actividad Nueva':
                try:
                    int(act['id'])
                except (ValueError, TypeError):
                    self.fail(
                        f"La nueva actividad debe tener ID convertible a entero, "
                        f"tiene: {type(act['id'])}: {act['id']}"
                    )

        # Los hitos en sesión deben tener referencias a IDs convertibles a enteros
        for milestone in session.get('milestones', []):
            for act_id in milestone.get('activities', []):
                try:
                    int(act_id)
                except (ValueError, TypeError):
                    self.fail(
                        f"Refs en hitos deben ser IDs convertibles a enteros, "
                        f"tiene: {type(act_id)}: {act_id}"
                    )

        # Completar wizard
        milestones_json = json.dumps(session.get('milestones', []))
        response = self._post_step(7, {'milestones': milestones_json})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('project_wizard', self.client.session)

        # Actividad nueva persistió
        self.assertEqual(
            Activity.objects.filter(project=project).count(),
            original_activity_count + 1
        )
        self.assertTrue(
            Activity.objects.filter(project=project, name='Actividad Nueva').exists()
        )

    def test_back_navigate_step5_data_persists_in_response(self):
        """
        Verifica que al navegar de vuelta a step 5, los riesgos y comunicaciones
        se renderizan correctamente en el HTML (no se pierden por escapejs).
        """
        self._complete_wizard_up_to(6)

        # GET a step 5 (back-navigate)
        response = self._get_step(5)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Verificar que los riesgos se cargan como JSON válido en la variable JS
        self.assertIn('let risks = [', content)
        self.assertIn('Riesgo principal', content)
        self.assertIn('Plan de mitigaci', content)  # con acento
        # NO debe contener \u0027 (escapejs) — eso indica el bug
        self.assertNotIn('\\u0027', content,
                         'escapejs contaminó el JSON. Los datos se renderizarían '
                         'como JS inválido en el navegador.')

        # Verificar comunicaciones
        self.assertIn('let communications = [', content)
        self.assertIn('Reuni', content)
        self.assertIn('quincenal', content)

    def test_back_navigate_step6_data_persists_in_response(self):
        """
        Verifica que al navegar de vuelta a step 6, las actividades se
        renderizan correctamente en el HTML.
        """
        self._complete_wizard_up_to(7)

        # GET a step 6 (back-navigate)
        response = self._get_step(6)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Verificar que las actividades se cargan como JSON válido
        self.assertIn('var activities_data = [', content)
        # json.dumps escapa no-ASCII con ensure_ascii=True, así que
        # 'Investigación' aparece como 'Investigaci\\u00f3n' en el HTML
        self.assertIn('Investigaci', content)
        self.assertIn('Dise\\u00f1o', content)
        self.assertIn('Implementaci', content)
        self.assertNotIn('\\u0027', content,
                         'escapejs contaminó el JSON de actividades.')

        # Verificar que también renderiza el listado
        self.assertIn('activities-list', content)

    def test_back_navigate_step7_data_persists_in_response(self):
        """
        Verifica que al navegar de vuelta a step 7, los hitos se
        renderizan correctamente en el HTML.
        """
        self._complete_wizard_up_to(6)

        session = self._session_data()
        self.assertEqual(self._session_step(), 7)

        # Agregar un hito via AJAX
        response = self.client.post(
            reverse('wizard_add_milestone'),
            {
                'name': 'Hito de prueba',
                'description': 'Descripción del hito',
                'due_date': '2026-06-30',
                'phase': 'closure',
                'is_phase_gate': True,
                'activities': [],
            },
        )
        self.assertEqual(response.status_code, 200)

        # GET a step 6 (back-navigate)
        response = self._get_step(6)
        self.assertEqual(response.status_code, 200)

        # GET a step 7 (volver a step 7)
        response = self._get_step(7)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Verificar que los hitos se cargan como JSON válido
        self.assertIn('let milestones = [', content)
        self.assertIn('Hito de prueba', content)
        self.assertNotIn('\\u0027', content,
                         'escapejs contaminó el JSON de hitos.')

    def test_activity_cost_calculated_from_resources(self):
        """
        Verifica que Activity.cost se calcule automáticamente desde
        la suma de Resource.total_cost al crear proyecto por wizard.
        """
        # Completar wizard hasta step 6 (sin POSTearlo)
        self.client.get(reverse('project_wizard'))
        self._post_step(1, {
            'name': 'Proyecto Cost Test',
            'description': 'Test costo desde recursos',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'budget': '50000',
        })
        self._post_step(2, {
            'alcance': 'Alcance test cost',
            'entregables': 'Entregable 1',
            'justificacion': 'Justificación test',
            'objetivos': 'Objetivos test',
        })
        self._post_step(3, {
            'stakeholders': [],
            'new_stakeholders': json.dumps([]),
        })
        self._post_step(4, {
            'descripcion': 'Alcance detallado',
            'objetivos': 'Objetivos específicos',
        })
        self._post_step(5, {
            'risks': json.dumps([]),
            'communications': json.dumps([]),
        })

        # Step 6 — actividad CON recursos
        activities = json.dumps([
            {
                'id': 'act_0',
                'name': 'Actividad con recursos',
                'description': '',
                'start_date': '2026-02-01',
                'end_date': '2026-02-28',
                'predecessor': None,
                'resources': [
                    {
                        'name': 'Analista Senior',
                        'type': 'human',
                        'quantity': 2,
                        'cost_per_unit': 5000,
                    },
                    {
                        'name': 'Licencia software',
                        'type': 'material',
                        'quantity': 1,
                        'cost_per_unit': 3000,
                    },
                ],
            },
            {
                'id': 'act_1',
                'name': 'Actividad sin recursos',
                'description': '',
                'start_date': '2026-03-01',
                'end_date': '2026-03-31',
                'predecessor': None,
                'resources': [],
            },
        ])
        response = self._post_step(6, {'activities': activities})
        self._assert_redirect_to_step(response, 7)

        session = self._session_data()
        project_id = session['project_id']
        project = Project.objects.get(id=project_id)

        # ── Verificar Actividad con recursos ──
        act_with_res = Activity.objects.get(project=project, name='Actividad con recursos')
        resources = Resource.objects.filter(activity=act_with_res)

        self.assertEqual(resources.count(), 2)
        self.assertEqual(resources[0].total_cost, Decimal('10000'))  # 2 * 5000
        self.assertEqual(resources[1].total_cost, Decimal('3000'))   # 1 * 3000

        # total_planned_cost debe SUMAR los recursos
        self.assertEqual(act_with_res.total_planned_cost, Decimal('13000'))

        # update_cost_from_resources sincronizó self.cost
        act_with_res.refresh_from_db()
        self.assertEqual(act_with_res.cost, Decimal('13000'))

        # ── Verificar Actividad sin recursos ──
        act_no_res = Activity.objects.get(project=project, name='Actividad sin recursos')
        self.assertEqual(Resource.objects.filter(activity=act_no_res).count(), 0)
        # fallback: self.cost es None → 0
        self.assertEqual(act_no_res.total_planned_cost, 0)

        # ── Verificar que eliminar un recurso actualiza el costo ──
        resources[0].delete()
        act_with_res.refresh_from_db()
        self.assertEqual(act_with_res.total_planned_cost, Decimal('3000'))
        self.assertEqual(act_with_res.cost, Decimal('3000'))

        # ── Completar el wizard ──
        milestones = json.dumps([{
            'id': 'mile_0',
            'name': 'Hito final',
            'description': 'Proyecto completado',
            'due_date': '2026-06-30',
            'phase': 'closure',
            'is_phase_gate': True,
            'activities': [],
        }])
        response = self._post_step(7, {'milestones': milestones})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('project_wizard', self.client.session)

        # Verificar estado final
        act_with_res.refresh_from_db()
        self.assertEqual(act_with_res.cost, Decimal('3000'))
        self.assertEqual(Resource.objects.filter(activity=act_with_res).count(), 1)

    # ─── helpers privados ───────────────────────────────────────────

    def _complete_wizard_up_to(self, target_step, with_activities=False):
        """
        Avanza el wizard hasta alcanzar target_step (sin POSTearlo).
        El helper POSTea los pasos ANTERIORES, luego se detiene.
        - target_step=7 → POST 1-6, queda en step 7 (session activa)
        - target_step=6 → POST 1-5, queda en step 6 (session activa)
        - target_step=5 → POST 1-4, queda en step 5
        - etc.
        POSTear target_step queda a cargo del test que llama al helper.
        with_activities solo es relevante para target_step >= 6.
        """
        # Step 0: iniciar wizard
        self.client.get(reverse('project_wizard'))

        self._post_step(1, {
            'name': 'Proyecto BackNav',
            'description': 'Proyecto para test de back-navigate',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'budget': '100000',
        })

        self._post_step(2, {
            'alcance': 'Alcance del proyecto backnav',
            'entregables': 'Entregable A, Entregable B',
            'justificacion': 'Justificación del proyecto',
            'objetivos': 'Objetivos del proyecto backnav',
        })

        self._post_step(3, {
            'stakeholders': [],
            'new_stakeholders': json.dumps([]),
        })

        self._post_step(4, {
            'descripcion': 'Alcance detallado backnav',
            'objetivos': 'Objetivos específicos backnav',
        })

        risks = json.dumps([{
            'description': 'Riesgo principal',
            'probability': 'low',
            'impact': 'medium',
            'mitigation_plan': 'Plan de mitigación',
            'identified_by': 'gestor_test',
        }])
        communications = json.dumps([{
            'type': 'reunion',
            'description': 'Reunión quincenal',
            'recipient': '',
        }])
        self._post_step(5, {
            'risks': risks,
            'communications': communications,
        })

        # Step 6 solo si target_step >= 6
        if target_step >= 6:
            activities = json.dumps([
                {
                    'id': 'act_0',
                    'name': 'Investigación',
                    'description': 'Investigación preliminar',
                    'start_date': '2026-02-01',
                    'end_date': '2026-02-28',
                    'cost': '2000',
                    'predecessor': None,
                    'resources': [],
                },
                {
                    'id': 'act_1',
                    'name': 'Diseño',
                    'description': 'Diseño de la solución',
                    'start_date': '2026-03-01',
                    'end_date': '2026-04-01',
                    'cost': '5000',
                    'predecessor': None,
                    'resources': [],
                },
                {
                    'id': 'act_2',
                    'name': 'Implementación',
                    'description': 'Implementación final',
                    'start_date': '2026-04-02',
                    'end_date': '2026-06-01',
                    'cost': '10000',
                    'predecessor': None,
                    'resources': [],
                },
            ])
            self._post_step(6, {'activities': activities})

        # NOTA: nunca POSTeamos step 7 aquí porque eso limpia la sesión.
        # Los tests que necesiten step 7 lo hacen manualmente.
