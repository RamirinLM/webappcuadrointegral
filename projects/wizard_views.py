"""
Vistas del Asistente para Creación de Proyectos
Implementa un wizard de 7 pasos para crear proyectos completos.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
import json
from datetime import datetime, date

from .models import (
    Project, ActaConstitucion, Alcance, Activity, Milestone,
    Comunicacion, ActivityAssignment
)
from .forms import ProjectForm, ActaConstitucionForm, ActivityForm, MilestoneForm
from .wizard_forms import (
    WizardProjectForm, WizardActaForm, WizardAlcanceForm,
    WizardStakeholderForm, WizardRiskForm, WizardCommunicationForm,
    WizardActivityForm, WizardResourceForm, WizardMilestoneForm
)
from stakeholders.models import Stakeholder
from risks.models import Risk
from resources.models import Resource


# Número total de pasos del wizard
TOTAL_STEPS = 7

# Nombres de los pasos para mostrar en la UI
STEP_NAMES = [
    'Datos del Proyecto',
    'Acta de Constitución',
    'Interesados',
    'Alcance Detallado',
    'Riesgos y Comunicación',
    'Actividades y Recursos',
    'Hitos'
]


def serialize_form_data(data):
    """Convierte datos del formulario a formato JSON serializable."""
    if isinstance(data, dict):
        return {k: serialize_form_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_form_data(item) for item in data]
    elif hasattr(data, 'isoformat'):  # date, datetime
        return data.isoformat()
    elif hasattr(data, '__str__'):
        return str(data)
    return data


def get_wizard_data(request):
    """Obtiene los datos del wizard almacenados en la sesión."""
    return request.session.get('project_wizard', {
        'step': 1,
        'project_id': None,
        'project_data': {},
        'acta_data': {},
        'stakeholder_ids': [],
        'new_stakeholders': [],
        'alcance_data': {},
        'risks': [],
        'communications': [],
        'activities': [],
        'milestones': [],
    })


def save_wizard_data(request, data):
    """Guarda los datos del wizard en la sesión."""
    # Asegurar que los datos sean serializables
    serialized_data = serialize_form_data(data)
    request.session['project_wizard'] = serialized_data
    request.session.modified = True


def clear_wizard_data(request):
    """Limpia los datos del wizard de la sesión."""
    if 'project_wizard' in request.session:
        del request.session['project_wizard']
    request.session.modified = True


@login_required
def project_wizard(request):
    """
    Vista principal del wizard. Redirige al paso actual.
    """
    data = get_wizard_data(request)
    
    # Si no hay datos, iniciar en paso 1
    if not data.get('step'):
        # Limpiar datos anteriores para empezar nuevo proyecto
        clear_wizard_data(request)
        data = {'step': 1}
        save_wizard_data(request, data)
    
    return redirect('wizard_step', step=data['step'])


@login_required
def wizard_step(request, step):
    """
    Maneja cada paso del wizard.
    """
    data = get_wizard_data(request)
    step = int(step)
    
    # Validar que el paso esté en rango
    if step < 1 or step > TOTAL_STEPS:
        messages.error(request, 'Paso inválido.')
        return redirect('project_wizard')
    
    # Verificar si se puede acceder a este paso
    # (debe haber completado los pasos anteriores)
    if step > 1 and not data.get('project_id') and step > 2:
        messages.warning(request, 'Debe completar los pasos anteriores primero.')
        return redirect('wizard_step', step=1)
    
    context = {
        'step': step,
        'total_steps': TOTAL_STEPS,
        'step_names': STEP_NAMES,
        'progress_percentage': round((step / TOTAL_STEPS) * 100),
        'edit_mode': data.get('edit_mode', False),
    }
    
    # Manejar cada paso
    if request.method == 'POST':
        return handle_step_post(request, step, data, context)
    else:
        return handle_step_get(request, step, data, context)


def handle_step_get(request, step, data, context):
    """Maneja las solicitudes GET para cada paso."""
    
    if step == 1:
        context['form'] = WizardProjectForm(initial=data.get('project_data', {}))
        context['title'] = 'Datos del Proyecto'
        context['description'] = 'Ingrese la información básica del proyecto.'
        
    elif step == 2:
        context['form'] = WizardActaForm(initial=data.get('acta_data', {}))
        context['title'] = 'Acta de Constitución'
        context['description'] = 'Complete el acta de constitución del proyecto.'
        
    elif step == 3:
        context['stakeholders'] = Stakeholder.objects.all()
        context['selected_ids'] = data.get('stakeholder_ids', [])
        context['new_stakeholders'] = data.get('new_stakeholders', [])
        context['stakeholder_form'] = WizardStakeholderForm()
        context['title'] = 'Interesados (Stakeholders)'
        context['description'] = 'Seleccione o agregue los interesados del proyecto.'
        
    elif step == 4:
        context['form'] = WizardAlcanceForm(initial=data.get('alcance_data', {}))
        context['title'] = 'Alcance Detallado'
        context['description'] = 'Defina el alcance técnico del proyecto.'
        
    elif step == 5:
        context['risks'] = data.get('risks', [])
        context['communications'] = data.get('communications', [])
        context['risk_form'] = WizardRiskForm()
        context['communication_form'] = WizardCommunicationForm()
        context['title'] = 'Riesgos y Plan de Comunicación'
        context['description'] = 'Identifique riesgos y defina el plan de comunicación.'
        
    elif step == 6:
        project_id = data.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                # Asegurar que activities esté en el contexto - obtener de la sesión
                session_activities = data.get('activities', [])
                context['activities'] = session_activities
                context['activity_form'] = WizardActivityForm(project_id=project_id)
                context['resource_form'] = WizardResourceForm()
                context['existing_activities'] = Activity.objects.filter(project_id=project_id)
                context['project_start_date'] = project.start_date.isoformat() if project.start_date else ''
                context['project_end_date'] = project.end_date.isoformat() if project.end_date else ''
            except Project.DoesNotExist:
                messages.error(request, 'El proyecto ya no existe. Por favor cree uno nuevo.')
                clear_wizard_data(request)
                return redirect('project_wizard')
        context['title'] = 'Actividades y Recursos'
        context['description'] = 'Defina las actividades y recursos del proyecto.'
        
    elif step == 7:
        project_id = data.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                context['milestones'] = data.get('milestones', [])
                context['activities'] = data.get('activities', [])
                context['form'] = WizardMilestoneForm(project_id=project_id)
                context['existing_activities'] = Activity.objects.filter(project_id=project_id)
                context['existing_milestones'] = Milestone.objects.filter(project_id=project_id)
                context['project_start_date'] = project.start_date.isoformat() if project.start_date else ''
                context['project_end_date'] = project.end_date.isoformat() if project.end_date else ''
            except Project.DoesNotExist:
                # El proyecto fue eliminado o no existe
                messages.error(request, 'El proyecto ya no existe. Por favor cree uno nuevo.')
                clear_wizard_data(request)
                return redirect('project_wizard')
        context['title'] = 'Hitos'
        context['description'] = 'Defina los hitos del proyecto.'
    
    return render(request, 'projects/project_wizard.html', context)


def handle_step_post(request, step, data, context):
    """Maneja las solicitudes POST para cada paso."""
    
    if step == 1:
        form = WizardProjectForm(request.POST)
        if form.is_valid():
            data['project_data'] = form.cleaned_data
            data['step'] = 2
            save_wizard_data(request, data)
            return redirect('wizard_step', step=2)
        context['form'] = form
        
    elif step == 2:
        form = WizardActaForm(request.POST)
        if form.is_valid():
            data['acta_data'] = form.cleaned_data
            
            # Crear o actualizar el proyecto y el acta en la base de datos
            try:
                with transaction.atomic():
                    edit_mode = data.get('edit_mode', False)
                    
                    if edit_mode and data.get('project_id'):
                        # Modo edición: actualizar proyecto existente
                        project = Project.objects.get(id=data['project_id'])
                        project.name = data['project_data']['name']
                        project.description = data['project_data']['description']
                        project.start_date = data['project_data']['start_date']
                        project.end_date = data['project_data']['end_date']
                        project.budget = data['project_data'].get('budget')
                        project.save()
                        
                        # Actualizar acta de constitución
                        if hasattr(project, 'actaconstitucion'):
                            acta = project.actaconstitucion
                            acta.alcance = form.cleaned_data['alcance']
                            acta.entregables = form.cleaned_data['entregables']
                            acta.justificacion = form.cleaned_data['justificacion']
                            acta.objetivos = form.cleaned_data['objetivos']
                            acta.save()
                        else:
                            acta = ActaConstitucion(
                                proyecto=project,
                                alcance=form.cleaned_data['alcance'],
                                entregables=form.cleaned_data['entregables'],
                                justificacion=form.cleaned_data['justificacion'],
                                objetivos=form.cleaned_data['objetivos']
                            )
                            acta.save()
                    else:
                        # Modo creación: crear nuevo proyecto
                        project = Project(
                            name=data['project_data']['name'],
                            description=data['project_data']['description'],
                            start_date=data['project_data']['start_date'],
                            end_date=data['project_data']['end_date'],
                            budget=data['project_data'].get('budget'),
                            status='planning',
                            created_by=request.user
                        )
                        project.save()
                        
                        # Crear acta de constitución
                        acta = ActaConstitucion(
                            proyecto=project,
                            alcance=form.cleaned_data['alcance'],
                            entregables=form.cleaned_data['entregables'],
                            justificacion=form.cleaned_data['justificacion'],
                            objetivos=form.cleaned_data['objetivos']
                        )
                        acta.save()
                    
                    data['project_id'] = project.id
                    data['step'] = 3
                    save_wizard_data(request, data)
                    if edit_mode:
                        messages.success(request, 'Proyecto y acta de constitución actualizados.')
                    else:
                        messages.success(request, 'Proyecto y acta de constitución creados.')
                    return redirect('wizard_step', step=3)
            except Exception as e:
                messages.error(request, f'Error al guardar el proyecto: {str(e)}')
        context['form'] = form
        
    elif step == 3:
        # Guardar stakeholders seleccionados y nuevos
        data['stakeholder_ids'] = request.POST.getlist('stakeholders')
        
        # Parsear nuevos stakeholders del JSON
        try:
            new_stakeholders_json = request.POST.get('new_stakeholders', '[]')
            data['new_stakeholders'] = json.loads(new_stakeholders_json)
        except json.JSONDecodeError:
            data['new_stakeholders'] = []
        
        # Crear los nuevos stakeholders en la base de datos
        project_id = data.get('project_id')
        if project_id and data['new_stakeholders']:
            try:
                project = Project.objects.get(id=project_id)
                for sh_data in data['new_stakeholders']:
                    stakeholder = Stakeholder.objects.create(
                        name=sh_data.get('name', ''),
                        email=sh_data.get('email', ''),
                        role=sh_data.get('role', 'other'),
                        contact_info=sh_data.get('contact_info', ''),
                        interest_level=sh_data.get('interest_level', 'medium'),
                        power_level=sh_data.get('power_level', 'medium')
                    )
                    stakeholder.projects.add(project)
                    data['stakeholder_ids'].append(str(stakeholder.id))
            except Exception as e:
                messages.warning(request, f'Error al crear algunos interesados: {str(e)}')
        
        data['step'] = 4
        save_wizard_data(request, data)
        messages.success(request, 'Interesados guardados.')
        return redirect('wizard_step', step=4)
        
    elif step == 4:
        form = WizardAlcanceForm(request.POST)
        if form.is_valid():
            data['alcance_data'] = form.cleaned_data
            
            # Crear o actualizar el alcance
            try:
                project = Project.objects.get(id=data['project_id'])
                edit_mode = data.get('edit_mode', False)
                
                if edit_mode and hasattr(project, 'alcance'):
                    # Actualizar alcance existente
                    alcance = project.alcance
                    alcance.descripcion = form.cleaned_data['descripcion']
                    alcance.objetivos = form.cleaned_data['objetivos']
                    alcance.save()
                else:
                    # Crear nuevo alcance
                    alcance = Alcance(
                        proyecto=project,
                        descripcion=form.cleaned_data['descripcion'],
                        objetivos=form.cleaned_data['objetivos']
                    )
                    alcance.save()
                data['step'] = 5
                save_wizard_data(request, data)
                messages.success(request, 'Alcance guardado.')
                return redirect('wizard_step', step=5)
            except Exception as e:
                messages.error(request, f'Error al guardar el alcance: {str(e)}')
        context['form'] = form
        
    elif step == 5:
        # Guardar riesgos y comunicaciones
        data['risks'] = json.loads(request.POST.get('risks', '[]'))
        data['communications'] = json.loads(request.POST.get('communications', '[]'))
        
        # Crear o actualizar riesgos en la base de datos
        try:
            project = Project.objects.get(id=data['project_id'])
            edit_mode = data.get('edit_mode', False)
            
            # En modo edición, eliminar riesgos existentes y crear nuevos
            if edit_mode:
                Risk.objects.filter(project=project).delete()
            
            for risk_data in data['risks']:
                Risk.objects.create(
                    project=project,
                    description=risk_data.get('description', ''),
                    probability=risk_data.get('probability', 'medium'),
                    impact=risk_data.get('impact', 'medium'),
                    mitigation_plan=risk_data.get('mitigation_plan', ''),
                    identified_by=risk_data.get('identified_by', request.user.username)
                )
            
            # En modo edición, eliminar comunicaciones existentes y crear nuevas
            if edit_mode:
                Comunicacion.objects.filter(proyecto=project).delete()
            
            for comm_data in data.get('communications', []):
                # Obtener el stakeholder si se especificó
                stakeholder = None
                recipient = comm_data.get('recipient', '')
                if recipient:
                    # Buscar stakeholder por nombre
                    stakeholders = Stakeholder.objects.filter(name__icontains=recipient)
                    if stakeholders.exists():
                        stakeholder = stakeholders.first()
                
                Comunicacion.objects.create(
                    proyecto=project,
                    tipo=comm_data.get('type', 'email') if comm_data.get('type', 'email') in {'email', 'reunion', 'llamada'} else 'email',
                    mensaje=comm_data.get('description', ''),
                    fecha=datetime.now(),
                    interesado=stakeholder
                )
            
            # Asociar stakeholders al proyecto (en modo edición, primero limpiar y luego agregar)
            if edit_mode:
                project.stakeholders.clear()
            for stakeholder_id in data.get('stakeholder_ids', []):
                stakeholder = Stakeholder.objects.get(id=stakeholder_id)
                stakeholder.projects.add(project)
                
            data['step'] = 6
            save_wizard_data(request, data)
            messages.success(request, 'Riesgos y comunicaciones guardados.')
            return redirect('wizard_step', step=6)
        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')
            
    elif step == 6:
        # Guardar actividades y recursos
        data['activities'] = json.loads(request.POST.get('activities', '[]'))
        
        # Crear actividades en la base de datos
        try:
            project = Project.objects.get(id=data['project_id'])
            edit_mode = data.get('edit_mode', False)
            
            # En modo edición, eliminar actividades existentes y crear nuevas
            if edit_mode:
                Activity.objects.filter(project=project).delete()
            
            def parse_date(date_str):
                if not date_str:
                    return None
                if isinstance(date_str, date):
                    return date_str
                return datetime.fromisoformat(date_str).date() if 'T' in str(date_str) else date.fromisoformat(date_str)
            
            for act_data in data['activities']:
                start_date = parse_date(act_data.get('start_date'))
                end_date = parse_date(act_data.get('end_date'))
                
                if start_date and end_date and start_date > end_date:
                    messages.error(request, f'Error en actividad "{act_data.get("name")}": La fecha de inicio no puede ser posterior a la fecha de fin.')
                    context['activities'] = data['activities']
                    return render(request, 'projects/project_wizard.html', context)
                
                if start_date and project.start_date and start_date < project.start_date:
                    messages.error(request, f'Error en actividad "{act_data.get("name")}": La fecha de inicio no puede ser anterior al inicio del proyecto.')
                    context['activities'] = data['activities']
                    return render(request, 'projects/project_wizard.html', context)
                
                if end_date and project.end_date and end_date > project.end_date:
                    messages.error(request, f'Error en actividad "{act_data.get("name")}": La fecha de fin no puede ser posterior al fin del proyecto.')
                    context['activities'] = data['activities']
                    return render(request, 'projects/project_wizard.html', context)
            
            # Crear las actividades primero sin predecesoras
            created_activities = {}
            for act_data in data['activities']:
                activity = Activity.objects.create(
                    project=project,
                    name=act_data.get('name', ''),
                    description=act_data.get('description', ''),
                    start_date=act_data.get('start_date') or None,
                    end_date=act_data.get('end_date') or None,
                    cost=act_data.get('cost'),
                    status='pending'
                )
                # Guardar referencia para predecesoras
                created_activities[act_data.get('id')] = activity
                
                # Guardar recursos para esta actividad
                for res_data in act_data.get('resources', []):
                    Resource.objects.create(
                        activity=activity,
                        name=res_data.get('name', ''),
                        type=res_data.get('type', 'material'),
                        quantity=res_data.get('quantity', 1),
                        cost_per_unit=res_data.get('cost_per_unit', 0)
                    )
            
            # Ahora asignar predecesoras
            for act_data in data['activities']:
                if act_data.get('predecessor'):
                    activity = created_activities.get(act_data.get('id'))
                    predecessor = created_activities.get(act_data.get('predecessor'))
                    if activity and predecessor:
                        activity.predecessor = predecessor
                        activity.save()
            
            data['step'] = 7
            save_wizard_data(request, data)
            messages.success(request, 'Actividades y recursos guardados.')
            return redirect('wizard_step', step=7)
        except Exception as e:
            messages.error(request, f'Error al guardar actividades: {str(e)}')
            
    elif step == 7:
        # Guardar hitos y finalizar
        data['milestones'] = json.loads(request.POST.get('milestones', '[]'))
        
        try:
            project = Project.objects.get(id=data['project_id'])
            edit_mode = data.get('edit_mode', False)
            
            def parse_date(date_str):
                if not date_str:
                    return None
                if isinstance(date_str, date):
                    return date_str
                return datetime.fromisoformat(date_str).date() if 'T' in str(date_str) else date.fromisoformat(date_str)
            
            for mile_data in data['milestones']:
                due_date = parse_date(mile_data.get('due_date'))
                
                if due_date and project.start_date and due_date < project.start_date:
                    messages.error(request, f'Error en hito "{mile_data.get("name")}": La fecha limite no puede ser anterior al inicio del proyecto.')
                    context['milestones'] = data['milestones']
                    return render(request, 'projects/project_wizard.html', context)
                
                if due_date and project.end_date and due_date > project.end_date:
                    messages.error(request, f'Error en hito "{mile_data.get("name")}": La fecha limite no puede ser posterior al fin del proyecto.')
                    context['milestones'] = data['milestones']
                    return render(request, 'projects/project_wizard.html', context)
            
            # En modo edición, eliminar hitos existentes y crear nuevos
            if edit_mode:
                Milestone.objects.filter(project=project).delete()
            
            # Crear los hitos
            created_milestones = {}
            for mile_data in data['milestones']:
                milestone = Milestone.objects.create(
                    project=project,
                    name=mile_data.get('name', ''),
                    description=mile_data.get('description', ''),
                    due_date=mile_data.get('due_date') or None,
                    phase=mile_data.get('phase', 'execution'),
                    is_phase_gate=mile_data.get('is_phase_gate', False)
                )
                # Guardar referencia para associações
                created_milestones[mile_data.get('id')] = milestone
                # Asociar actividades (convertir IDs prefijados a IDs reales)
                activity_ids = mile_data.get('activities', [])
                if activity_ids:
                    # Convertir IDs prefijados (edit_X) a IDs reales
                    real_activity_ids = []
                    for act_id in activity_ids:
                        if act_id.startswith('edit_'):
                            real_id = int(act_id.replace('edit_', ''))
                            real_activity_ids.append(real_id)
                        else:
                            real_activity_ids.append(act_id)
                    milestone.activities.set(real_activity_ids)
            
            # Limpiar datos del wizard
            clear_wizard_data(request)
            if edit_mode:
                messages.success(request, f'Proyecto "{project.name}" actualizado exitosamente.')
            else:
                messages.success(request, f'Proyecto "{project.name}" creado exitosamente.')
            return redirect('project_detail', pk=project.id)
        except Exception as e:
            messages.error(request, f'Error al guardar hitos: {str(e)}')
    
    return render(request, 'projects/project_wizard.html', context)


def _check_wizard_project_permission(request, data):
    """Verifica que el usuario tenga permisos sobre el proyecto del wizard."""
    from .permissions import can_edit_project
    project_id = data.get('project_id')
    if not project_id:
        return True
    try:
        project = Project.objects.get(id=project_id)
        return can_edit_project(request.user, project)
    except Project.DoesNotExist:
        return False


def _get_wizard_permission_error():
    return JsonResponse(
        {'success': False, 'error': 'No tienes permisos para modificar este proyecto.'},
        status=403
    )


@login_required
@require_POST
def wizard_add_stakeholder(request):
    """Agrega un nuevo stakeholder temporalmente al wizard."""
    data = get_wizard_data(request)
    if not _check_wizard_project_permission(request, data):
        return _get_wizard_permission_error()
    
    form = WizardStakeholderForm(request.POST)
    if form.is_valid():
        new_stakeholder = {
            'id': f"new_{len(data.get('new_stakeholders', []))}",
            'name': form.cleaned_data['name'],
            'email': form.cleaned_data['email'],
            'role': form.cleaned_data['role'],
            'contact_info': form.cleaned_data.get('contact_info', ''),
            'interest_level': form.cleaned_data['interest_level'],
            'power_level': form.cleaned_data['power_level'],
        }
        data.setdefault('new_stakeholders', []).append(new_stakeholder)
        save_wizard_data(request, data)
        return JsonResponse({'success': True, 'stakeholder': new_stakeholder})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def wizard_add_risk(request):
    """Agrega un riesgo temporalmente al wizard."""
    data = get_wizard_data(request)
    if not _check_wizard_project_permission(request, data):
        return _get_wizard_permission_error()
    
    form = WizardRiskForm(request.POST)
    if form.is_valid():
        risk = {
            'id': f"risk_{len(data.get('risks', []))}",
            'description': form.cleaned_data['description'],
            'probability': form.cleaned_data['probability'],
            'impact': form.cleaned_data['impact'],
            'mitigation_plan': form.cleaned_data.get('mitigation_plan', ''),
            'identified_by': form.cleaned_data.get('identified_by', request.user.username),
        }
        data.setdefault('risks', []).append(risk)
        save_wizard_data(request, data)
        return JsonResponse({'success': True, 'risk': risk})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def wizard_add_activity(request):
    """Agrega una actividad temporalmente al wizard."""
    data = get_wizard_data(request)
    if not _check_wizard_project_permission(request, data):
        return _get_wizard_permission_error()
    
    form = WizardActivityForm(request.POST, project_id=data.get('project_id'))
    if form.is_valid():
        activity = {
            'id': f"act_{len(data.get('activities', []))}",
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data.get('description', ''),
            'start_date': form.cleaned_data['start_date'].isoformat() if form.cleaned_data.get('start_date') else None,
            'end_date': form.cleaned_data['end_date'].isoformat() if form.cleaned_data.get('end_date') else None,
            'cost': str(form.cleaned_data.get('cost', 0)),
            'resources': [],
        }
        data.setdefault('activities', []).append(activity)
        save_wizard_data(request, data)
        return JsonResponse({'success': True, 'activity': activity})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def wizard_add_milestone(request):
    """Agrega un hito temporalmente al wizard."""
    data = get_wizard_data(request)
    if not _check_wizard_project_permission(request, data):
        return _get_wizard_permission_error()
    
    form = WizardMilestoneForm(request.POST, project_id=data.get('project_id'))
    if form.is_valid():
        milestone = {
            'id': f"mile_{len(data.get('milestones', []))}",
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data.get('description', ''),
            'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data.get('due_date') else None,
            'phase': form.cleaned_data.get('phase', 'execution'),
            'is_phase_gate': form.cleaned_data.get('is_phase_gate', False),
            'activities': form.cleaned_data.get('activities', []),
        }
        data.setdefault('milestones', []).append(milestone)
        save_wizard_data(request, data)
        return JsonResponse({'success': True, 'milestone': milestone})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def wizard_cancel(request):
    """Cancela el wizard y limpia los datos."""
    # Si hay un proyecto creado, eliminarlo
    data = get_wizard_data(request)
    if data.get('project_id'):
        try:
            project = Project.objects.get(id=data['project_id'])
            project.delete()
        except Project.DoesNotExist:
            pass
    
    clear_wizard_data(request)
    messages.info(request, 'Creación de proyecto cancelada.')
    return redirect('project_list')


@login_required
def project_edit_wizard(request, pk):
    """
    Vista para editar un proyecto existente usando el wizard.
    Carga los datos existentes del proyecto en la sesión del wizard.
    """
    from .views import can_edit_project
    
    project = get_object_or_404(Project, pk=pk)
    
    # Verificar permisos
    if not can_edit_project(request.user, project):
        messages.error(request, 'No tienes permisos para editar este proyecto.')
        return redirect('project_list')
    
    # Limpiar datos anteriores del wizard
    clear_wizard_data(request)
    
    # Cargar datos del proyecto existente
    wizard_data = {
        'step': 1,
        'project_id': project.id,
        'edit_mode': True,  # Flag para indicar modo edición
        'project_data': {
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.isoformat() if project.start_date else '',
            'end_date': project.end_date.isoformat() if project.end_date else '',
            'budget': str(project.budget) if project.budget else '',
            'status': project.status,
        },
        'acta_data': {},
        'stakeholder_ids': list(project.stakeholders.values_list('id', flat=True)),
        'new_stakeholders': [],
        'alcance_data': {},
        'risks': [],
        'communications': [],
        'activities': [],
        'milestones': [],
    }
    
    # Cargar Acta de Constitución
    if hasattr(project, 'actaconstitucion'):
        acta = project.actaconstitucion
        wizard_data['acta_data'] = {
            'alcance': acta.alcance,
            'entregables': acta.entregables,
            'justificacion': acta.justificacion,
            'objetivos': acta.objetivos,
        }
    
    # Cargar Alcance
    if hasattr(project, 'alcance'):
        alcance = project.alcance
        wizard_data['alcance_data'] = {
            'descripcion': alcance.descripcion,
            'objetivos': alcance.objetivos,
        }
    
    # Cargar Riesgos
    risks = Risk.objects.filter(project=project)
    wizard_data['risks'] = [
        {
            'id': f"edit_{r.id}",  # ID temporal para edición
            'description': r.description,
            'probability': r.probability,
            'impact': r.impact,
            'mitigation_plan': r.mitigation_plan,
            'identified_by': r.identified_by or '',
        }
        for r in risks
    ]
    
    # Cargar Comunicaciones
    comunicaciones = Comunicacion.objects.filter(proyecto=project)
    wizard_data['communications'] = [
        {
            'id': f"edit_{c.id}",
            'type': c.tipo,
            'frequency': 'semanal',  # Valor por defecto
            'recipient': c.interesado.name if c.interesado else '',
            'description': c.mensaje,
        }
        for c in comunicaciones
    ]
    
    # Cargar Actividades
    activities = Activity.objects.filter(project=project)
    # Crear un mapa de actividades para resolver predecesoras
    activity_id_map = {a.id: f"edit_{a.id}" for a in activities}
    wizard_data['activities'] = [
        {
            'id': f"edit_{a.id}",  # ID temporal para edición
            'name': a.name,
            'description': a.description,
            'start_date': a.start_date.isoformat() if a.start_date else '',
            'end_date': a.end_date.isoformat() if a.end_date else '',
            'status': a.status,
            'cost': str(a.cost) if a.cost else '',
            'time_estimate': a.time_estimate or '',
            'predecessor_id': activity_id_map.get(a.predecessor.id) if a.predecessor else None,
            'assigned_to_id': a.assigned_to.id if a.assigned_to else None,
            'resources': [
                {
                    'name': r.name,
                    'type': r.type,
                    'quantity': r.quantity,
                    'cost_per_unit': str(r.cost_per_unit) if r.cost_per_unit else '0',
                }
                for r in a.resource_set.all()
            ],
        }
        for a in activities
    ]
    
    # Cargar Hitos
    milestones = Milestone.objects.filter(project=project)
    wizard_data['milestones'] = [
        {
            'id': f"edit_{m.id}",  # ID temporal para edición
            'name': m.name,
            'description': m.description,
            'due_date': m.due_date.isoformat() if m.due_date else '',
            'completed': m.completed,
            'phase': m.phase,
            'is_phase_gate': m.is_phase_gate,
            'activities': [activity_id_map.get(act_id) for act_id in m.activities.values_list('id', flat=True) if act_id in activity_id_map],
        }
        for m in milestones
    ]
    
    # Guardar datos en sesión
    save_wizard_data(request, wizard_data)
    
    messages.info(request, f'Editando proyecto: {project.name}. Haga clic en Siguiente para continuar.')
    return redirect('wizard_step', step=1)
