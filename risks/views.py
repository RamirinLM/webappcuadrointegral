from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.permissions import can_edit_project, can_view_project, get_user_projects
from .models import Risk
from .forms import RiskForm

@login_required
def risk_list(request):
    risks = Risk.objects.filter(project__in=get_user_projects(request.user)).select_related("project")
    return render(request, 'risks/risk_list.html', {'risks': risks})

@login_required
def risk_create(request):
    if request.method == 'POST':
        form = RiskForm(request.POST, user=request.user)
        if form.is_valid():
            risk = form.save(commit=False)
            if not can_edit_project(request.user, risk.project):
                messages.error(request, 'No tienes permisos para crear riesgos en este proyecto.')
                return redirect('risks:risk_list')
            risk.save()
            messages.success(request, 'Riesgo creado exitosamente.')
            return redirect('risks:risk_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = RiskForm(user=request.user)
    return render(request, 'risks/risk_form.html', {'form': form})

@login_required
def risk_edit(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    if not can_edit_project(request.user, risk.project):
        messages.error(request, 'No tienes permisos para editar este riesgo.')
        return redirect('risks:risk_list')
    if request.method == 'POST':
        form = RiskForm(request.POST, instance=risk, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Riesgo actualizado exitosamente.')
            return redirect('risks:risk_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = RiskForm(instance=risk, user=request.user)
    return render(request, 'risks/risk_form.html', {'form': form})

@login_required
def risk_delete(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    if not can_edit_project(request.user, risk.project):
        messages.error(request, 'No tienes permisos para eliminar este riesgo.')
        return redirect('risks:risk_list')
    if request.method == 'POST':
        risk.delete()
        messages.success(request, 'Riesgo eliminado exitosamente.')
        return redirect('risks:risk_list')
    return render(request, 'risks/risk_confirm_delete.html', {'risk': risk})
