from django import template

register = template.Library()


@register.filter
def first_name(value):
    return value.split(' ')[1]


@register.filter
def last_name(value):
    return value.split(' ')[0]
