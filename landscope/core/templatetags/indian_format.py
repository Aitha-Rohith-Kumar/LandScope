from django import template

register = template.Library()

@register.filter
def indian_comma(value):
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        return value

    s = str(value)
    if len(s) <= 3:
        return s

    last3 = s[-3:]
    remaining = s[:-3]

    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    if remaining:
        parts.insert(0, remaining)

    return ",".join(parts) + "," + last3