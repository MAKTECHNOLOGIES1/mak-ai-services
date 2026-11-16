"""
Role definitions and access constants for Identity Service.
Matches roles defined in identity_service.roles database catalog.
"""

from enum import Enum


class SystemRole(str, Enum):
    ROLE_SUPER_ADMIN = "ROLE_SUPER_ADMIN"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_TECHNICAL_MANAGER = "ROLE_TECHNICAL_MANAGER"
    ROLE_MANAGER = "ROLE_MANAGER"
    ROLE_HOD = "ROLE_HOD"
    ROLE_SR_LEAD = "ROLE_SR_LEAD"
    ROLE_TRAINER = "ROLE_TRAINER"
    ROLE_FACULTY = "ROLE_FACULTY"
    ROLE_TPO = "ROLE_TPO"
    ROLE_STUDENT = "ROLE_STUDENT"


ROLE_HIERARCHY: dict[str, int] = {
    SystemRole.ROLE_SUPER_ADMIN: 100,
    SystemRole.ROLE_ADMIN: 90,
    SystemRole.ROLE_TECHNICAL_MANAGER: 80,
    SystemRole.ROLE_MANAGER: 75,
    SystemRole.ROLE_HOD: 70,
    SystemRole.ROLE_SR_LEAD: 65,
    SystemRole.ROLE_TRAINER: 60,
    SystemRole.ROLE_FACULTY: 50,
    SystemRole.ROLE_TPO: 50,
    SystemRole.ROLE_STUDENT: 10,
}

