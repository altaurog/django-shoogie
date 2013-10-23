import socket
import sys
import traceback

from django         import http
from django.views   import debug

from . import models, utils


def log_exception(request, exc_type=None, exc_val=None, tb=None):
    django_request = None
    if isinstance(request, http.HttpRequest):
        django_request = request

    if tb is None:
        exc_type, exc_val, tb = sys.exc_info()

    reporter = debug.ExceptionReporter(django_request, exc_type, exc_val, tb)

    tb_desc = traceback.extract_tb(tb, 1)
    tb_file, tb_line_num, tb_function, tb_text = tb_desc[0]

    data = {}
    if request is not None:
        data = request_data(request)
    
    data.update({
        'exception_type' : exc_type.__name__,
        'exception_str'  : str(exc_val),
        'source_file'    : utils.TruncateBeginning(tb_file),
        'source_line_num': tb_line_num,
        'source_function': tb_function,
        'source_text'    : tb_text,
    })

    kwargs = utils.clean_data_for_insert(data, models.ServerError)
    models.ServerError.objects.create(
            issue           = '',
            technical_response = reporter.get_traceback_html(),
            **kwargs
        )

def request_data(request):
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

