"""
A collection of tools and EOTasks for image co-registration
"""

from .coregistration import (
    RegistrationTask, InterpolationType, ECCRegistration, PointBasedRegistration, ThunderRegistration,
    ECCRegistrationTask, PointBasedRegistrationTask, ThunderRegistrationTask
)

__version__ = '1.0.0'
