from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Project, Activity, Milestone, Seguimiento
from .forms import ProjectForm, ActivityForm, MilestoneForm, UserForm, SeguimientoForm

@login_required
def dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'projects/dashboard.html', {'projects': projects})

@login_required
def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    activities = project.activity_set.all()
    milestones = project.milestone_set.all()
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'activities': activities,
        'milestones': milestones
    })

@login_required
def project_create(request):
    if request.user.userprofile.role not in ['tecnico_proyectos', 'gestor_proyectos']:
        messages.error(request, 'No tienes permisos para crear proyectos.')
        return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Proyecto creado exitosamente.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

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
    activities = Activity.objects.filter(project__created_by=request.user)
    return render(request, 'projects/activity_list.html', {'activities': activities})

@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity created successfully.')
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'projects/activity_form.html', {'form': form})

@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk, project__created_by=request.user)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully.')
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'projects/activity_form.html', {'form': form})

@login_required
def milestone_list(request):
    milestones = Milestone.objects.filter(project__created_by=request.user)
    return render(request, 'projects/milestone_list.html', {'milestones': milestones})

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

@login_required
def user_list(request):
    if request.user.userprofile.role != 'gestor_proyectos':
        messages.error(request, 'No tienes permisos para gestionar usuarios.')
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'projects/user_list.html', {'users': users})

@login_required
def user_create(request):
    if request.user.userprofile.role != 'gestor_proyectos':
        messages.error(request, 'No tienes permisos para crear usuarios.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'projects/user_form.html', {'form': form})

@login_required
def user_edit(request, pk):
    if request.user.userprofile.role != 'gestor_proyectos':
        messages.error(request, 'No tienes permisos para editar usuarios.')
        return redirect('dashboard')
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

@login_required
def user_delete(request, pk):
    if request.user.userprofile.role != 'gestor_proyectos':
        messages.error(request, 'No tienes permisos para eliminar usuarios.')
        return redirect('dashboard')
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

@login_required
def seguimiento_create(request):
    if request.method == 'POST':
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seguimiento creado exitosamente.')
            return redirect('seguimiento_list')
    else:
        form = SeguimientoForm()
    return render(request, 'projects/seguimiento_form.html', {'form': form})

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

