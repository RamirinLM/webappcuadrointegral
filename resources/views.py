from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm

@login_required
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resources/resource_list.html', {'resources': resources})

@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm()
    return render(request, 'resources/resource_form.html', {'form': form})
