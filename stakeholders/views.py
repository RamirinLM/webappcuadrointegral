from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Stakeholder
from .forms import StakeholderForm

@login_required
def stakeholder_list(request):
    stakeholders = Stakeholder.objects.all()
    return render(request, 'stakeholders/stakeholder_list.html', {'stakeholders': stakeholders})

@login_required
def stakeholder_create(request):
    if request.method == 'POST':
        form = StakeholderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stakeholder created successfully.')
            return redirect('stakeholders:stakeholder_list')
    else:
        form = StakeholderForm()
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form})

@login_required
def stakeholder_edit(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk)
    if request.method == 'POST':
        form = StakeholderForm(request.POST, instance=stakeholder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stakeholder updated successfully.')
            return redirect('stakeholders:stakeholder_list')
    else:
        form = StakeholderForm(instance=stakeholder)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form})
