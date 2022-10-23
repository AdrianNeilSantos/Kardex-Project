from django import template

register = template.Library()
@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)

@register.filter(name='split')
def split_string(string, split_by):
    return string.split(split_by)

@register.filter(name='replace_with_underscores')
def replace_string_with_underscores(string, replace_with):
    return string.replace(replace_with, '_')

@register.filter(name='map')
def map_list(a, b):
    return map(a, b)

@register.filter(name='lowerfirst')
def lowerfirst(string):
    return string[0].lower() + string[1:]

@register.filter(name='is_instance')
def is_instance(obj, data_type):
    return isinstance(obj, data_type)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
