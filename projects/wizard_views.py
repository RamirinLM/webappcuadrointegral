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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import json
from datetime import datetime, date
from decimal import Decimal

from .models import (
    Project, ActaConstitucion, Alcance, Activity, Milestone,
    Comunicacion, ActivityAssignment
)
from .forms import ProjectForm, ActaConstitucionForm, ActivityForm, MilestoneForm
from .permissions import get_user_projects
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
    """Convierte datos del formulario a formato JSON serializable.
    
    Preserva int/float (JSON-serializables nativos). Convierte Decimal a string
    porque Decimal NO es serializable por json.dumps().
    """
    if isinstance(data, dict):
        return {k: serialize_form_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_form_data(item) for item in data]
    elif isinstance(data, (int, float)):
        return data  # JSON-serializable, preservar
    elif isinstance(data, Decimal):
        return str(data)  # No es JSON-serializable, convertir a string
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
    Vista principal del wizard para CREAR un nuevo proyecto.
    Siempre limpia la sesión y empieza desde 0.
    """
    # Limpiar datos anteriores para empezar nuevo proyecto desde 0
    clear_wizard_data(request)
    data = {'step': 1}
    save_wizard_data(request, data)
    return redirect('wizard_step', step=1)


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
        # Usar datos de la sesión consistentemente (tanto create como edit)
        # project_edit_wizard ya cargó project_data en la sesión
        initial = data.get('project_data', {})
        context['form'] = WizardProjectForm(initial=initial)
        context['title'] = 'Datos del Proyecto'
        context['description'] = 'Ingrese la información básica del proyecto.'
        
    elif step == 2:
        context['form'] = WizardActaForm(initial=data.get('acta_data', {}))
        context['title'] = 'Acta de Constitución'
        context['description'] = 'Complete el acta de constitución del proyecto.'
        
    elif step == 3:
        context['stakeholders'] = Stakeholder.objects.filter(projects__in=get_user_projects(request.user)).distinct()
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
        risks = data.get('risks', [])
        communications = data.get('communications', [])
        context['risks'] = risks
        context['risks_json'] = json.dumps(risks)
        context['communications'] = communications
        context['communications_json'] = json.dumps(communications)
        context['risk_form'] = WizardRiskForm()
        context['communication_form'] = WizardCommunicationForm(user=request.user)
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
                context['activities_json'] = json.dumps(session_activities)
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
                milestones = data.get('milestones', [])
                session_activities = data.get('activities', [])
                context['milestones'] = milestones
                context['milestones_json'] = json.dumps(milestones)
                context['activities'] = session_activities
                context['activities_json'] = json.dumps(session_activities)
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
                    # Si ya tiene ID numérico, ya fue creado en un POST anterior
                    sh_id = sh_data.get('id')
                    if sh_id is not None:
                        try:
                            int(sh_id)
                            continue  # Saltar: ya fue creado antes
                        except (ValueError, TypeError):
                            pass  # ID temporal (new_0, new_1, etc.) → crear
                    
                    # Validar email antes de crear
                    email_raw = sh_data.get('email', '')
                    if email_raw:
                        try:
                            validate_email(email_raw)
                        except DjangoValidationError:
                            messages.warning(
                                request,
                                f'El correo "{email_raw}" del interesado "{sh_data.get("name", "")}" no es válido. Se omitió.'
                            )
                            continue
                    
                    stakeholder = Stakeholder.objects.create(
                        name=sh_data.get('name', ''),
                        email=email_raw,
                        role=sh_data.get('role', 'other'),
                        contact_info=sh_data.get('contact_info', ''),
                        interest_level=sh_data.get('interest_level', 'medium'),
                        power_level=sh_data.get('power_level', 'medium')
                    )
                    stakeholder.projects.add(project)
                    data['stakeholder_ids'].append(str(stakeholder.id))
                    sh_data['id'] = stakeholder.id  # Marcar como creado para próximos POST
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
            
            # Crear o actualizar el alcance (si ya existe por POST anterior, actualizar)
            try:
                project = Project.objects.get(id=data['project_id'])
                
                if hasattr(project, 'alcance'):
                    # Actualizar alcance existente (tanto create mode como edit)
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

        try:
            project = Project.objects.get(id=data['project_id'])

            # ── Riesgos: update-or-create ──
            existing_risks = {r.id: r for r in Risk.objects.filter(project=project)}
            submitted_risk_ids = set()

            for risk_data in data['risks']:
                risk_id = risk_data.get('id')
                existing_risk = None
                db_id = None
                try:
                    if isinstance(risk_id, str) and risk_id.startswith('edit_'):
                        db_id = int(risk_id.replace('edit_', ''))
                    elif risk_id is not None:
                        db_id = int(risk_id)
                    if db_id is not None and db_id in existing_risks:
                        existing_risk = existing_risks[db_id]
                except (ValueError, TypeError):
                    pass

                if existing_risk:
                    existing_risk.description = risk_data.get('description', '')
                    existing_risk.probability = risk_data.get('probability', 'medium')
                    existing_risk.impact = risk_data.get('impact', 'medium')
                    existing_risk.mitigation_plan = risk_data.get('mitigation_plan', '')
                    existing_risk.identified_by = risk_data.get('identified_by', request.user.username)
                    existing_risk.save()
                    submitted_risk_ids.add(db_id)
                else:
                    risk = Risk.objects.create(
                        project=project,
                        description=risk_data.get('description', ''),
                        probability=risk_data.get('probability', 'medium'),
                        impact=risk_data.get('impact', 'medium'),
                        mitigation_plan=risk_data.get('mitigation_plan', ''),
                        identified_by=risk_data.get('identified_by', request.user.username)
                    )
                    risk_data['id'] = risk.id  # Guardar ID real en sesión (serialize lo pasa a str)
                    submitted_risk_ids.add(risk.id)

            # Eliminar riesgos que el usuario quitó
            for db_id, existing in existing_risks.items():
                if db_id not in submitted_risk_ids:
                    existing.delete()

            # ── Comunicaciones: update-or-create ──
            existing_comms = {c.id: c for c in Comunicacion.objects.filter(proyecto=project)}
            submitted_comm_ids = set()

            for comm_data in data.get('communications', []):
                comm_id = comm_data.get('id')
                existing_comm = None
                db_id = None
                try:
                    if isinstance(comm_id, str) and comm_id.startswith('edit_'):
                        db_id = int(comm_id.replace('edit_', ''))
                    elif comm_id is not None:
                        db_id = int(comm_id)
                    if db_id is not None and db_id in existing_comms:
                        existing_comm = existing_comms[db_id]
                except (ValueError, TypeError):
                    pass

                # Resolver stakeholder
                stakeholder = None
                recipient = comm_data.get('recipient', '')
                if recipient:
                    stakeholders_qs = Stakeholder.objects.filter(name__icontains=recipient)
                    if stakeholders_qs.exists():
                        stakeholder = stakeholders_qs.first()

                if existing_comm:
                    existing_comm.tipo = comm_data.get('type', 'email') if comm_data.get('type', 'email') in {'email', 'reunion', 'llamada'} else 'email'
                    existing_comm.mensaje = comm_data.get('description', '')
                    existing_comm.interesado = stakeholder
                    existing_comm.save()
                    submitted_comm_ids.add(db_id)
                else:
                    comm = Comunicacion.objects.create(
                        proyecto=project,
                        tipo=comm_data.get('type', 'email') if comm_data.get('type', 'email') in {'email', 'reunion', 'llamada'} else 'email',
                        mensaje=comm_data.get('description', ''),
                        fecha=datetime.now(),
                        interesado=stakeholder
                    )
                    comm_data['id'] = comm.id
                    submitted_comm_ids.add(comm.id)

            # Eliminar comunicaciones que el usuario quitó
            for db_id, existing in existing_comms.items():
                if db_id not in submitted_comm_ids:
                    existing.delete()

            # Asociar stakeholders al proyecto
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
            
            def parse_date(date_str):
                if not date_str:
                    return None
                if isinstance(date_str, date):
                    return date_str
                return datetime.fromisoformat(date_str).date() if 'T' in str(date_str) else date.fromisoformat(date_str)
            
            for act_data in data['activities']:
                start_date = parse_date(act_data.get('start_date')) or project.start_date
                end_date = parse_date(act_data.get('end_date')) or project.end_date
                
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
            
            # Obtener actividades existentes del proyecto (tanto create como edit mode)
            # En create mode: después del primer POST, si el usuario vuelve atrás, las
            # actividades ya existen en DB y debemos actualizarlas, no duplicarlas
            existing_activities = {a.id: a for a in Activity.objects.filter(project=project)}
            submitted_ids = set()
            
            # Crear o actualizar las actividades
            created_activities = {}
            for act_data in data['activities']:
                act_id = act_data.get('id')
                is_existing = False
                # Intentar determinar si esta actividad ya existe en DB
                # El ID puede venir como: entero (ID real), 'edit_42' (edit mode), 'act_X' (nueva)
                try:
                    db_id = None
                    if isinstance(act_id, str) and act_id.startswith('edit_'):
                        db_id = int(act_id.replace('edit_', ''))
                    elif act_id is not None:
                        db_id = int(act_id)
                    
                    if db_id is not None and db_id in existing_activities:
                        activity = existing_activities[db_id]
                        activity.name = act_data.get('name', '')
                        raw_desc = act_data.get('description', '')
                        if raw_desc:
                            activity.description = raw_desc
                        activity.start_date = parse_date(act_data.get('start_date')) or activity.start_date
                        activity.end_date = parse_date(act_data.get('end_date')) or activity.end_date
                        cost_raw = act_data.get('cost')
                        if cost_raw:
                            try:
                                activity.cost = float(cost_raw) if isinstance(cost_raw, str) else cost_raw
                            except (ValueError, TypeError):
                                pass
                        activity.save()
                        is_existing = True
                        submitted_ids.add(db_id)
                        created_activities[act_id] = activity
                        
                        # Actualizar recursos: borrar y recrear
                        activity.resource_set.all().delete()
                        for res_data in act_data.get('resources', []):
                            quantity_raw = res_data.get('quantity', 1)
                            cost_raw = res_data.get('cost_per_unit', 0)
                            quantity_val = int(quantity_raw) if isinstance(quantity_raw, str) else quantity_raw
                            cost_val = Decimal(str(cost_raw)) if not isinstance(cost_raw, Decimal) else cost_raw
                            if quantity_val < 1:
                                messages.warning(request, f'Recurso "{res_data.get("name", "")}" en actividad "{act_data.get("name")}": cantidad debe ser >= 1. Se usó 1.')
                                quantity_val = 1
                            if cost_val < 0:
                                messages.warning(request, f'Recurso "{res_data.get("name", "")}" en actividad "{act_data.get("name")}": costo por unidad negativo. Se usó 0.')
                                cost_val = Decimal('0')
                            Resource.objects.create(
                                activity=activity,
                                name=res_data.get('name', ''),
                                type=res_data.get('type', 'material'),
                                quantity=quantity_val,
                                cost_per_unit=cost_val,
                            )
                except (ValueError, TypeError):
                    pass
                
                if not is_existing:
                    # Es una actividad nueva (no existía antes)
                    # cost se calcula automáticamente desde los recursos
                    # Si no se especificaron fechas, usar las del proyecto
                    activity_start = parse_date(act_data.get('start_date')) or project.start_date
                    activity_end = parse_date(act_data.get('end_date')) or project.end_date
                    # El modelo Activity.save() llama a full_clean() y no permite
                    # blank=True sin migración → usar placeholder si está vacía
                    raw_desc = act_data.get('description', '')
                    if not raw_desc:
                        raw_desc = '(sin descripción)'
                    activity = Activity.objects.create(
                        project=project,
                        name=act_data.get('name', ''),
                        description=raw_desc,
                        start_date=activity_start,
                        end_date=activity_end,
                        status='pending'
                    )
                    created_activities[act_id] = activity
                    
                    # Guardar recursos para esta actividad nueva
                    for res_data in act_data.get('resources', []):
                        quantity_raw = res_data.get('quantity', 1)
                        cost_raw = res_data.get('cost_per_unit', 0)
                        quantity_val = int(quantity_raw) if isinstance(quantity_raw, str) else quantity_raw
                        cost_val = Decimal(str(cost_raw)) if not isinstance(cost_raw, Decimal) else cost_raw
                        if quantity_val < 1:
                            messages.warning(request, f'Recurso "{res_data.get("name", "")}" en actividad "{act_data.get("name")}": cantidad debe ser >= 1. Se usó 1.')
                            quantity_val = 1
                        if cost_val < 0:
                            messages.warning(request, f'Recurso "{res_data.get("name", "")}" en actividad "{act_data.get("name")}": costo por unidad negativo. Se usó 0.')
                            cost_val = Decimal('0')
                        Resource.objects.create(
                            activity=activity,
                            name=res_data.get('name', ''),
                            type=res_data.get('type', 'material'),
                            quantity=quantity_val,
                            cost_per_unit=cost_val,
                        )
            
            # En edit mode, eliminar actividades que fueron removidas por el usuario
            if edit_mode:
                for db_id, existing_act in existing_activities.items():
                    if db_id not in submitted_ids:
                        existing_act.delete()
            else:
                # En create mode: crear todas las actividades (ya se crearon arriba)
                pass
            
            # Ahora asignar predecesoras
            for act_data in data['activities']:
                if act_data.get('predecessor'):
                    activity = created_activities.get(act_data.get('id'))
                    predecessor = created_activities.get(act_data.get('predecessor'))
                    if activity and predecessor:
                        activity.predecessor = predecessor
                        activity.save()
            
            # Guardar mapping de IDs temporales → IDs reales de DB
            # Necesario para que step 7 resuelva las referencias en hitos
            activity_id_mapping = {}
            for temp_id, activity_obj in created_activities.items():
                activity_id_mapping[temp_id] = activity_obj.id
            data['activity_id_mapping'] = activity_id_mapping
            
            # Actualizar IDs de actividades en la sesión a IDs reales de DB
            # para que step 7 muestre IDs consistentes
            for act_data in data['activities']:
                temp_id = act_data.get('id')
                real_id = activity_id_mapping.get(temp_id)
                if real_id is not None:
                    act_data['id'] = real_id
                # También actualizar referencias de predecesoras
                pred = act_data.get('predecessor')
                if pred is not None:
                    mapped_pred = activity_id_mapping.get(str(pred))
                    if mapped_pred is not None:
                        act_data['predecessor'] = mapped_pred
            
            # Convertir referencias a actividades en los hitos (milestones)
            # que aún usan IDs temporales (edit_X o act_X) a IDs reales de DB
            milestones = data.get('milestones', [])
            for milestone in milestones:
                if milestone.get('activities'):
                    converted = []
                    for aid in milestone['activities']:
                        str_aid = str(aid)
                        if str_aid in activity_id_mapping:
                            converted.append(activity_id_mapping[str_aid])
                        else:
                            try:
                                converted.append(int(aid))
                            except (ValueError, TypeError):
                                pass
                    milestone['activities'] = converted
            
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
            
            # En modo edición: actualizar hitos existentes en vez de borrarlos
            # para no perder datos como completed/completed_at
            if edit_mode:
                existing_milestones = {m.id: m for m in Milestone.objects.filter(project=project)}
                submitted_milestone_ids = set()
            else:
                existing_milestones = {}
                submitted_milestone_ids = set()
            
            # Crear o actualizar hitos
            created_milestones = {}
            activity_id_mapping = data.get('activity_id_mapping', {})
            for mile_data in data['milestones']:
                mile_id = mile_data.get('id')
                is_existing = False
                if edit_mode:
                    try:
                        db_id = int(str(mile_id).replace('edit_', '')) if isinstance(mile_id, str) and mile_id.startswith('edit_') else int(mile_id)
                        if db_id in existing_milestones:
                            milestone = existing_milestones[db_id]
                            milestone.name = mile_data.get('name', '')
                            milestone.description = mile_data.get('description', '')
                            milestone.due_date = mile_data.get('due_date') or None
                            milestone.phase = mile_data.get('phase', 'execution')
                            milestone.is_phase_gate = mile_data.get('is_phase_gate', False)
                            milestone.save()
                            is_existing = True
                            submitted_milestone_ids.add(db_id)
                            created_milestones[mile_id] = milestone
                    except (ValueError, TypeError):
                        pass
                
                if not is_existing:
                    milestone = Milestone.objects.create(
                        project=project,
                        name=mile_data.get('name', ''),
                        description=mile_data.get('description', ''),
                        due_date=mile_data.get('due_date') or None,
                        phase=mile_data.get('phase', 'execution'),
                        is_phase_gate=mile_data.get('is_phase_gate', False)
                    )
                    created_milestones[mile_id] = milestone
                
                # Asociar actividades (resolver IDs temporales a IDs reales)
                activity_ids = mile_data.get('activities', [])
                if activity_ids:
                    real_activity_ids = []
                    for act_id in activity_ids:
                        str_aid = str(act_id)
                        # Si el mapping lo tiene, es un ID real de DB
                        if str_aid in activity_id_mapping:
                            real_activity_ids.append(activity_id_mapping[str_aid])
                        else:
                            # Si no, intentar como entero directamente (ID de DB)
                            try:
                                real_activity_ids.append(int(act_id))
                            except (ValueError, TypeError):
                                pass
                    if real_activity_ids:
                        milestone.activities.set(real_activity_ids)
            
            # En edit mode, eliminar hitos que fueron removidos por el usuario
            if edit_mode:
                for db_id, existing_m in existing_milestones.items():
                    if db_id not in submitted_milestone_ids:
                        existing_m.delete()
            
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
            'predecessor': form.cleaned_data.get('predecessor').id if form.cleaned_data.get('predecessor') else None,
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
        # Convertir QuerySet de actividades a lista de IDs para JSON
        activities_qs = form.cleaned_data.get('activities', [])
        activities_ids = [a.id for a in activities_qs] if activities_qs else []
        milestone = {
            'id': f"mile_{len(data.get('milestones', []))}",
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data.get('description', ''),
            'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data.get('due_date') else None,
            'phase': form.cleaned_data.get('phase', 'execution'),
            'is_phase_gate': form.cleaned_data.get('is_phase_gate', False),
            'activities': activities_ids,
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
            'predecessor': activity_id_map.get(a.predecessor.id) if a.predecessor else None,
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
