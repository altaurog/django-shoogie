import sys
import traceback

from django         import http
from django.conf    import settings
from django.views   import debug

from shoogie        import models

class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        if settings.DEBUG:
            return
        exc_type, exc_val, tb = sys.exc_info()
        if issubclass(exc_type, http.Http404):
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
                post_data       = request.raw_post_data,
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

