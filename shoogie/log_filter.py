"""This module contains a copy of the RequireDebugFalse logging filter
available in Django 1.4+ so that 1.3 users can still use it with shoogie
"""

import logging
from django.conf import settings

class RequireDebugFalse(logging.Filter):
    def filter(self, record):
        return not settings.DEBUG
