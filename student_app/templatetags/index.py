from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    if indexable[i]:
        return indexable[i]
    return ""
