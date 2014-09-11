from django.contrib import admin
from certificates.models import GeneratedCertificate


class GeneratedCertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_id', 'download_url', 'grade', 'status', 'name')
    search_fields = ('name', 'user__first_name', 'user__last_name', 'user__email',
        'course_id', 'status', 'key', 'download_url')

admin.site.register(GeneratedCertificate, GeneratedCertificateAdmin)
