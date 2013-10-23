import socket
import sys
import traceback
import warnings

from django         import http
from django.conf    import settings
from django.core    import exceptions
from django.db.models import fields
from django.utils   import encoding
from django.views   import debug

from shoogie        import models

DEFAULT_IGNORES = (http.Http404, exceptions.PermissionDenied)

class TruncateBeginning(unicode):
    "Mark string for truncation at beginning"

def truncate(strval, max_length, at_beginning=None):
    strval = encoding.force_unicode(strval)
    if len(strval) <= max_length:
        return strval
    if at_beginning is None and isinstance(strval, TruncateBeginning):
        at_end = False
    else:
        at_end = not(at_beginning)

    if at_end:
        return strval[:max_length - 3] + u'...'
    else:
        return u'...' + strval[-max_length + 3:]


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

        django_request = None
        if isinstance(request, http.HttpRequest):
            django_request = request
        reporter = debug.ExceptionReporter(django_request, exc_type, exc_val, tb)

        tb_desc = traceback.extract_tb(tb, 1)
        tb_file, tb_line_num, tb_function, tb_text = tb_desc[0]

        data = {}
        if request is not None:
            data = self.request_data(request)
        
        data.update({
            'exception_type' : exc_type.__name__,
            'exception_str'  : str(exc_val),
            'source_file'    : TruncateBeginning(tb_file),
            'source_line_num': tb_line_num,
            'source_function': tb_function,
            'source_text'    : tb_text,
        })

        kwargs = self.clean_data_for_insert(data, models.ServerError)
        models.ServerError.objects.create(
                issue           = '',
                technical_response = reporter.get_traceback_html(),
                **kwargs
            )

    def request_data(self, request):
        """
        Get data out of the request object.  Assume nothing
        """
        # Allow a string for convenience
        if isinstance(request, basestring):
            return {'request_path': request}

        data = {}
        try:
            data['hostname'] = request.get_host()
        except:
            data['hostname'] = socket.getfqdn()

        data['request_method'] = getattr(request, 'method', '')
        data['request_path'] = getattr(request, 'path', '')

        try:
            data['query_string'] = request.META.get('QUERY_STRING', '')
        except:
            data['query_string'] = ''

        try:
            data['post_data'] = dict(request.POST)
        except:
            data['post_data'] = ''

        try:
            data['cookie_data'] = request.COOKIES
        except:
            data['cookie_data'] = ''

        try:
            data['session_id'] = request.session.session_key
        except:
            data['session_id'] = ''

        try:
            data['session_data'] = dict(request.session.iteritems())
        except:
            data['session_data'] = ''

        try:
            user = request.user
            if user.is_anonymous():
                user = None
        except:
            user = None

        data['user'] = user
        return data

    def clean_data_for_insert(self, data, model):
        """
        Make sure the data will fit in our fields
        """
        clean_data = {}
        for f in model._meta.local_fields:
            try:
                val = data[f.name]
            except KeyError:
                continue

            if isinstance(f, (fields.CharField, fields.TextField)):
                if val is not None:
                    if not isinstance(val, basestring):
                        val = repr(val)
                    if f.max_length is not None:
                        val = truncate(val, f.max_length)
            clean_data[f.name] = val
        return clean_data

