from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from projects.models import Project
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Send automated project reports to stakeholders'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        for project in projects:
            # Generate report data
            activities = project.activity_set.all()
            completed = activities.filter(status='completed').count()
            total = activities.count()
            progress = (completed / total * 100) if total > 0 else 0

            # Send email to project creator
            subject = f'Informe Automático del Proyecto: {project.name}'
            context = {
                'project': project,
                'progress': progress,
                'completed': completed,
                'total': total,
            }
            message = render_to_string('reports/email_report.html', context)
            send_mail(
                subject,
                message,
                'your-email@gmail.com',
                [project.created_by.email],
                html_message=message,
                fail_silently=True,
            )
            self.stdout.write(f'Report sent for project: {project.name}')