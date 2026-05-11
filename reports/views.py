import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from projects.permissions import can_view_project, get_user_projects
from projects.services import export_project_csv, parse_report_filters
from projects.models import Project


def _get_project_for_user(user, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not can_view_project(user, project):
        raise PermissionDenied
    return project


def _filter_activities(project, filters):
    activities = project.activity_set.all()
    if filters.activity_status:
        activities = activities.filter(status=filters.activity_status)
    if filters.date_from:
        activities = activities.filter(start_date__gte=filters.date_from)
    if filters.date_to:
        activities = activities.filter(end_date__lte=filters.date_to)
    if filters.owner_id:
        activities = activities.filter(assigned_to_id=filters.owner_id)
    return activities.select_related("assigned_to")


@login_required
def report_list(request):
    filters = parse_report_filters(request.GET)
    projects = get_user_projects(request.user)
    if filters.project_status:
        projects = projects.filter(status=filters.project_status)
    if filters.owner_id:
        projects = projects.filter(created_by_id=filters.owner_id)
    return render(request, "reports/report_list.html", {"projects": projects, "filters": filters})


@login_required
def gantt_chart(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    milestones = project.milestone_set.all()

    timeline_start = project.start_date
    timeline_end = project.end_date

    if activities.filter(start_date__isnull=False).exists():
        activity_start = activities.exclude(start_date__isnull=True).order_by("start_date").first().start_date
        if timeline_start is None or activity_start < timeline_start:
            timeline_start = activity_start
    if activities.filter(end_date__isnull=False).exists():
        activity_end = activities.exclude(end_date__isnull=True).order_by("-end_date").first().end_date
        if timeline_end is None or activity_end > timeline_end:
            timeline_end = activity_end

    total_days = max(((timeline_end - timeline_start).days + 1), 1) if timeline_start and timeline_end else 1
    gantt_rows = []
    month_markers = []
    week_markers = []
    milestone_markers = []
    dependency_lines = []
    today_offset = None
    timeline_width_px = 960
    timeline_height_px = 0

    if timeline_start and timeline_end:
        total_weeks = max((total_days + 6) // 7, 1)
        timeline_width_px = max(total_weeks * 56, 960)
        px_per_day = timeline_width_px / total_days
        row_height = 60

        current = timeline_start.replace(day=1)
        while current <= timeline_end:
            next_month = current.replace(year=current.year + (1 if current.month == 12 else 0), month=1 if current.month == 12 else current.month + 1, day=1)
            marker_start = max(current, timeline_start)
            marker_end = min(next_month, timeline_end)
            offset_days = (marker_start - timeline_start).days
            width_days = max((marker_end - marker_start).days, 1)
            month_markers.append(
                {
                    "label": current.strftime("%b %Y"),
                    "offset_px": round(offset_days * px_per_day, 2),
                    "width_px": round(max(width_days * px_per_day, 72), 2),
                }
            )
            current = next_month

        week_cursor = timeline_start
        week_index = 0
        label_every = 1 if total_weeks <= 12 else (2 if total_weeks <= 24 else 4)
        while week_cursor <= timeline_end:
            offset_days = (week_cursor - timeline_start).days
            width_days = min(7, (timeline_end - week_cursor).days + 1)
            week_markers.append(
                {
                    "label": week_cursor.strftime("%d %b"),
                    "offset_px": round(offset_days * px_per_day, 2),
                    "width_px": round(max(width_days * px_per_day, 28), 2),
                    "show_label": week_index % label_every == 0,
                }
            )
            week_cursor = week_cursor + timedelta(days=7)
            week_index += 1

        today = date.today()
        if timeline_start <= today <= timeline_end:
            today_offset = round((today - timeline_start).days * px_per_day, 2)

        activity_rows = list(activities)
        critical_ids = set()
        if activity_rows:
            latest_activity = max(
                (activity for activity in activity_rows if activity.end_date),
                key=lambda activity: activity.end_date,
                default=None,
            )
            while latest_activity:
                critical_ids.add(latest_activity.pk)
                latest_activity = latest_activity.predecessor

        row_lookup = {}
        for index, activity in enumerate(activity_rows):
            if not activity.start_date or not activity.end_date:
                continue
            duration_days = max((activity.end_date - activity.start_date).days + 1, 1)
            start_px = round((activity.start_date - timeline_start).days * px_per_day, 2)
            width_px = round(max(duration_days * px_per_day, 24), 2)
            finish_px = round(start_px + width_px, 2)
            progress = 100 if activity.status == "completed" else (55 if activity.status == "in_progress" else 10)
            row_center_y = round(index * row_height + (row_height / 2), 2)
            row_lookup[activity.pk] = {
                "start_px": start_px,
                "finish_px": finish_px,
                "center_y": row_center_y,
            }
            gantt_rows.append(
                {
                    "id": activity.pk,
                    "row_index": index,
                    "name": activity.name,
                    "status": activity.get_status_display(),
                    "owner": activity.assigned_to.get_full_name() if activity.assigned_to else "Sin responsable",
                    "start_date": activity.start_date,
                    "end_date": activity.end_date,
                    "offset_px": start_px,
                    "width_px": width_px,
                    "duration_days": duration_days,
                    "progress": progress,
                    "bar_class": (
                        "is-complete"
                        if activity.status == "completed"
                        else ("is-active" if activity.status == "in_progress" else "is-pending")
                    ),
                    "predecessor": activity.predecessor.name if activity.predecessor else "",
                    "predecessor_id": activity.predecessor_id,
                    "is_critical": activity.pk in critical_ids,
                }
            )

        timeline_height_px = max(len(gantt_rows) * row_height, row_height)

        for row in gantt_rows:
            predecessor_id = row["predecessor_id"]
            if predecessor_id and predecessor_id in row_lookup and row["id"] in row_lookup:
                source = row_lookup[predecessor_id]
                target = row_lookup[row["id"]]
                dependency_lines.append(
                    {
                        "path": (
                            f"M {source['finish_px']} {source['center_y']} "
                            f"L {source['finish_px'] + 18} {source['center_y']} "
                            f"L {source['finish_px'] + 18} {target['center_y']} "
                            f"L {max(target['start_px'] - 8, source['finish_px'] + 18)} {target['center_y']}"
                        ),
                        "is_critical": row["is_critical"] and predecessor_id in critical_ids,
                    }
                )

        for milestone in milestones:
            if not milestone.due_date:
                continue
            milestone_markers.append(
                {
                    "name": milestone.name,
                    "date": milestone.due_date,
                    "offset_px": round((milestone.due_date - timeline_start).days * px_per_day, 2),
                    "completed": milestone.completed,
                }
            )

    return render(
        request,
        "reports/gantt.html",
        {
            "project": project,
            "activities": activities,
            "milestones": milestones,
            "filters": filters,
            "gantt_rows": gantt_rows,
            "month_markers": month_markers,
            "week_markers": week_markers,
            "milestone_markers": milestone_markers,
            "dependency_lines": dependency_lines,
            "today_offset": today_offset,
            "timeline_width_px": timeline_width_px,
            "timeline_height_px": timeline_height_px,
            "timeline_start": timeline_start,
            "timeline_end": timeline_end,
        },
    )


@login_required
def progress_report(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    completed = activities.filter(status="completed").count()
    total = activities.count()
    progress = (completed / total * 100) if total > 0 else 0
    return render(
        request,
        "reports/progress_report.html",
        {"project": project, "progress": progress, "completed": completed, "total": total, "filters": filters},
    )


@login_required
def cost_report(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    total_cost = sum(activity.cost or 0 for activity in activities)
    return render(
        request,
        "reports/cost_report.html",
        {"project": project, "activities": activities, "total_cost": total_cost, "filters": filters},
    )


@login_required
def export_csv(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    return export_project_csv(project, activities)


@login_required
def status_report(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    completed = activities.filter(status="completed").count()
    total = activities.count()
    progress = (completed / total * 100) if total > 0 else 0

    planned_cost = sum(activity.cost or 0 for activity in activities)
    actual_cost = planned_cost + sum((resource.total_cost or 0) for activity in activities for resource in activity.resource_set.all())
    cost_difference = actual_cost - planned_cost

    today = date.today()
    planned_days = (project.end_date - project.start_date).days if project.end_date and project.start_date else 0
    actual_days = (today - project.start_date).days if project.start_date else 0
    time_difference = actual_days - planned_days

    activity_data = []
    for activity in activities:
        act_planned_days = (activity.end_date - activity.start_date).days if activity.end_date and activity.start_date else 0
        act_actual_days = (today - activity.start_date).days if activity.start_date else 0
        act_time_diff = act_actual_days - act_planned_days
        activity_data.append(
            {
                "name": activity.name,
                "status": activity.status,
                "progress": 100 if activity.status == "completed" else 0,
                "planned_cost": activity.cost or 0,
                "actual_cost": (activity.cost or 0) + sum(resource.total_cost or 0 for resource in activity.resource_set.all()),
                "cost_diff": sum(resource.total_cost or 0 for resource in activity.resource_set.all()),
                "planned_days": act_planned_days,
                "actual_days": act_actual_days,
                "time_diff": act_time_diff,
            }
        )

    return render(
        request,
        "reports/status_report.html",
        {
            "project": project,
            "progress": progress,
            "completed": completed,
            "total": total,
            "planned_cost": planned_cost,
            "actual_cost": actual_cost,
            "cost_difference": cost_difference,
            "planned_days": planned_days,
            "actual_days": actual_days,
            "time_difference": time_difference,
            "activities": activity_data,
            "filters": filters,
        },
    )


@login_required
def calendar_view(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)
    milestones = project.milestone_set.all()

    events = []
    for activity in activities:
        if activity.start_date:
            events.append(
                {
                    "title": f"Actividad: {activity.name}",
                    "start": activity.start_date.isoformat(),
                    "end": activity.end_date.isoformat() if activity.end_date else None,
                    "backgroundColor": "#007bff",
                    "borderColor": "#0056b3",
                }
            )
    for milestone in milestones:
        if milestone.due_date:
            events.append(
                {
                    "title": f"Hito: {milestone.name}",
                    "start": milestone.due_date.isoformat(),
                    "backgroundColor": "#dc3545",
                    "borderColor": "#a71d2a",
                }
            )

    return render(request, "reports/calendar.html", {"project": project, "events": json.dumps(events) if events else "[]", "filters": filters})


@login_required
def performance_graphs(request, project_id):
    project = _get_project_for_user(request.user, project_id)
    filters = parse_report_filters(request.GET)
    activities = _filter_activities(project, filters)

    status_data = {
        "pending": activities.filter(status="pending").count(),
        "in_progress": activities.filter(status="in_progress").count(),
        "completed": activities.filter(status="completed").count(),
    }
    cost_data = [float(activity.cost) if activity.cost else 0 for activity in activities]
    cost_labels = [activity.name for activity in activities]

    return render(
        request,
        "reports/performance_graphs.html",
        {"project": project, "status_data": status_data, "cost_data": json.dumps(cost_data), "cost_labels": json.dumps(cost_labels), "filters": filters},
    )
