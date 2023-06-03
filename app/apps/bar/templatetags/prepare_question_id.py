from django import template

register = template.Library()


@register.filter
def prepare_id(value):
    return value + 1
