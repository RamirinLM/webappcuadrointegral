from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from projects.models import Project, Activity, UserProfile, Notification, Seguimiento
from projects.services import (
    ReportFilters,
    parse_report_filters,
    create_project_with_acta,
    transition_project_approval,
    set_project_modified_if_needed,
    create_notification,
    deliver_notification,
    send_automated_project_report,
    export_project_csv,
)


def set_user_role(user, role):
    UserProfile.objects.filter(user=user).update(role=role)
    user.userprofile.refresh_from_db()


class TestParseReportFilters(TestCase):
    def test_parse_default_filters(self):
        params = {}
        filters = parse_report_filters(params)
        self.assertIsInstance(filters, ReportFilters)
        self.assertEqual(filters.project_status, "")
        self.assertEqual(filters.activity_status, "")
        self.assertEqual(filters.export_format, "html")

    def test_parse_filters_with_values(self):
        params = {
            "project_status": "in_progress",
            "activity_status": "completed",
            "owner_id": "5",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "export_format": "csv",
            "include_cost": "0",
        }
        filters = parse_report_filters(params)
        self.assertEqual(filters.project_status, "in_progress")
        self.assertEqual(filters.activity_status, "completed")
        self.assertEqual(filters.owner_id, "5")
        self.assertEqual(filters.date_from, "2024-01-01")
        self.assertEqual(filters.date_to, "2024-12-31")
        self.assertEqual(filters.export_format, "csv")
        self.assertFalse(filters.include_cost)
        self.assertTrue(filters.include_schedule)

    def test_parse_filters_boolean_values(self):
        params = {"include_cost": "false", "include_schedule": "0", "include_risks": "1"}
        filters = parse_report_filters(params)
        self.assertFalse(filters.include_cost)
        self.assertFalse(filters.include_schedule)
        self.assertTrue(filters.include_risks)


class TestCreateProjectWithActa(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_proj', password='pass')
        set_user_role(self.user, 'gestor_proyectos')

    def test_create_project_with_acta(self):
        from projects.models import ActaConstitucion
        from projects.forms import ProjectForm, ActaConstitucionForm

        project_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'budget': Decimal('10000.00'),
            'status': 'planning',
        }
        acta_data = {
            'alcance': 'Test scope',
            'entregables': 'Deliverables',
            'justificacion': 'Justification',
            'objetivos': 'Objectives',
        }

        project_form = ProjectForm(data=project_data)
        acta_form = ActaConstitucionForm(data=acta_data)

        self.assertTrue(project_form.is_valid(), project_form.errors)
        self.assertTrue(acta_form.is_valid(), acta_form.errors)

        project = create_project_with_acta(
            form=project_form,
            acta_form=acta_form,
            user=self.user
        )

        self.assertIsNotNone(project.id)
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.status, 'planning')
        self.assertEqual(project.created_by, self.user)

        self.assertTrue(hasattr(project, 'actaconstitucion'))
        self.assertEqual(project.actaconstitucion.alcance, 'Test scope')


class TestTransitionProjectApproval(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_trans', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user,
            status='planning'
        )

    def test_approve_planning_project(self):
        new_status, message = transition_project_approval(self.project, 'approve')
        self.assertEqual(new_status, 'in_progress')
        self.assertEqual(message, 'Proyecto aprobado.')

        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'in_progress')

    def test_approve_modified_project(self):
        self.project.status = 'modified'
        self.project.save()

        new_status, message = transition_project_approval(self.project, 'approve')
        self.assertEqual(new_status, 'in_progress')
        self.assertEqual(message, 'Cambios en proyecto aprobados.')

    def test_reject_planning_project(self):
        new_status, message = transition_project_approval(self.project, 'reject')
        self.assertEqual(new_status, 'on_hold')
        self.assertEqual(message, 'Proyecto rechazado.')

        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'on_hold')

    def test_reject_modified_project(self):
        self.project.status = 'modified'
        self.project.save()

        new_status, message = transition_project_approval(self.project, 'reject')
        self.assertEqual(new_status, 'on_hold')
        self.assertEqual(message, 'Cambios en proyecto rechazados.')

    def test_invalid_action_raises_error(self):
        with self.assertRaises(ValueError) as context:
            transition_project_approval(self.project, 'invalid_action')
        self.assertIn('Unsupported', str(context.exception))


class TestSetProjectModifiedIfNeeded(TestCase):
    def setUp(self):
        self.jefe = User.objects.create_user(username='jefe_svc', password='pass')
        set_user_role(self.jefe, 'jefe_departamental')

        self.gestor = User.objects.create_user(username='gestor_svc', password='pass')
        set_user_role(self.gestor, 'gestor_proyectos')

        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.gestor,
            status='in_progress'
        )

    def test_jefe_does_not_change_status(self):
        set_project_modified_if_needed(self.project, self.jefe)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'in_progress')

    def test_non_jefe_changes_status_to_modified(self):
        another_user = User.objects.create_user(username='another_svc', password='pass')
        set_project_modified_if_needed(self.project, another_user)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'modified')


