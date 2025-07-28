from django import template

register = template.Library()

@register.filter
def round_to(value, decimal_places=0):
    if value is not None:
        return round(value, decimal_places)
    return value