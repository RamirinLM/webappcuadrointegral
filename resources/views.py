from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.permissions import can_edit_project, get_user_projects, is_jefe_departamental
from .models import Resource
from .forms import ResourceForm

@login_required
def resource_list(request):
    resources = Resource.objects.filter(activity__project__in=get_user_projects(request.user)).select_related("activity", "activity__project")
    return render(request, 'resources/resource_list.html', {'resources': resources})

@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, user=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            if resource.activity is None:
                form.add_error('activity', 'Debe seleccionar una actividad válida para crear el recurso.')
                messages.error(request, 'Por favor corrija los errores en el formulario.')
                return render(request, 'resources/resource_form.html', {'form': form})
            if not can_edit_project(request.user, resource.activity.project):
                messages.error(request, 'No tienes permisos para crear recursos en este proyecto.')
                return redirect('resources:resource_list')
            resource.save()
            messages.success(request, 'Recurso creado exitosamente.')
            return redirect('resources:resource_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ResourceForm(user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form})

@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.activity is None:
        messages.error(request, 'El recurso no tiene una actividad asociada válida.')
        return redirect('resources:resource_list')
    if not can_edit_project(request.user, resource.activity.project):
        messages.error(request, 'No tienes permisos para editar este recurso.')
        return redirect('resources:resource_list')
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurso actualizado exitosamente.')
            return redirect('resources:resource_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ResourceForm(instance=resource, user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form})

@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.activity is None:
        messages.error(request, 'El recurso no tiene una actividad asociada válida.')
        return redirect('resources:resource_list')
    if not can_edit_project(request.user, resource.activity.project):
        messages.error(request, 'No tienes permisos para eliminar este recurso.')
        return redirect('resources:resource_list')
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Recurso eliminado exitosamente.')
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})
