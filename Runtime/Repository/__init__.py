"""Repository-only engines for governed project entities."""

from .case_repository import CaseRepository, CaseRepositoryError, CaseValidationError

__all__ = [
    "CaseRepository",
    "CaseRepositoryError",
    "CaseValidationError",
    "validate_all",
]


def validate_all(*args, **kwargs):
    """Run global validation without eagerly importing the CLI module."""
    from .global_validator import validate_all as run_validation

    return run_validation(*args, **kwargs)
