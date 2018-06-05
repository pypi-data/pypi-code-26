from django.contrib import admin

from signoff.models import Document, DocumentConsent


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(DocumentConsent)
class DocumentConsentAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'user',
    )
