django-shoogie
=================

Shoogie is a small django application with middleware that logs exceptions
to a table in the database, along with django's standard HTML debug
response.  It is intended to be a lightweight alternative to
`django-sentry`_, inspired by `this answer on stackoverflow`_.  

The logging middleware doesn't do anything when running in ``DEBUG`` mode.

Shoogie has been used in production since March 2012.

The name Shoogie is a diminutive of the Hebrew word *sh'giah* (שגיאה), which means
'error.'  It also happens to be the name of a popular kids' candy snack in
Israel.  It's our hope that django-shoogie will make dealing with server errors a
sweeter experience.

.. _this answer on stackoverflow: http://stackoverflow.com/questions/7130985/#answer-7579467

Key Features
--------------
* Simple, server-error specific logging
* Logs django's familiar technical 500 response
* Uses django's standard admin interface
* Easy retrieval by user, exception, file, function
* Easy extraction of users' email addresses
* Middleware can easily be placed outside transaction management
* Configurable exception ignores
* Configurable traceback filtering

Version Compatibility
---------------------

django-shoogie is compatible with Django versions 1.3 to 1.6

Installation 
------------

To install shoogie::

    pip install django-shoogie

To use shoogie in a django project, add it to the ``INSTALLED_APPS`` and
add the shoogie middleware to ``MIDDLEWARE_CLASSES`` in your ``settings.py``.
Be sure to put the middleware *above* the transaction middleware, 
or errors which cause the DB transaction to be rolled back will not be
logged.  The ``django.contrib.admin`` app must also be installed to view
the errors logged via django's admin interface::

    MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'shoogie.middleware.ExceptionLoggingMiddleware',        # <---
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.transaction.TransactionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            # ...
        )

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'shoogie',                      # <---
        # ...
    )

Make sure to run ``syncdb`` after adding shoogie to create the
``shoogie_servererror`` table.

Configuration
---------------

Shoogie can be configured with the following settings:

settings.SHOOGIE_IGNORE_EXCEPTIONS
'''''''''''''''''''''''''''''''''''
A sequence of absolute dotted paths of exceptions which it should not log.
These exceptions and their subclasses will be ignored.
The default value is::

    SHOOGIE_IGNORE_EXCEPTIONS = (
        'django.http.Http404',
        'django.exceptions.PermissionDenied',
    )

settings.SHOOGIE_TRACEBACK_EXCLUDE
''''''''''''''''''''''''''''''''''''
A sequence of regular expression pairs (filename, funcname) used to filter
the traceback included in django's debug page.  This is intended to
eliminate the time needed to render, store, and display traceback frames
which aren't useful.  The default value is::

    SHOOGIE_TRACEBACK_EXCLUDE = (
        ('/django/core/handlers/base.py$', '^get_response$'),
        ('/django/template/', 'render'),
    )

Use
----

Errors logged by shoogie can be viewed via django's admin interface at
``/admin/shoogie/servererror/``.

To view the data fields stored in the log entry, click in the first column.

To visit the url in which the error occurred, click the 'path' column.
This won't work if the host is inaccessible, if the request method was
something other than GET, or if the path isn't really an HTTP request path
(see below).

If a user is logged with an entry, a link to the admin detail page for the
user will be displayed in the admin list.

Click the 'debug' link to view the django-generated 'technical response'
(debug page) for the exception.

To get a list of users and email addresses who encountered a set of errors,
select the log entries using the checkboxes on the left, then select "Get
user email addresses for selected errors" from the 'Action' drop-down menu
and click the 'Go' button.

To mark a set of errors as resolved or as not resolved, select the entries
in question and pick the appropriate action from the drop-down as above.

API
---

Shoogie can also be used to log exceptions directly.  This could be useful
for exceptions occurring in back-end processes such as long-running
calculations, cron-jobs, and celery workers::

    from shoogie import logger
    logger.log_exception([request, [exc_type, exc_val, tb]])

Logs an exception to the db.  If ``exc_type``, ``exc_val``, and ``tb``
aren't supplied, they will be retrieved using ``sys.exc_info()``.
The django technical debug page stored will display the traceback as with
errors occuring in normal views.

If ``request`` is given, whatever request information is present will also
be saved in the log entry.  ``request`` should be an object which implements,
partially or wholly, the same interface as a ``django.http.HttpRequest``.

As a convenience for logging exceptions outside the context of an HTTP
request, ``log_exception`` can be passed a string instead, which will be
logged as the request path.  Make sure the logging is done outside any
transaction which might be reversed by the exception being logged.  A
general pattern as follows is recommended::

    try:
        with transaction.commit_on_success():
            "insert your processing here"
    except:
        logger.log_exception('Description')

Related Projects
-----------------

`django-sentry`_ is a large, very full-featured multi-platform error logging server,
which is based on django, and which offers prepackaged integration with
many other platforms.  It offers some advanced features including aggregation of similar
exceptions, graphs, a fully web-2.0 real-time AJAX interface, and much more.

raven_ is the python logging client for django-sentry.

`django-erroneous`_ is a very simple logging system, similar in scope to
django-shoogie.  It uses django signals rather than middleware to capture
exceptions.

`django-logdb`_ provides a handler for python's logging_ module which
stores log messages in the db.  It includes middleware for exception logging. 
It also provides aggregation and some of the features offered by django-sentry.


.. _django-sentry: http://pypi.python.org/pypi/django-sentry
.. _raven: http://pypi.python.org/pypi/raven
.. _django-erroneous: http://pypi.python.org/pypi/django-erroneous
.. _django-logdb: http://pypi.python.org/pypi/django-logdb
.. _logging: http://docs.python.org/2/library/logging.html
