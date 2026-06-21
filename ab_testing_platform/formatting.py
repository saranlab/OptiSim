"""Formatting helpers for examples and reports."""


def format_percentage(value: float, digits: int = 2) -> str:
    """Format a decimal rate as a percentage string."""

    return f"{100.0 * value:.{digits}f}%"
