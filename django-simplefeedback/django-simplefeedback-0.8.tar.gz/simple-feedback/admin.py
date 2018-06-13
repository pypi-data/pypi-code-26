from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_filter = ['status']
    list_display = ['subject', 'created', 'status', 'assignee']
    readonly_fields = ['user', 'email', 'subject', 'text', 'download_meta_btn']
    search_fields = ['subject']
    exclude = ('meta',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(TicketAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'assignee':
            field.label_from_instance = lambda u: '{} <{}>'.format(u.get_full_name(), u.email)
        return field

    def has_module_permission(self, request):
        """ Only available to superusers """
        return request.user.is_superuser

    def download_meta_btn(self, obj):
        markup = '<a href="/api/tickets/{}/meta/">Download Meta JSON </a>'.format(obj.id)
        return mark_safe(markup)
    download_meta_btn.short_description = 'Meta'


admin.site.register(Ticket, TicketAdmin)
