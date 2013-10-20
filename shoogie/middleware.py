import sys
import traceback
import warnings

from django         import http
from django.conf    import settings
from django.core    import exceptions
from django.views   import debug

from shoogie        import models

DEFAULT_IGNORES = (http.Http404, exceptions.PermissionDenied)

class ExceptionLoggingMiddleware(object):
    def __init__(self):
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

    def process_exception(self, request, exception):
        if settings.DEBUG:
            return
        exc_type, exc_val, tb = sys.exc_info()
        if issubclass(exc_type, self.ignores):
            return
        reporter = debug.ExceptionReporter(request, exc_type, exc_val, tb)
        user     = request.user
        if user.is_anonymous():
            user = None

        tb_desc = traceback.extract_tb(tb, 1)
        tb_file, tb_line_num, tb_function, tb_text = tb_desc[0]

        models.ServerError.objects.create(
                hostname        = request.get_host()[:64],
                request_method  = request.method[:10],
                request_path    = request.path[:1024],
                query_string    = request.META.get('QUERY_STRING',''),
                post_data       = repr(dict(request.POST)),
                cookie_data     = repr(request.COOKIES),
                session_id      = request.session.session_key[:64],
                session_data    = repr(dict(request.session.iteritems())),
                user            = user,
                exception_type  = exc_type.__name__[:128],
                exception_str   = str(exc_val),
                source_file     = tb_file[-256:],
                source_line_num = tb_line_num,
                source_function = tb_function[:128],
                source_text     = tb_text[:256],
                issue           = '',
                technical_response = reporter.get_traceback_html(),
            )