class TestCreateNotification(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser_notif', password='pass', email='test@example.com'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )

    @patch('projects.services.deliver_notification')
    def test_create_notification_default_recipient(self, mock_deliver):
        mock_deliver.return_value = True
        notification = create_notification(
            project=self.project,
            alert_type='cost',
            message='High cost alert'
        )

        self.assertIsNotNone(notification.id)
        self.assertEqual(notification.alert_type, 'cost')
        self.assertEqual(notification.message, 'High cost alert')
        self.assertEqual(notification.recipient, self.user)

    @patch('projects.services.deliver_notification')
    def test_create_notification_custom_recipient(self, mock_deliver):
        mock_deliver.return_value = True
        recipient = User.objects.create_user(
            username='recipient_svc', password='pass', email='recipient@example.com'
        )
        notification = create_notification(
            project=self.project,
            alert_type='schedule',
            message='Schedule alert',
            recipient=recipient
        )

        self.assertEqual(notification.recipient, recipient)


class TestDeliverNotification(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser_deliv', password='pass', email='test@example.com'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )

    @patch('projects.services.send_mail')
    def test_deliver_notification_success(self, mock_send_mail):
        notification = Notification.objects.create(
            project=self.project,
            recipient=self.user,
            alert_type='cost',
            message='Test notification'
        )
        mock_send_mail.reset_mock()
        result = deliver_notification(notification)
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

        notification.refresh_from_db()
        self.assertTrue(notification.sent)

    @patch('projects.services.send_mail')
    def test_deliver_notification_no_recipient(self, mock_send_mail):
        other_user = User.objects.create_user(
            username='other_noemail', password='pass', email=''
        )
        notification = Notification.objects.create(
            project=self.project,
            recipient=other_user,
            alert_type='cost',
            message='Test notification'
        )
        result = deliver_notification(notification)
        self.assertFalse(result)
        mock_send_mail.assert_not_called()

    @patch('projects.services.send_mail')
    def test_deliver_notification_no_email(self, mock_send_mail):
        self.user.email = ''
        self.user.save()

        notification = Notification.objects.create(
            project=self.project,
            recipient=self.user,
            alert_type='cost',
            message='Test notification'
        )
        result = deliver_notification(notification)
        self.assertFalse(result)
        mock_send_mail.assert_not_called()

    @patch('projects.services.send_mail')
    def test_deliver_notification_send_fails(self, mock_send_mail):
        mock_send_mail.side_effect = Exception("SMTP Error")

        notification = Notification.objects.create(
            project=self.project,
            recipient=self.user,
            alert_type='cost',
            message='Test notification'
        )
        mock_send_mail.reset_mock()
        result = deliver_notification(notification)
        self.assertFalse(result)


class TestSendAutomatedProjectReport(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser_report', password='pass', email='test@example.com'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='completed',
            cost=Decimal('100.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='pending',
            cost=Decimal('200.00')
        )

    @patch('projects.services.send_mail')
    @patch('projects.services.render_to_string')
    def test_send_automated_project_report_success(self, mock_render, mock_send_mail):
        mock_render.return_value = '<html>Report</html>'

        result = send_automated_project_report(self.project)
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    def test_send_automated_project_report_no_email(self):
        self.user.email = ''
        self.user.save()

        result = send_automated_project_report(self.project)
        self.assertFalse(result)


class TestExportProjectCsv(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_csv', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        self.activity1 = Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='completed',
            cost=Decimal('100.00')
        )
        self.activity2 = Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='pending',
            cost=Decimal('200.00')
        )

    def test_export_project_csv(self):
        activities = self.project.activity_set.all()
        response = export_project_csv(self.project, activities)

        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('Test Project', response['Content-Disposition'])

        content = response.content.decode('utf-8')
        self.assertIn('Activity', content)
        self.assertIn('Activity 1', content)
        self.assertIn('Activity 2', content)
        self.assertIn('completed', content)
        self.assertIn('pending', content)


class TestTrafficLightStatus(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_tl', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            created_by=self.user
        )

    def test_traffic_light_gray_without_seguimientos(self):
        status = self.project.get_traffic_light_status()
        self.assertEqual(status, 'gray')

    def test_traffic_light_green(self):
        Activity.objects.create(
            project=self.project,
            name='Completed Activity',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='completed',
            cost=Decimal('1000.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Pending Activity',
            description='Desc',
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            status='pending',
            cost=Decimal('500.00')
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today() + timedelta(days=15),
            observacion='Good progress'
        )
        status = self.project.get_traffic_light_status()
        self.assertEqual(status, 'green')

    def test_traffic_light_yellow(self):
        seg_fecha = date.today() + timedelta(days=3)
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=seg_fecha,
            status='completed',
            cost=Decimal('900.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Desc',
            start_date=date.today(),
            end_date=seg_fecha,
            status='in_progress',
            cost=Decimal('100.00')
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=seg_fecha,
            observacion='Warning'
        )
        status = self.project.get_traffic_light_status()
        self.assertEqual(status, 'yellow')

    def test_traffic_light_red(self):
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='in_progress',
            cost=Decimal('1000.00')
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            observacion='Critical'
        )
        status = self.project.get_traffic_light_status()
        self.assertEqual(status, 'red')

    def test_traffic_light_uses_most_recent_seguimiento(self):
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='completed',
            cost=Decimal('1000.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Desc',
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            status='in_progress',
            cost=Decimal('1000.00')
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today() - timedelta(days=10),
            observacion='Old'
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            observacion='New'
        )
        status = self.project.get_traffic_light_status()
        self.assertEqual(status, 'red')
