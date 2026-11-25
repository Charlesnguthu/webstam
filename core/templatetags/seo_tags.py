import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def jsonld(value):
    data = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(data)
