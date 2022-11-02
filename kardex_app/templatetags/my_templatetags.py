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

@register.filter(name='get_by_idx')
def get_by_idx(els, idx):
    return els[idx]

# code adapted from and thanks to
# https://stackoverflow.com/a/3132818
@register.filter(name='list_iter')
def list_iter(lists):
    list_a, list_b, list_c = lists
    for x, y, z in zip(list_a, list_b, list_c):
        yield (x, y, z)

@register.filter(name='strip')
def trim(value):
    return value.strip()
