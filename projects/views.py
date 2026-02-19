from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from functools import wraps
from .models import Project, Activity, Milestone, Seguimiento, ChangeRequest, ActaConstitucion, ActivityAssignment
from .forms import ProjectForm, ActivityForm, MilestoneForm, UserForm, SeguimientoForm, ActaConstitucionForm, ActivityAssignmentForm

def jefe_departamental_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'jefe_departamental':
            messages.error(request, 'Acceso denegado. Solo el Jefe Departamental tiene permisos para esta acción.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    active_projects = projects.filter(status__in=['in_progress', 'planning'])
    pending_tasks = Activity.objects.filter(project__created_by=request.user, status='pending')
    latest_reports = Seguimiento.objects.filter(proyecto__created_by=request.user).order_by('-fecha')[:5]
    user_role = request.user.userprofile.get_role_display() if hasattr(request.user, 'userprofile') else 'Sin rol'
    
    # Add traffic light status and progress to each project
    projects_with_status = []
    for project in projects:
        projects_with_status.append({
            'project': project,
            'traffic_light': project.get_traffic_light_status(),
            'progress': project.get_progress_percentage(),
            'budget_utilization': project.budget_utilization_percentage,
        })
    
    return render(request, 'projects/dashboard.html', {
        'projects': projects,
        'projects_with_status': projects_with_status,
        'active_projects': active_projects,
        'pending_tasks': pending_tasks,
        'latest_reports': latest_reports,
        'user_role': user_role
    })

@login_required
def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    activities = project.activity_set.all()
    milestones = project.milestone_set.all()
    
    # Calculate financial summary
    total_activities_cost = project.total_activities_cost
    total_resources_cost = project.total_resources_cost
    total_cost = project.total_actual_cost
    budget_variance = project.budget_variance
    budget_utilization = project.budget_utilization_percentage
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'activities': activities,
        'milestones': milestones,
        'total_activities_cost': total_activities_cost,
        'total_resources_cost': total_resources_cost,
        'total_cost': total_cost,
        'budget_variance': budget_variance,
        'budget_utilization': budget_utilization,
        'traffic_light': project.get_traffic_light_status(),
        'progress': project.get_progress_percentage(),
    })

@login_required
def project_create(request):
    if request.user.userprofile.role not in ['tecnico_proyectos', 'gestor_proyectos', 'jefe_departamental']:
        messages.error(request, 'No tienes permisos para crear proyectos.')
        return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        acta_form = ActaConstitucionForm(request.POST)
        if form.is_valid() and acta_form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.status = 'planning'  # or 'pending'
            project.save()
            acta = acta_form.save(commit=False)
            acta.proyecto = project
            acta.save()
            messages.success(request, 'Proyecto y acta de constitución creados exitosamente.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
        acta_form = ActaConstitucionForm()
    return render(request, 'projects/project_form.html', {'form': form, 'acta_form': acta_form})

@jefe_departamental_required
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            project.status = 'modified'
            project.save()
            messages.success(request, 'Proyecto actualizado. Pendiente de aprobación.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@jefe_departamental_required
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
def activity_list(request):
    activities = Activity.objects.filter(project__created_by=request.user).select_related('project', 'predecessor')
    return render(request, 'projects/activity_list.html', {'activities': activities})

@jefe_departamental_required
@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            try:
                activity = form.save()
                messages.success(request, 'Actividad creada exitosamente.')
                return redirect('activity_list')
            except Exception as e:
                messages.error(request, f'Error al crear la actividad: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ActivityForm()
    return render(request, 'projects/activity_form.html', {'form': form})

@jefe_departamental_required
@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk, project__created_by=request.user)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Actividad actualizada exitosamente.')
                return redirect('activity_list')
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'projects/activity_form.html', {'form': form, 'activity': activity})

@login_required
def milestone_list(request):
    milestones = Milestone.objects.filter(project__created_by=request.user)
    return render(request, 'projects/milestone_list.html', {'milestones': milestones})

@jefe_departamental_required
@login_required
def milestone_create(request):
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hito creado exitosamente.')
            return redirect('milestone_list')
    else:
        form = MilestoneForm()
    return render(request, 'projects/milestone_form.html', {'form': form})

@jefe_departamental_required
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'projects/user_list.html', {'users': users})

@jefe_departamental_required
@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'projects/user_form.html', {'form': form})

@jefe_departamental_required
@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'projects/user_form.html', {'form': form})

@jefe_departamental_required
@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('user_list')
    return render(request, 'projects/user_confirm_delete.html', {'user': user})

@login_required
def seguimiento_list(request):
    seguimientos = Seguimiento.objects.filter(proyecto__created_by=request.user)
    return render(request, 'projects/seguimiento_list.html', {'seguimientos': seguimientos})

@jefe_departamental_required
@login_required
def seguimiento_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, created_by=request.user)
    if request.method == 'POST':
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seguimiento creado exitosamente.')
            return redirect('seguimiento_list')
    else:
        form = SeguimientoForm(initial={'proyecto': project})
    return render(request, 'projects/seguimiento_form.html', {'form': form})

