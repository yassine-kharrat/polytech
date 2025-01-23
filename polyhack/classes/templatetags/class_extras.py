from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    try:
        return round(value / arg)
    except (ValueError, ZeroDivisionError):
        return 0 