from django.contrib import admin
from .models import Seguimiento, CostPerformanceIndexCPI, EarnedValueEV, PlannedValuePV, ShedulePerformanceIndexSPI

# Register your models here.

admin.site.register(Seguimiento)
admin.site.register(CostPerformanceIndexCPI)
admin.site.register(EarnedValueEV)
admin.site.register(PlannedValuePV)
admin.site.register(ShedulePerformanceIndexSPI)

