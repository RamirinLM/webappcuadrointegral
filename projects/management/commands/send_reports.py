from django.core.management.base import BaseCommand

from projects.models import Project
from projects.services import send_automated_project_report


class Command(BaseCommand):
    help = "Send automated project reports to stakeholders"

    def handle(self, *args, **options):
        for project in Project.objects.all():
            if send_automated_project_report(project):
                self.stdout.write(f"Report sent for project: {project.name}")
            else:
                self.stdout.write(f"Skipped report for project without recipient email: {project.name}")
