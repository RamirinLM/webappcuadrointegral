from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.permissions import can_view_project, can_edit_project, get_user_projects, is_jefe_departamental
from .models import Stakeholder, Feedback
from .forms import FeedbackForm, StakeholderForm

@login_required
def stakeholder_list(request):
    projects = get_user_projects(request.user)
    stakeholders = Stakeholder.objects.filter(projects__in=projects).distinct()
    return render(request, 'stakeholders/stakeholder_list.html', {'stakeholders': stakeholders})

@login_required
def stakeholder_create(request):
    if request.method == 'POST':
        form = StakeholderForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interesado creado exitosamente.')
            return redirect('stakeholders:stakeholder_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = StakeholderForm(user=request.user)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form})

@login_required
def stakeholder_edit(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk)
    if not stakeholder.projects.filter(pk__in=get_user_projects(request.user).values_list("pk", flat=True)).exists():
        messages.error(request, 'No tienes permisos para editar este interesado.')
        return redirect('stakeholders:stakeholder_list')
    if request.method == 'POST':
        form = StakeholderForm(request.POST, instance=stakeholder, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interesado actualizado exitosamente.')
            return redirect('stakeholders:stakeholder_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = StakeholderForm(instance=stakeholder, user=request.user)
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form})

@login_required
def stakeholder_delete(request, pk):
    stakeholder = get_object_or_404(Stakeholder, pk=pk)
    if not stakeholder.projects.filter(pk__in=get_user_projects(request.user).values_list("pk", flat=True)).exists():
        messages.error(request, 'No tienes permisos para eliminar este interesado.')
        return redirect('stakeholders:stakeholder_list')
    if request.method == 'POST':
        stakeholder.delete()
        messages.success(request, 'Interesado eliminado exitosamente.')
        return redirect('stakeholders:stakeholder_list')
    return render(request, 'stakeholders/stakeholder_confirm_delete.html', {'stakeholder': stakeholder})

@login_required
def feedback_list(request):
    projects = get_user_projects(request.user)
    feedbacks = Feedback.objects.filter(project__in=projects).select_related("project", "stakeholder")
    return render(request, 'stakeholders/feedback_list.html', {'feedbacks': feedbacks})

@login_required
def feedback_create(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            feedback = form.save(commit=False)
            if not can_edit_project(request.user, feedback.project):
                messages.error(request, 'No tienes permisos para registrar feedback en este proyecto.')
                return redirect('stakeholders:feedback_list')
            feedback.save()
            messages.success(request, 'Retroalimentacion registrada exitosamente.')
            return redirect('stakeholders:feedback_list')
        messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = FeedbackForm(user=request.user)
    return render(request, 'stakeholders/feedback_form.html', {'form': form, 'is_jefe_departamental': is_jefe_departamental(request.user)})


@login_required
def feedback_edit(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if not can_edit_project(request.user, feedback.project):
        messages.error(request, 'No tienes permisos para editar esta retroalimentacion.')
        return redirect('stakeholders:feedback_list')
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Retroalimentacion actualizada exitosamente.')
            return redirect('stakeholders:feedback_list')
        messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = FeedbackForm(instance=feedback, user=request.user)
    return render(request, 'stakeholders/feedback_form.html', {'form': form, 'feedback': feedback})


@login_required
def feedback_delete(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if not can_edit_project(request.user, feedback.project):
        messages.error(request, 'No tienes permisos para eliminar esta retroalimentacion.')
        return redirect('stakeholders:feedback_list')
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Retroalimentacion eliminada exitosamente.')
        return redirect('stakeholders:feedback_list')
    return render(request, 'stakeholders/feedback_confirm_delete.html', {'feedback': feedback})
