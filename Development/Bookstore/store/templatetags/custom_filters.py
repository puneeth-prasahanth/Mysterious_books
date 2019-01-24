from django import template

register=template.Library()

@register.filter(name='to_paise')
def to_paise(value):
    return value*1000

@register.filter(name='pluralize')
def pluralize(value):
    retval=""
    if value >1:
        retval="s"
    return value*1000
