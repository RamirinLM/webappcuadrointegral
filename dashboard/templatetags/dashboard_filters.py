# dashboard/templatetags/dashboard_filters.py
from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def currency(value):
    """Formatear valor como moneda"""
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"

@register.filter
def progress_color(value):
    """Determinar color basado en porcentaje de progreso"""
    if value >= 80:
        return "success"
    elif value >= 50:
        return "warning"
    else:
        return "danger"

@register.filter
def estado_badge(estado):
    """Crear badge para estado del proyecto"""
    colores = {
        0: ('primary', 'Iniciado'),
        1: ('warning', 'En Progreso'),
        2: ('success', 'Completado'),
        3: ('danger', 'Cancelado'),
    }
    
    color, texto = colores.get(estado, ('secondary', 'Desconocido'))
    return format_html('<span class="badge bg-{}">{}</span>', color, texto)

@register.filter
def cpi_color(valor):
    """Color para valores CPI"""
    if valor >= 1:
        return "success"
    elif valor >= 0.9:
        return "warning"
    else:
        return "danger"

@register.filter
def spi_color(valor):
    """Color para valores SPI"""
    if valor >= 1:
        return "success"
    elif valor >= 0.9:
        return "warning"
    else:
        return "danger"