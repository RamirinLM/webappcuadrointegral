import logging
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ActivityAssignmentForm,
    ActivityForm,
    ActaConstitucionForm,
    MilestoneForm,
    ProjectForm,
    SeguimientoForm,
    UserForm,
)
from .models import (
    Activity,
    ChangeRequest,
    Milestone,
    Notification,
    Project,
    ProjectCut,
    Seguimiento,
    ActaConstitucion,
)
from .permissions import can_edit_project, can_view_project, get_user_projects, is_jefe_departamental
from .services import (
    create_project_with_acta,
    generate_project_cuts,
    set_project_modified_if_needed,
    transition_project_approval,
)

logger = logging.getLogger(__name__)


def jefe_departamental_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_jefe_departamental(request.user):
            messages.error(request, "Acceso denegado. Solo el Jefe Departamental tiene permisos para esta acciÃ³n.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def render_schema_mismatch(request, *, status=503):
    return render(
        request,
        "errors/schema_mismatch.html",
        {
            "error_summary": "La base de datos no esta sincronizada con la version actual del sistema.",
            "requested_path": request.path,
        },
        status=status,
    )


@login_required
def dashboard(request):
    projects = get_user_projects(request.user)
    active_projects = projects.filter(status__in=["in_progress", "planning"])
    pending_tasks = Activity.objects.filter(project__in=projects, status="pending")
    latest_reports = Seguimiento.objects.filter(proyecto__in=projects).order_by("-fecha")[:5]
    user_role = request.user.userprofile.get_role_display() if hasattr(request.user, "userprofile") else "Sin rol"

    projects_with_status = [
        {
            "project": project,
            "traffic_light": project.get_traffic_light_status(),
            "progress": project.get_progress_percentage(),
            "budget_utilization": project.budget_utilization_percentage,
        }
        for project in projects
    ]

    return render(
        request,
        "projects/dashboard.html",
        {
            "projects": projects,
            "projects_with_status": projects_with_status,
            "active_projects": active_projects,
            "pending_tasks": pending_tasks,
            "latest_reports": latest_reports,
            "user_role": user_role,
            "is_jefe_departamental": is_jefe_departamental(request.user),
        },
    )


@login_required
def project_list(request):
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": get_user_projects(request.user),
            "is_jefe_departamental": is_jefe_departamental(request.user),
        },
    )


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_view_project(request.user, project):
        messages.error(request, "No tienes permisos para ver este proyecto.")
        return redirect("project_list")

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "activities": project.activity_set.all(),
            "milestones": project.milestone_set.all(),
            "total_activities_cost": project.total_activities_cost,
            "total_resources_cost": project.total_resources_cost,
            "total_cost": project.total_actual_cost,
            "budget_variance": project.budget_variance,
            "budget_utilization": project.budget_utilization_percentage,
            "traffic_light": project.get_traffic_light_status(),
            "progress": project.get_progress_percentage(),
            "can_edit": can_edit_project(request.user, project),
            "is_jefe_departamental": is_jefe_departamental(request.user),
        },
    )


