from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from shoogie import models, views

class ServerErrorAdmin(admin.ModelAdmin):
    list_display = ('exception_type', 'exception_str', 'path_link', 'error_date_format', 'user', 'technicalresponse_link', 'resolved',)
    list_display_links = ('exception_type', 'exception_str',)
    date_hierarchy = 'datestamp'
    search_fields  = ('request_path', 'exception_type', 'exception_str', 'source_file', 'source_function', 'source_text')
    actions = ('get_email_list', 'resolve_servererror', 'unresolve_servererror')

    exclude = ('technical_response',)
    readonly_fields = (
            'datestamp',
            'hostname',
            'request_method',
            'request_path',
            'query_string',
            'post_data',
            'cookie_data',
            'session_id',
            'session_data',
            'user',
            'exception_type',
            'exception_str',
            'source_file',
            'source_line_num',
            'source_function',
            'source_text',
        )

    def error_date_format(self, instance):
        return instance.datestamp.strftime('%Y-%b-%d %H:%M')
    error_date_format.admin_order_field = 'datestamp'

    def path_link(self, instance):
        url = 'http://%s%s?%s' % (instance.hostname, instance.request_path, instance.query_string)
        return '<a href="{0}" title="{0}">{1}</a>'.format(url, instance.request_path)
    path_link.allow_tags = True
    path_link.short_description = 'path'

    def get_email_list(self, request, queryset):
        content = queryset.values_list('user__email', flat=True).distinct()
        return HttpResponse(',\n'.join(content), mimetype='text/plain')
    get_email_list.short_description = 'Get user email addresses for selected errors'

    def technicalresponse_link(self, instance):
        tr_url = reverse('admin:shoogie_technicalresponse', kwargs={'pk':instance.pk})
        return '<a href="%s"><b>debug</b></a>' % tr_url
    technicalresponse_link.allow_tags = True
    technicalresponse_link.short_description = 'Debug'

    def resolve_servererror(self, request, queryset):
        update_count = queryset.update(resolved=True)
        plural = 's' if update_count != 1 else ''
        self.message_user(request, "Marked %d error%s as resolved" % (update_count, plural))
    resolve_servererror.short_description = "Mark selected errors as resolved"

    def unresolve_servererror(self, request, queryset):
        update_count = queryset.update(resolved=False)
        plural = 's' if update_count != 1 else ''
        self.message_user(request, "Marked %d error%s as not resolved" % (update_count, plural))
    unresolve_servererror.short_description = "Mark selected errors as NOT resolved"

    def get_urls(self):
        myview = views.TechnicalResponseView.as_view()
        myurls = patterns('',
            url(r'(?P<pk>\d+)/technicalresponse/$',
                self.admin_site.admin_view(myview, cacheable=True),
                name='shoogie_technicalresponse',
            ),
        )
        return myurls + super(ServerErrorAdmin, self).get_urls()

admin.site.register(models.ServerError, ServerErrorAdmin)
