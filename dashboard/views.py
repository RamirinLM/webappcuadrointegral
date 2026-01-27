# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestionproyecto.models import Proyecto, Interesado, Riesgo
from lineabase.models import Cronograma, Actividad
from seguimiento.models import Seguimiento, CostPerformanceIndexCPI, ShedulePerformanceIndexSPI
from django.utils import timezone
from datetime import timedelta

#@login_required
def dashboard_principal(request):
    """Vista principal del dashboard con todas las métricas"""
    
    # 1. Métricas básicas de proyectos
    total_proyectos = Proyecto.objects.count()
    proyectos_activos = Proyecto.objects.filter(estado__in=[0, 1]).count()
    proyectos_completados = Proyecto.objects.filter(estado=2).count()
    
    # Distribución por estado
    proyectos_por_estado = {
        'Iniciado': Proyecto.objects.filter(estado=0).count(),
        'En Progreso': Proyecto.objects.filter(estado=1).count(),
        'Completado': Proyecto.objects.filter(estado=2).count(),
        'Cancelado': Proyecto.objects.filter(estado=3).count(),
    }
    
    # 2. Métricas financieras
    cronogramas = Cronograma.objects.all()
    costo_total_estimado = sum(c.costoEstimado for c in cronogramas) if cronogramas else 0
    costo_total_real = sum(c.costoRealTotal for c in cronogramas) if cronogramas else 0
    
    # 3. Actividades recientes (últimas 10)
    actividades_recientes = Actividad.objects.order_by('-fechaInicio')[:10]
    
    # 4. Índices de rendimiento (últimos registros)
    ultimos_cpi = CostPerformanceIndexCPI.objects.order_by('-fecha')[:5]
    ultimos_spi = ShedulePerformanceIndexSPI.objects.order_by('-fecha')[:5]
    
    # 5. Proyectos con posibles problemas
    proyectos_con_problemas = obtener_proyectos_con_problemas()
    
    # 6. Proyectos próximos a vencer (próximos 7 días)
    hoy = timezone.now().date()
    proyectos_proximos_vencer = Proyecto.objects.filter(
        fecha_fin__range=[hoy, hoy + timedelta(days=7)],
        estado__in=[0, 1]
    )
    
    context = {
        'total_proyectos': total_proyectos,
        'proyectos_activos': proyectos_activos,
        'proyectos_completados': proyectos_completados,
        'proyectos_por_estado': proyectos_por_estado,
        'costo_total_estimado': costo_total_estimado,
        'costo_total_real': costo_total_real,
        'diferencia_costo': costo_total_estimado - costo_total_real,
        'actividades_recientes': actividades_recientes,
        'ultimos_cpi': ultimos_cpi,
        'ultimos_spi': ultimos_spi,
        'proyectos_con_problemas': proyectos_con_problemas[:5],
        'proyectos_proximos_vencer': proyectos_proximos_vencer,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

#@login_required
def dashboard_proyectos(request):
    """Vista específica para métricas de proyectos"""
    proyectos = Proyecto.objects.all()
    
    # Estadísticas adicionales
    proyectos_por_mes = {}
    for proyecto in proyectos:
        mes = proyecto.fecha_creacion.strftime('%Y-%m')
        proyectos_por_mes[mes] = proyectos_por_mes.get(mes, 0) + 1
    
    context = {
        'proyectos': proyectos,
        'proyectos_por_mes': proyectos_por_mes,
        'total_interesados': Interesado.objects.count(),
        'total_riesgos': Riesgo.objects.count(),
    }
    
    return render(request, 'dashboard/proyectos.html', context)

#@login_required
def dashboard_financiero(request):
    """Vista específica para métricas financieras"""
    cronogramas = Cronograma.objects.all()
    actividades = Actividad.objects.all()
    
    # Cálculos financieros
    if cronogramas:
        costo_promedio_estimado = sum(c.costoEstimado for c in cronogramas) / len(cronogramas)
        costo_promedio_real = sum(c.costoRealTotal for c in cronogramas) / len(cronogramas)
    else:
        costo_promedio_estimado = costo_promedio_real = 0
    
    context = {
        'cronogramas': cronogramas,
        'total_actividades': actividades.count(),
        'costo_promedio_estimado': costo_promedio_estimado,
        'costo_promedio_real': costo_promedio_real,
        'actividades_completadas': actividades.filter(estado=2).count(),
        'actividades_en_progreso': actividades.filter(estado=1).count(),
    }
    
    return render(request, 'dashboard/financiero.html', context)

def obtener_proyectos_con_problemas():
    """Función auxiliar para identificar proyectos con problemas"""
    proyectos_con_problemas = []
    
    for proyecto in Proyecto.objects.filter(estado__in=[0, 1]):  # Solo activos
        ultimo_seguimiento = Seguimiento.objects.filter(proyecto=proyecto).order_by('-fecha').first()
        
        if ultimo_seguimiento:
            cpi = CostPerformanceIndexCPI.objects.filter(seguimiento=ultimo_seguimiento).first()
            spi = ShedulePerformanceIndexSPI.objects.filter(seguimiento=ultimo_seguimiento).first()
            
            problema = False
            razon = []
            
            if cpi and cpi.valorCPI < 1:
                problema = True
                razon.append(f"CPI bajo ({cpi.valorCPI:.2f})")
            
            if spi and spi.valor < 0.9:
                problema = True
                razon.append(f"SPI bajo ({spi.valor:.2f})")
            
            if problema:
                proyectos_con_problemas.append({
                    'proyecto': proyecto,
                    'cpi': cpi.valorCPI if cpi else None,
                    'spi': spi.valor if spi else None,
                    'razones': ', '.join(razon),
                    'ultimo_seguimiento': ultimo_seguimiento.fecha
                })
    
    return proyectos_con_problemas