@login_required
def project_create(request):
    if not hasattr(request.user, "userprofile"):
        messages.error(request, "No tienes permisos para crear proyectos.")
        return redirect("project_list")

    if request.method == "POST":
        form = ProjectForm(request.POST)
        acta_form = ActaConstitucionForm(request.POST)
        if form.is_valid() and acta_form.is_valid():
            project = create_project_with_acta(form=form, acta_form=acta_form, user=request.user)
            messages.success(request, "Proyecto y acta de constituciÃ³n creados exitosamente.")
            return redirect("project_detail", pk=project.pk)
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ProjectForm()
        acta_form = ActaConstitucionForm()

    return render(request, "projects/project_form.html", {"form": form, "acta_form": acta_form})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para editar este proyecto.")
        return redirect("project_detail", pk=project.pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            set_project_modified_if_needed(project, request.user)
            messages.success(request, "Proyecto actualizado exitosamente.")
            return redirect("project_detail", pk=project.pk)
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/project_form.html", {"form": form, "project": project})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para eliminar este proyecto.")
        return redirect("project_list")

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyecto eliminado exitosamente.")
        return redirect("project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})


@login_required
def activity_list(request):
    activities = Activity.objects.filter(project__in=get_user_projects(request.user)).select_related("project", "predecessor")
    return render(
        request,
        "projects/activity_list.html",
        {"activities": activities, "is_jefe_departamental": is_jefe_departamental(request.user)},
    )


@login_required
def activity_create(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            try:
                activity = form.save(commit=False)
                if not can_edit_project(request.user, activity.project):
                    messages.error(request, "No tienes permisos para crear actividades en este proyecto.")
                    return redirect("activity_list")
                activity.save()
                messages.success(request, "Actividad creada exitosamente.")
                return redirect("activity_list")
            except Exception as exc:
                messages.error(request, f"Error al crear la actividad: {exc}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ActivityForm()
    return render(request, "projects/activity_form.html", {"form": form})


@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if not can_edit_project(request.user, activity.project):
        messages.error(request, "No tienes permisos para editar esta actividad.")
        return redirect("activity_list")

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Actividad actualizada exitosamente.")
                return redirect("activity_list")
            except Exception as exc:
                messages.error(request, f"Error al actualizar: {exc}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ActivityForm(instance=activity)

    return render(request, "projects/activity_form.html", {"form": form, "activity": activity})


@login_required
def milestone_list(request):
    milestones = Milestone.objects.filter(project__in=get_user_projects(request.user))
    return render(
        request,
        "projects/milestone_list.html",
        {"milestones": milestones, "is_jefe_departamental": is_jefe_departamental(request.user)},
    )


@login_required
def milestone_create(request):
    if request.method == "POST":
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            if not can_edit_project(request.user, milestone.project):
                messages.error(request, "No tienes permisos para crear hitos en este proyecto.")
                return redirect("milestone_list")
            milestone.save()
            messages.success(request, "Hito creado exitosamente.")
            return redirect("milestone_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = MilestoneForm()
    return render(request, "projects/milestone_form.html", {"form": form})


@jefe_departamental_required
@login_required
def user_list(request):
    users = User.objects.all().select_related("userprofile")
    return render(request, "projects/user_list.html", {"users": users})


@jefe_departamental_required
@login_required
def user_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect("user_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = UserForm()
    return render(request, "projects/user_form.html", {"form": form})


@jefe_departamental_required
@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("user_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = UserForm(instance=user)
    return render(request, "projects/user_form.html", {"form": form})


@jefe_departamental_required
@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuario eliminado exitosamente.")
        return redirect("user_list")
    return render(request, "projects/user_confirm_delete.html", {"user": user})


@login_required
def seguimiento_list(request):
    proyectos = get_user_projects(request.user)
    seguimientos = Seguimiento.objects.filter(proyecto__in=proyectos).order_by("-fecha").select_related("proyecto")
    return render(
        request,
        "projects/seguimiento_list.html",
        {
            "proyectos": proyectos,
            "seguimientos": seguimientos,
            "is_jefe_departamental": is_jefe_departamental(request.user),
        },
    )


@login_required
def seguimiento_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para crear seguimientos en este proyecto.")
        return redirect("seguimiento_list")

    if request.method == "POST":
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.proyecto = project
            seguimiento.save()
            messages.success(request, "Seguimiento creado exitosamente.")
            return redirect("project_detail", pk=project.pk)
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = SeguimientoForm(initial={"proyecto": project})
    return render(request, "projects/seguimiento_form.html", {"form": form})


@login_required
def linea_base_seguimiento(request, project_id):
    """
    Vista de Linea Base: muestra el plan completo del proyecto y permite
    hacer un seguimiento masivo: ingresar fechas reales y costos reales
    por cada actividad, y crear un registro de Seguimiento con las
    metricas EVM calculadas.
    """
    from datetime import date
    from decimal import Decimal

    project = get_object_or_404(Project, pk=project_id)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para modificar este proyecto.")
        return redirect("project_detail", pk=project.pk)

    activities = project.activity_set.all().order_by("start_date", "name")

    if request.method == "POST":
        fecha_str = request.POST.get("fecha", "")
        observacion = request.POST.get("observacion", "")

        if not fecha_str:
            messages.error(request, "Debe seleccionar una fecha para el seguimiento.")
            return redirect("linea_base_seguimiento", project_id=project.pk)

        try:
            from datetime import date as dt_date
            fecha = dt_date.fromisoformat(fecha_str)
        except (ValueError, TypeError):
            messages.error(request, "Fecha invalida.")
            return redirect("linea_base_seguimiento", project_id=project.pk)

        # Actualizar datos reales por actividad
        errores = 0
        for activity in activities:
            a_start = request.POST.get(f"actual_start_{activity.id}", "").strip()
            a_end = request.POST.get(f"actual_end_{activity.id}", "").strip()
            a_cost = request.POST.get(f"actual_cost_{activity.id}", "").strip()

            changed = False
            if a_start:
                try:
                    activity.actual_start_date = date.fromisoformat(a_start)
                    changed = True
                except ValueError:
                    pass
            if a_end:
                try:
                    activity.actual_end_date = date.fromisoformat(a_end)
                    # Si tiene fecha real de fin, marcarla como completada
                    if activity.status in ("pending", "in_progress"):
                        activity.status = "completed"
                    changed = True
                except ValueError:
                    pass
            if a_cost:
                try:
                    activity.actual_cost = Decimal(a_cost)
                    changed = True
                except (ValueError, TypeError):
                    pass

            if changed:
                try:
                    activity.save()
                except Exception as e:
                    errores += 1
                    logger.warning("Error al guardar actividad %s: %s", activity.id, e)

        # Crear el registro de seguimiento
        seguimiento = Seguimiento(proyecto=project, fecha=fecha, observacion=observacion)
        seguimiento.save()  # calculate_metrics() se ejecuta automaticamente

        if errores:
            messages.warning(request, f"Seguimiento creado con {errores} error(es) al actualizar actividades.")
        else:
            messages.success(
                request,
                f"Seguimiento del {fecha.strftime('%d/%m/%Y')} creado. "
                f"PV: ${seguimiento.pv:.2f} | EV: ${seguimiento.ev:.2f} | AC: ${seguimiento.ac:.2f} | "
                f"SV: ${seguimiento.sv:.2f} | CV: ${seguimiento.cv:.2f}"
            )

        return redirect("linea_base_seguimiento", project_id=project.pk)

    # GET: mostrar linea base
    today = date.today()
    latest_seguimiento = Seguimiento.objects.filter(proyecto=project).order_by("-fecha").first()
    all_seguimientos = Seguimiento.objects.filter(proyecto=project).order_by("-fecha")
    completed_count = activities.filter(status="completed").count()
    in_progress_count = activities.filter(status="in_progress").count()

    context = {
        "project": project,
        "activities": activities,
        "today": today,
        "latest_seguimiento": latest_seguimiento,
        "all_seguimientos": all_seguimientos,
        "can_edit": can_edit_project(request.user, project),
        "completed_count": completed_count,
        "in_progress_count": in_progress_count,
    }
    return render(request, "projects/linea_base_seguimiento.html", context)


@login_required
def seguimiento_edit(request, pk):
    seguimiento = get_object_or_404(Seguimiento, pk=pk)
    if not can_edit_project(request.user, seguimiento.proyecto):
        messages.error(request, "No tienes permisos para editar este seguimiento.")
        return redirect("seguimiento_list")

    if request.method == "POST":
        form = SeguimientoForm(request.POST, instance=seguimiento)
        if form.is_valid():
            form.save()
            messages.success(request, "Seguimiento actualizado exitosamente.")
            return redirect("seguimiento_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = SeguimientoForm(instance=seguimiento)
    return render(request, "projects/seguimiento_form.html", {"form": form})


@login_required
def change_request_list(request):
    if is_jefe_departamental(request.user):
        change_requests = ChangeRequest.objects.all()
    else:
        change_requests = ChangeRequest.objects.filter(project__in=get_user_projects(request.user))
    return render(
        request,
        "projects/change_request_list.html",
        {"change_requests": change_requests, "is_jefe_departamental": is_jefe_departamental(request.user)},
    )


@login_required
def change_request_create(request):
    from .forms import ChangeRequestForm

    if request.method == "POST":
        form = ChangeRequestForm(request.user, request.POST)
        if form.is_valid():
            change_request = form.save(commit=False)
            change_request.requested_by = request.user
            change_request.save()
            messages.success(request, "Solicitud de cambio creada exitosamente.")
            return redirect("change_request_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ChangeRequestForm(user=request.user)
    return render(request, "projects/change_request_form.html", {"form": form})


@login_required
def change_request_approve(request, pk):
    if not is_jefe_departamental(request.user):
        messages.error(request, "No tienes permisos para aprobar cambios.")
        return redirect("change_request_list")
    change_request = get_object_or_404(ChangeRequest, pk=pk)
    change_request.status = "approved"
    change_request.approved_by = request.user
    change_request.save()
    messages.success(request, "Cambio aprobado.")
    return redirect("change_request_list")


@login_required
def change_request_reject(request, pk):
    if not is_jefe_departamental(request.user):
        messages.error(request, "No tienes permisos para rechazar cambios.")
        return redirect("change_request_list")
    change_request = get_object_or_404(ChangeRequest, pk=pk)
    change_request.status = "rejected"
    change_request.approved_by = request.user
    change_request.save()
    messages.success(request, "Cambio rechazado.")
    return redirect("change_request_list")


@login_required
def project_approve(request, pk):
    if not is_jefe_departamental(request.user):
        messages.error(request, "No tienes permisos para aprobar proyectos.")
        return redirect("project_list")
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        _, message = transition_project_approval(project, request.POST.get("action"))
        messages.success(request, message)
        return redirect("project_list")
    return render(request, "projects/project_approve.html", {"project": project})


@login_required
def acta_constitucion_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para crear acta de constituciÃ³n en este proyecto.")
        return redirect("project_detail", pk=project.pk)
    if hasattr(project, "actaconstitucion"):
        messages.warning(request, "El proyecto ya tiene un acta de constituciÃ³n.")
        return redirect("project_detail", pk=project.pk)

    if request.method == "POST":
        form = ActaConstitucionForm(request.POST)
        if form.is_valid():
            acta = form.save(commit=False)
            acta.proyecto = project
            acta.save()
            messages.success(request, "Acta de constituciÃ³n creada exitosamente.")
            return redirect("project_detail", pk=project.pk)
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ActaConstitucionForm(initial={"proyecto": project})
    return render(request, "projects/acta_constitucion_form.html", {"form": form, "project": project})


@login_required
def acta_constitucion_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not can_edit_project(request.user, project):
        messages.error(request, "No tienes permisos para editar el acta de este proyecto.")
        return redirect("project_detail", pk=project.pk)
    acta = get_object_or_404(ActaConstitucion, proyecto=project)
    if request.method == "POST":
        form = ActaConstitucionForm(request.POST, instance=acta)
        if form.is_valid():
            form.save()
            messages.success(request, "Acta de constituciÃ³n actualizada exitosamente.")
            return redirect("project_detail", pk=project.pk)
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ActaConstitucionForm(instance=acta)
    return render(request, "projects/acta_constitucion_form.html", {"form": form, "project": project})


@login_required
def project_financial_summary(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_view_project(request.user, project):
        messages.error(request, "No tienes permisos para ver este proyecto.")
        return redirect("dashboard")

    return render(
        request,
        "projects/financial_summary.html",
        {
            "project": project,
            "budget": project.budget,
            "activities_cost": project.total_activities_cost,
            "resources_cost": project.total_resources_cost,
            "total_cost": project.total_actual_cost,
            "variance": project.budget_variance,
            "utilization": project.budget_utilization_percentage,
            "activities": project.activity_set.all(),
            "traffic_light": project.get_traffic_light_status(),
        },
    )


@login_required
def activity_assign_user(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if not can_edit_project(request.user, activity.project):
        messages.error(request, "No tienes permisos para asignar usuarios en esta actividad.")
        return redirect("activity_list")

    if request.method == "POST":
        form = ActivityAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.activity = activity
            assignment.save()
            messages.success(request, f"Usuario asignado exitosamente a {activity.name}.")
            return redirect("activity_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ActivityAssignmentForm()

    return render(
        request,
        "projects/activity_assignment_form.html",
        {"form": form, "activity": activity, "existing_assignments": activity.assignments.all()},
    )


@jefe_departamental_required
@login_required
def milestone_edit(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk)
    if not can_edit_project(request.user, milestone.project):
        messages.error(request, "No tienes permisos para editar este hito.")
        return redirect("milestone_list")
    if request.method == "POST":
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, "Hito actualizado exitosamente.")
            return redirect("milestone_list")
        messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = MilestoneForm(instance=milestone)
    return render(request, "projects/milestone_form.html", {"form": form, "milestone": milestone})


@login_required
def notification_list(request):
    try:
        notifications = Notification.objects.filter(recipient=request.user).select_related("project").order_by("-created_at")
    except (OperationalError, ProgrammingError):
        return render_schema_mismatch(request)
    return render(request, "projects/notification_list.html", {"notifications": notifications})


@login_required
def notification_detail(request, pk):
    try:
        notification = get_object_or_404(Notification.objects.select_related("project"), pk=pk, recipient=request.user)
    except (OperationalError, ProgrammingError):
        return render_schema_mismatch(request)
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at", "updated_at"])
    return render(request, "projects/notification_detail.html", {"notification": notification})


@login_required
def notification_mark_read(request, pk):
    try:
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at", "updated_at"])
    except (OperationalError, ProgrammingError):
        return render_schema_mismatch(request)
    messages.success(request, "Notificacion marcada como leida.")
    return redirect("notification_list")


# ── Cortes del proyecto (períodos de revisión) ────────────────────────────

@login_required
def project_cuts(request, project_id):
    """
    Vista de cortes del proyecto: muestra la línea de tiempo dividida en
    períodos (trimestres) con métricas agregadas (planificado vs real).

    - GET: muestra los cortes existentes + formulario para generar/regenerar
    - POST: guarda nuevos parámetros de intervalo y regenera los cortes
    """
    project = get_object_or_404(Project, pk=project_id)
    if not can_view_project(request.user, project):
        messages.error(request, "No tienes permisos para ver este proyecto.")
        return redirect("project_list")

    interval = request.POST.get("interval", "90")

    if request.method == "POST" and "generate" in request.POST:
        try:
            interval_days = int(interval)
            if interval_days < 1:
                raise ValueError
        except (ValueError, TypeError):
            interval_days = 90
            interval = "90"

        generate_project_cuts(project, interval_days=interval_days)
        messages.success(
            request,
            f"Cortes generados cada {interval_days} días para '{project.name}'."
        )
        return redirect("project_cuts", project_id=project.pk)

    if request.method == "POST" and "delete_cut" in request.POST:
        cut_id = request.POST.get("cut_id")
        if cut_id:
            ProjectCut.objects.filter(pk=cut_id, project=project).delete()
            messages.success(request, "Corte eliminado.")
        return redirect("project_cuts", project_id=project.pk)

    if request.method == "POST" and "update_cut" in request.POST:
        cut_id = request.POST.get("cut_id")
        name = request.POST.get("cut_name", "").strip()
        start = request.POST.get("cut_start", "").strip()
        end = request.POST.get("cut_end", "").strip()
        if cut_id:
            cut = get_object_or_404(ProjectCut, pk=cut_id, project=project)
            if name:
                cut.name = name
            if start:
                from datetime import date
                try:
                    cut.start_date = date.fromisoformat(start)
                except ValueError:
                    pass
            if end:
                from datetime import date
                try:
                    cut.end_date = date.fromisoformat(end)
                except ValueError:
                    pass
            cut.save()
            messages.success(request, f"Corte '{cut.name}' actualizado.")
        return redirect("project_cuts", project_id=project.pk)

    # ── GET: mostrar cortes ──
    cuts = project.cuts.all().order_by("sort_order")

    # Totales acumulados del proyecto
    from decimal import Decimal
    total_planned_cost = Decimal("0")
    total_ev = Decimal("0")
    total_ac = Decimal("0")
    for cut in cuts:
        total_planned_cost += cut.planned_cost
        total_ev += cut.ev
        total_ac += cut.ac

    if total_planned_cost > 0:
        overall_spi = total_ev / total_planned_cost
    else:
        overall_spi = Decimal("0")
    if total_ac > 0:
        overall_cpi = total_ev / total_ac
    else:
        overall_cpi = Decimal("0")

    # Traducción a colores Bootstrap para el template
    STATUS_BOOTSTRAP = {
        "green": "success",
        "yellow": "warning",
        "red": "danger",
        "no_data": "secondary",
    }

    return render(
        request,
        "projects/project_cuts.html",
        {
            "project": project,
            "cuts": cuts,
            "interval": interval,
            "has_cuts": cuts.exists(),
            "total_planned_cost": total_planned_cost,
            "total_ev": total_ev,
            "total_ac": total_ac,
            "overall_spi": overall_spi,
            "overall_cpi": overall_cpi,
            "status_bootstrap": STATUS_BOOTSTRAP,
            "can_edit": can_edit_project(request.user, project),
        },
    )
