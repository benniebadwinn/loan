from django import template

register = template.Library()

@register.filter(name='range')
def range_filter(number):
    return range(number)

@register.simple_tag
def generate_years(start_year, end_year):
    return range(start_year, end_year - 1, -1)
