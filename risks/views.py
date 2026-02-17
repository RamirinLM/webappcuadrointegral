from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Risk
from .forms import RiskForm

@login_required
def risk_list(request):
    risks = Risk.objects.all()
    return render(request, 'risks/risk_list.html', {'risks': risks})

@login_required
def risk_create(request):
    if request.method == 'POST':
        form = RiskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk created successfully.')
            return redirect('risks:risk_list')
    else:
        form = RiskForm()
    return render(request, 'risks/risk_form.html', {'form': form})

@login_required
def risk_edit(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    if request.method == 'POST':
        form = RiskForm(request.POST, instance=risk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk updated successfully.')
            return redirect('risks:risk_list')
    else:
        form = RiskForm(instance=risk)
    return render(request, 'risks/risk_form.html', {'form': form})

@login_required
def risk_delete(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    if request.method == 'POST':
        risk.delete()
        messages.success(request, 'Risk deleted successfully.')
        return redirect('risks:risk_list')
    return render(request, 'risks/risk_confirm_delete.html', {'risk': risk})
