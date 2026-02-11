from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from projects.models import Project, Activity

@login_required
def report_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'reports/report_list.html', {'projects': projects})

@login_required
def gantt_chart(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    activities = project.activity_set.all()
    return render(request, 'reports/gantt.html', {'project': project, 'activities': activities})
