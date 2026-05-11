from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Activity, Notification, Project


class NotificationFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="manager", password="testpass", email="manager@example.com")
        self.user.userprofile.role = "gestor_proyectos"
        self.user.userprofile.save()
        self.client.login(username="manager", password="testpass")
        self.project = Project.objects.create(
            name="Proyecto Alertas",
            description="Proyecto con alertas",
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user,
        )

    def test_notification_created_for_high_cost_activity(self):
        activity = Activity.objects.create(
            project=self.project,
            name="Actividad Costosa",
            description="Costo alto",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            cost=15000,
        )
        self.assertTrue(Notification.objects.filter(project=self.project, alert_type="cost").exists())
        activity.description = "Costo alto actualizado"
        activity.save()
        self.assertEqual(Notification.objects.filter(project=self.project, alert_type="cost").count(), 1)

    def test_notification_list_and_mark_read(self):
        notification = Notification.objects.create(
            project=self.project,
            recipient=self.user,
            alert_type="general",
            message="Mensaje de prueba",
        )
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mensaje de prueba")

        response = self.client.get(reverse("notification_mark_read", args=[notification.pk]))
        self.assertEqual(response.status_code, 302)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)
