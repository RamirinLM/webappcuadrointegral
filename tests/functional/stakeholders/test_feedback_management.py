from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project
from stakeholders.models import Feedback, Stakeholder


class FeedbackManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="manager", password="testpass")
        self.user.userprofile.role = "gestor_proyectos"
        self.user.userprofile.save()
        self.client.login(username="manager", password="testpass")
        self.project = Project.objects.create(
            name="Proyecto Feedback",
            description="Proyecto con feedback",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            created_by=self.user,
        )
        self.stakeholder = Stakeholder.objects.create(
            name="Interesado Clave",
            email="stakeholder@example.com",
            role="client",
            interest_level="high",
            power_level="high",
        )
        self.stakeholder.projects.add(self.project)

    def test_feedback_creation_success(self):
        response = self.client.post(
            reverse("stakeholders:feedback_create"),
            {
                "stakeholder": self.stakeholder.pk,
                "project": self.project.pk,
                "rating": 5,
                "comments": "Excelente avance",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Feedback.objects.filter(project=self.project, stakeholder=self.stakeholder).exists())

    def test_feedback_list_view(self):
        Feedback.objects.create(
            stakeholder=self.stakeholder,
            project=self.project,
            rating=4,
            comments="Buen trabajo",
        )
        response = self.client.get(reverse("stakeholders:feedback_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interesado Clave")
        self.assertContains(response, "Buen trabajo")

