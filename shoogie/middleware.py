import sys
import warnings

from django         import http
from django.conf    import settings
from django.core    import exceptions

from . import logger

DEFAULT_IGNORES = (http.Http404, exceptions.PermissionDenied)

class ExceptionLoggingMiddleware(object):
    def __init__(self):
        if settings.DEBUG:
            raise exceptions.MiddlewareNotUsed
        ignores = getattr(settings, 'SHOOGIE_IGNORE_EXCEPTIONS', None)
        if ignores:
            self.ignores = []
            for exception_path in ignores:
                try:
                    mod, exc = exception_path.rsplit('.', 1)
                    __import__(mod)
                    ignore_mod = sys.modules[mod]
                    ignore_exc = getattr(ignore_mod, exc)
                    self.ignores.append(ignore_exc)
                except (ValueError, ImportError, AttributeError):
                    warnings.warn("Unable to import exception: %s" % exception_path)
        else:
            self.ignores = DEFAULT_IGNORES

    def process_exception(self, request, _):
        exc_type, exc_val, tb = sys.exc_info()
        if issubclass(exc_type, self.ignores):
            return
        logger.log_exception(request, exc_type, exc_val, tb)
