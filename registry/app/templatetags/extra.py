from django import template

register = template.Library()

@register.simple_tag(takes_context = True)
def url_replace(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.filter(name='times') 
def times(number):
    return range(1,number+1)