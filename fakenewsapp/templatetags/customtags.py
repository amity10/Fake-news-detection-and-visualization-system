from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get dictionary item in templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0
