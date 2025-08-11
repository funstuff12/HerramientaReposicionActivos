from django import template
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

register = template.Library()

@register.filter
def is_overdue(fecha_limite):
    """
    Verifica si una fecha límite está vencida.
    Retorna True si la fecha es anterior a la fecha actual.
    """
    if not fecha_limite:
        return False
    
    # Obtener la fecha actual
    today = timezone.now().date()
    
    # Si fecha_limite es datetime, convertir a date
    if isinstance(fecha_limite, datetime):
        fecha_limite = fecha_limite.date()
    
    return fecha_limite < today

@register.filter
def sum_field(queryset, field_name):
    """
    Suma los valores de un campo específico en un queryset.
    Útil para calcular totales en templates.
    """
    if not queryset:
        return 0
    
    total = 0
    for item in queryset:
        try:
            # Obtener el valor del campo usando getattr
            value = getattr(item, field_name, 0)
            
            # Convertir a decimal o float si es necesario
            if value:
                if isinstance(value, str):
                    value = float(value)
                elif isinstance(value, Decimal):
                    value = float(value)
                
                total += value
        except (ValueError, TypeError, AttributeError):
            # Si hay error en la conversión, continuar
            continue
    
    return total

@register.filter
def pluralize_es(count, singular_plural):
    """
    Pluralización en español.
    Uso: {{ count|pluralize_es:"obligación,obligaciones" }}
    """
    if not singular_plural:
        return ""
    
    try:
        singular, plural = singular_plural.split(',')
        return singular if count == 1 else plural
    except ValueError:
        return singular_plural

@register.filter
def currency_format(value):
    """
    Formatea un valor como moneda colombiana.
    """
    if not value:
        return "$0"
    
    try:
        # Convertir a float si es necesario
        if isinstance(value, str):
            value = float(value)
        elif isinstance(value, Decimal):
            value = float(value)
        
        # Formatear con separadores de miles
        return "${:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

@register.filter
def days_until_due(fecha_limite):
    """
    Calcula los días restantes hasta la fecha límite.
    Retorna número positivo si faltan días, negativo si está vencido.
    """
    if not fecha_limite:
        return None
    
    today = timezone.now().date()
    
    # Si fecha_limite es datetime, convertir a date
    if isinstance(fecha_limite, datetime):
        fecha_limite = fecha_limite.date()
    
    delta = fecha_limite - today
    return delta.days

@register.filter
def get_status_color(estado):
    """
    Retorna la clase CSS apropiada para el estado.
    """
    status_colors = {
        'pendiente': 'status-pendiente',
        'pagado_parcial': 'status-pagado_parcial',
        'pagado_total': 'status-pagado_total',
    }
    return status_colors.get(estado, 'status-pendiente')

@register.filter
def percentage_paid(valor_pagado, valor_total):
    """
    Calcula el porcentaje pagado.
    """
    if not valor_total or valor_total == 0:
        return 0
    
    try:
        if isinstance(valor_pagado, str):
            valor_pagado = float(valor_pagado)
        if isinstance(valor_total, str):
            valor_total = float(valor_total)
        
        percentage = (valor_pagado / valor_total) * 100
        return round(percentage, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0