# crm/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def get_dynamic_field(obj, field_name):
    return getattr(obj, field_name, {})



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 'N/A')


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else None

@register.filter
def make_range(value):
    try:
        return range(int(value))
    except:
        return range(0)
    

@register.simple_tag
def get_key_value(dict_data, base, index):
    key = f"{base}-{index}"
    return dict_data.get(key, '')


@register.filter(name='replace')
def replace(value, arg):
    old, new = arg.split(',')
    return value.replace(old, new)