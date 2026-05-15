from __future__ import annotations

import csv
import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Notification, Project

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReportFilters:
    project_status: str = ""
    activity_status: str = ""
    owner_id: str = ""
    date_from: str = ""
    date_to: str = ""
    export_format: str = "html"
    include_cost: bool = True
    include_schedule: bool = True
    include_risks: bool = True


def parse_report_filters(params) -> ReportFilters:
    return ReportFilters(
        project_status=params.get("project_status", "").strip(),
        activity_status=params.get("activity_status", "").strip(),
        owner_id=params.get("owner_id", "").strip(),
        date_from=params.get("date_from", "").strip(),
        date_to=params.get("date_to", "").strip(),
        export_format=params.get("export_format", "html").strip() or "html",
        include_cost=params.get("include_cost", "1") not in {"0", "false", "False"},
        include_schedule=params.get("include_schedule", "1") not in {"0", "false", "False"},
        include_risks=params.get("include_risks", "1") not in {"0", "false", "False"},
    )


def create_project_with_acta(*, form, acta_form, user):
    with transaction.atomic():
        project = form.save(commit=False)
        project.created_by = user
        project.status = "planning"
        project.save()

        acta = acta_form.save(commit=False)
        acta.proyecto = project
        acta.save()
        return project


def transition_project_approval(project: Project, action: str) -> tuple[str, str]:
    previous_status = project.status
    if action == "approve":
        project.status = "in_progress"
        project.save(update_fields=["status", "updated_at"])
        if previous_status == "modified":
            return "in_progress", "Cambios en proyecto aprobados."
        return "in_progress", "Proyecto aprobado."
    if action == "reject":
        project.status = "on_hold"
        project.save(update_fields=["status", "updated_at"])
        if previous_status == "modified":
            return "on_hold", "Cambios en proyecto rechazados."
        return "on_hold", "Proyecto rechazado."
    raise ValueError("Unsupported project approval action")


def set_project_modified_if_needed(project: Project, acting_user) -> None:
    from .permissions import is_jefe_departamental

    if not is_jefe_departamental(acting_user):
        project.status = "modified"
        project.save(update_fields=["status", "updated_at"])


def create_notification(*, project, alert_type: str, message: str, recipient=None) -> Notification:
    return Notification.objects.create(
        project=project,
        alert_type=alert_type,
        message=message,
        recipient=recipient or project.created_by,
    )


def deliver_notification(notification: Notification) -> bool:
    recipient = notification.recipient or notification.project.created_by
    if not recipient or not recipient.email:
        logger.info("Skipping notification delivery without recipient email", extra={"notification_id": notification.id})
        return False

    subject = f"Alerta de Proyecto: {notification.get_alert_type_display()}"
    try:
        send_mail(
            subject,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Notification delivery failed", extra={"notification_id": notification.id})
        return False

    notification.sent = True
    notification.save(update_fields=["sent", "updated_at"])
    return True


def send_automated_project_report(project: Project) -> bool:
    if not project.created_by.email:
        return False

    activities = project.activity_set.all()
    completed = activities.filter(status="completed").count()
    total = activities.count()
    progress = (completed / total * 100) if total > 0 else 0

    context = {
        "project": project,
        "progress": progress,
        "completed": completed,
        "total": total,
    }
    html_message = render_to_string("reports/email_report.html", context)
    send_mail(
        f"Informe Automático del Proyecto: {project.name}",
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        [project.created_by.email],
        html_message=html_message,
        fail_silently=False,
    )
    return True


def export_project_csv(project: Project, activities) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{project.name}_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Activity", "Status", "Cost", "Start Date", "End Date"])
    for activity in activities:
        writer.writerow([activity.name, activity.status, activity.cost, activity.start_date, activity.end_date])
    return response


# ── Cortes del proyecto (períodos de revisión) ────────────────────────────

def generate_project_cuts(project, interval_days: int = 90):
    """
    Genera (o regenera) los cortes de un proyecto dividiendo su duración
    en períodos de 'interval_days' días.

    1. Elimina los cortes existentes.
    2. Divide el rango [start_date, end_date] en segmentos iguales.
    3. Crea un ProjectCut por segmento.

    Retorna la lista de ProjectCut creados.
    """
    from datetime import timedelta
    from .models import ProjectCut

    project.cuts.all().delete()

    start = project.start_date
    end = project.end_date
    if not start or not end or start > end:
        return []

    delta = timedelta(days=interval_days)
    cuts = []
    current_start = start
    period_num = 1

    while current_start <= end:
        current_end = min(current_start + delta - timedelta(days=1), end)

        if interval_days >= 80:
            name = f"Trimestre {period_num}"
        elif interval_days >= 25:
            name = f"Mes {period_num}"
        else:
            name = f"Periodo {period_num}"

        cuts.append(ProjectCut(
            project=project,
            name=name,
            start_date=current_start,
            end_date=current_end,
            sort_order=period_num,
        ))
        current_start = current_end + timedelta(days=1)
        period_num += 1

    ProjectCut.objects.bulk_create(cuts)
    return list(project.cuts.all().order_by('sort_order'))
