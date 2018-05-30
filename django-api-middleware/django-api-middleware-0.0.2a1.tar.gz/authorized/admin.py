from django.contrib import admin
from authorized.models import Applications
# Register your models here.
@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'can_request')
