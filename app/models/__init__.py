# models/__init__.py
from .salary import Salary  # Сначала импортировать Salary
from .role import Role
from .employee import Employee

__all__ = ['Employee', 'Role', 'Salary']