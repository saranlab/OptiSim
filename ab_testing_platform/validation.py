"""Input validation helpers and domain-specific errors."""


class ValidationError(ValueError):
    """Raised when invalid experiment parameters are provided."""


def validate_probability(value: float, name: str, *, inclusive: bool = True) -> None:
    """Validate that a value is a probability."""

    if inclusive:
        valid = 0.0 <= value <= 1.0
        interval = "[0, 1]"
    else:
        valid = 0.0 < value < 1.0
        interval = "(0, 1)"

    if not valid:
        raise ValidationError(f"{name} must be in {interval}; received {value}.")


def validate_count_data(conversions: int, sample_size: int, label: str) -> None:
    """Validate conversion count data for one experiment variation."""

    if sample_size <= 0:
        raise ValidationError(f"sample_size_{label} must be positive.")
    if conversions < 0:
        raise ValidationError(f"conversions_{label} cannot be negative.")
    if conversions > sample_size:
        raise ValidationError(f"conversions_{label} cannot exceed sample_size_{label}.")
