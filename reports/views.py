from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from projects.models import Project, Activity
import csv
import json

@login_required
def report_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'reports/report_list.html', {'projects': projects})

@login_required
def gantt_chart(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    milestones = project.milestone_set.all()
    return render(request, 'reports/gantt.html', {'project': project, 'activities': activities, 'milestones': milestones})

@login_required
def progress_report(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    completed = activities.filter(status='completed').count()
    total = activities.count()
    progress = (completed / total * 100) if total > 0 else 0
    return render(request, 'reports/progress_report.html', {
        'project': project,
        'progress': progress,
        'completed': completed,
        'total': total
    })

@login_required
def cost_report(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    total_cost = sum(activity.cost or 0 for activity in activities)
    return render(request, 'reports/cost_report.html', {
        'project': project,
        'activities': activities,
        'total_cost': total_cost
    })

@login_required
def export_csv(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Activity', 'Status', 'Cost', 'Start Date', 'End Date'])
    for activity in activities:
        writer.writerow([activity.name, activity.status, activity.cost, activity.start_date, activity.end_date])
    return response

@login_required
def status_report(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    completed = activities.filter(status='completed').count()
    total = activities.count()
    progress = (completed / total * 100) if total > 0 else 0

    # Cost calculations
    planned_cost = sum(activity.cost or 0 for activity in activities)
    # Assuming actual cost is tracked elsewhere, for now use planned
    actual_cost = planned_cost  # Placeholder
    cost_difference = actual_cost - planned_cost

    # Time calculations
    from datetime import date
    today = date.today()
    planned_days = (project.end_date - project.start_date).days if project.end_date and project.start_date else 0
    actual_days = (today - project.start_date).days if project.start_date else 0
    time_difference = actual_days - planned_days

    activity_data = []
    for activity in activities:
        act_planned_days = (activity.end_date - activity.start_date).days if activity.end_date and activity.start_date else 0
        act_actual_days = (today - activity.start_date).days if activity.start_date else 0
        act_time_diff = act_actual_days - act_planned_days
        activity_data.append({
            'name': activity.name,
            'status': activity.status,
            'progress': 100 if activity.status == 'completed' else 0,  # Placeholder
            'planned_cost': activity.cost or 0,
            'actual_cost': activity.cost or 0,  # Placeholder
            'cost_diff': 0,
            'planned_days': act_planned_days,
            'actual_days': act_actual_days,
            'time_diff': act_time_diff,
        })

    return render(request, 'reports/status_report.html', {
        'project': project,
        'progress': progress,
        'completed': completed,
        'total': total,
        'planned_cost': planned_cost,
        'actual_cost': actual_cost,
        'cost_difference': cost_difference,
        'planned_days': planned_days,
        'actual_days': actual_days,
        'time_difference': time_difference,
        'activities': activity_data,
    })

@login_required
def calendar_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    milestones = project.milestone_set.all()

    events = []
    for activity in activities:
        events.append({
            'title': f'Actividad: {activity.name}',
            'start': activity.start_date.isoformat() if activity.start_date else None,
            'end': activity.end_date.isoformat() if activity.end_date else None,
            'backgroundColor': 'blue',
        })
    for milestone in milestones:
        events.append({
            'title': f'Hito: {milestone.name}',
            'start': milestone.due_date.isoformat(),
            'backgroundColor': 'red',
        })

    return render(request, 'reports/calendar.html', {
        'project': project,
        'events': json.dumps(events),
    })

@login_required
def performance_graphs(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()

    # Data for charts
    status_data = {
        'pending': activities.filter(status='pending').count(),
        'in_progress': activities.filter(status='in_progress').count(),
        'completed': activities.filter(status='completed').count(),
    }

    cost_data = [float(activity.cost) if activity.cost else 0 for activity in activities]
    cost_labels = [activity.name for activity in activities]

    return render(request, 'reports/performance_graphs.html', {
        'project': project,
        'status_data': status_data,
        'cost_data': json.dumps(cost_data),
        'cost_labels': json.dumps(cost_labels),
    })
