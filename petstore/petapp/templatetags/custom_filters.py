from django import template

register = template.Library()

@register.filter
def urlencode_without_page(querydict):
    """Return the query string without the 'page' parameter."""
    querydict = querydict.copy()
    querydict.pop('page', None)  # Remove 'page' if it exists
    return querydict.urlencode()
