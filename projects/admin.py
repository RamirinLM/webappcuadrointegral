from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Project, Activity, Milestone, Seguimiento, Notification,
    ChangeRequest, ActaConstitucion, Alcance, Comunicacion,
    Baseline, Acquisition, UserProfile, ActivityAssignment,
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil de Usuario'
    verbose_name_plural = 'Perfiles de Usuario'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'get_role')

    def get_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else '-'
    get_role.short_description = 'Rol'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'budget', 'start_date', 'end_date', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'cost', 'start_date', 'end_date')
    list_filter = ('status', 'project')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    raw_id_fields = ('project', 'assigned_to', 'predecessor')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'phase', 'due_date', 'completed')
    list_filter = ('phase', 'completed')
    search_fields = ('name', 'description')
    raw_id_fields = ('project',)


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'fecha', 'pv', 'ev', 'ac', 'sv', 'cv', 'cpi', 'spi')
    list_filter = ('fecha', 'proyecto')
    date_hierarchy = 'fecha'
    readonly_fields = ('pv', 'ev', 'ac', 'sv', 'cv', 'cpi', 'spi')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'project', 'recipient', 'sent', 'created_at')
    list_filter = ('alert_type', 'sent')
    search_fields = ('message',)
    date_hierarchy = 'created_at'


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'requested_by', 'approved_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('description', 'justification')
    date_hierarchy = 'created_at'


@admin.register(ActaConstitucion)
class ActaConstitucionAdmin(admin.ModelAdmin):
    list_display = ('proyecto',)
    search_fields = ('proyecto__name', 'alcance', 'objetivos')
    raw_id_fields = ('proyecto',)


@admin.register(Alcance)
class AlcanceAdmin(admin.ModelAdmin):
    list_display = ('proyecto',)
    search_fields = ('proyecto__name', 'descripcion', 'objetivos')
    raw_id_fields = ('proyecto',)


@admin.register(Baseline)
class BaselineAdmin(admin.ModelAdmin):
    list_display = ('project', 'cost_baseline', 'created_at')
    raw_id_fields = ('project',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Acquisition)
class AcquisitionAdmin(admin.ModelAdmin):
    list_display = ('item', 'project', 'status', 'estimated_cost', 'actual_cost', 'delivery_date')
    list_filter = ('status',)
    search_fields = ('item', 'description')
    raw_id_fields = ('project',)


@admin.register(ActivityAssignment)
class ActivityAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'role', 'hours_assigned', 'created_at')
    list_filter = ('role',)
    raw_id_fields = ('activity', 'user')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

