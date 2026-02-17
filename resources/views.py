from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm

@login_required
def resource_list(request):
    resources = Resource.objects.filter(activity__project__created_by=request.user)
    return render(request, 'resources/resource_list.html', {'resources': resources})

@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form})

@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk, activity__project__created_by=request.user)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(instance=resource, user=request.user)
    return render(request, 'resources/resource_form.html', {'form': form})

@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, activity__project__created_by=request.user)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully.')
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})
