"""Template filters for formatting dashboard values."""

from __future__ import annotations

from django import template

from ab_testing_platform import format_percentage

register = template.Library()


@register.filter
def percentage(value: any, digits: int = 2) -> str:
    if value is None or value == "":
        return "0.00%"
    try:
        return format_percentage(float(value), int(digits))
    except (ValueError, TypeError):
        return "0.00%"


@register.filter
def number(value: any, digits: int = 2) -> str:
    if value is None or value == "":
        return "0"
    try:
        if isinstance(value, int):
            return f"{value:,}"
        # If it's a float that is actually an integer
        val_float = float(value)
        if val_float.is_integer() and int(digits) == 0:
            return f"{int(val_float):,}"
        return f"{val_float:,.{int(digits)}f}"
    except (ValueError, TypeError):
        return "0"


@register.filter
def subtract(value: any, arg: any) -> float:
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def safe_divide(value: any, arg: any) -> float:
    try:
        denom = float(arg)
        if abs(denom) < 1e-12:
            return 0.0
        return float(value) / denom
    except (ValueError, TypeError):
        return 0.0
