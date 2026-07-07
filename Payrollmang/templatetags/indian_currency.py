from django import template

register = template.Library()

@register.filter
def indian_currency(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    number = f"{value:.2f}"
    integer, decimal = number.split(".")

    if len(integer) <= 3:
        return f"₹ {integer}.{decimal}"

    last3 = integer[-3:]
    remaining = integer[:-3]

    parts = []

    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    if remaining:
        parts.insert(0, remaining)

    integer = ",".join(parts) + "," + last3

    return f"₹ {integer}.{decimal}"