@jefe_departamental_required
@login_required
def seguimiento_edit(request, pk):
    seguimiento = get_object_or_404(Seguimiento, pk=pk, proyecto__created_by=request.user)
    if request.method == 'POST':
        form = SeguimientoForm(request.POST, instance=seguimiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seguimiento actualizado exitosamente.')
            return redirect('seguimiento_list')
    else:
        form = SeguimientoForm(instance=seguimiento)
    return render(request, 'projects/seguimiento_form.html', {'form': form})

@login_required
def change_request_list(request):
    if request.user.userprofile.role == 'jefe_departamental':
        change_requests = ChangeRequest.objects.all()
    else:
        change_requests = ChangeRequest.objects.filter(requested_by=request.user)
    return render(request, 'projects/change_request_list.html', {'change_requests': change_requests})

@login_required
def change_request_create(request):
    if request.method == 'POST':
        # Assuming a form, but for simplicity, use model form
        pass  # Implement form
    return render(request, 'projects/change_request_form.html')

@login_required
def change_request_approve(request, pk):
    if request.user.userprofile.role != 'jefe_departamental':
        messages.error(request, 'No tienes permisos para aprobar cambios.')
        return redirect('change_request_list')
    change_request = get_object_or_404(ChangeRequest, pk=pk)
    change_request.status = 'approved'
    change_request.approved_by = request.user
    change_request.save()
    messages.success(request, 'Cambio aprobado.')
    return redirect('change_request_list')

@login_required
def project_approve(request, pk):
    if request.user.userprofile.role != 'jefe_departamental':
        messages.error(request, 'No tienes permisos para aprobar proyectos.')
        return redirect('project_list')
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            if project.status == 'modified':
                project.status = 'in_progress'
                messages.success(request, 'Cambios en proyecto aprobados.')
            else:
                project.status = 'in_progress'
                messages.success(request, 'Proyecto aprobado.')
        elif action == 'reject':
            if project.status == 'modified':
                project.status = 'on_hold'
                messages.success(request, 'Cambios en proyecto rechazados.')
            else:
                project.status = 'on_hold'
                messages.success(request, 'Proyecto rechazado.')
        project.save()
        return redirect('project_list')
    return render(request, 'projects/project_approve.html', {'project': project})

@login_required
def acta_constitucion_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id, created_by=request.user)
    if hasattr(project, 'actaconstitucion'):
        messages.warning(request, 'El proyecto ya tiene un acta de constitución.')
        return redirect('project_detail', pk=project.pk)
    if request.method == 'POST':
        form = ActaConstitucionForm(request.POST)
        if form.is_valid():
            acta = form.save(commit=False)
            acta.proyecto = project
            acta.save()
            messages.success(request, 'Acta de constitución creada exitosamente.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ActaConstitucionForm(initial={'proyecto': project})
    return render(request, 'projects/acta_constitucion_form.html', {'form': form, 'project': project})

@login_required
def acta_constitucion_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id, created_by=request.user)
    acta = get_object_or_404(ActaConstitucion, proyecto=project)
    if request.method == 'POST':
        form = ActaConstitucionForm(request.POST, instance=acta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta de constitución actualizada exitosamente.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ActaConstitucionForm(instance=acta)
    return render(request, 'projects/acta_constitucion_form.html', {'form': form, 'project': project})

@login_required
def project_financial_summary(request, pk):
    """Vista de resumen financiero del proyecto"""
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    # Get activities with their resource costs
    activities = project.activity_set.all()
    
    context = {
        'project': project,
        'budget': project.budget,
        'activities_cost': project.total_activities_cost,
        'resources_cost': project.total_resources_cost,
        'total_cost': project.total_actual_cost,
        'variance': project.budget_variance,
        'utilization': project.budget_utilization_percentage,
        'activities': activities,
        'traffic_light': project.get_traffic_light_status(),
    }
    return render(request, 'projects/financial_summary.html', context)

@login_required
def activity_assign_user(request, pk):
    """Asignar múltiples usuarios a una actividad"""
    activity = get_object_or_404(Activity, pk=pk, project__created_by=request.user)
    
    if request.method == 'POST':
        form = ActivityAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.activity = activity
            assignment.save()
            messages.success(request, f'Usuario asignado exitosamente a {activity.name}.')
            return redirect('activity_list')
    else:
        form = ActivityAssignmentForm()
    
    existing_assignments = activity.assignments.all()
    
    return render(request, 'projects/activity_assignment_form.html', {
        'form': form,
        'activity': activity,
        'existing_assignments': existing_assignments
    })

@jefe_departamental_required
@login_required
def milestone_edit(request, pk):
    """Editar hito existente"""
    milestone = get_object_or_404(Milestone, pk=pk, project__created_by=request.user)
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hito actualizado exitosamente.')
            return redirect('milestone_list')
    else:
        form = MilestoneForm(instance=milestone)
    return render(request, 'projects/milestone_form.html', {'form': form, 'milestone': milestone})

