from django.contrib import admin

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin


class FunTokenAdmin(TokenAdmin):
    raw_id_fields = ('user',)


admin.site.unregister(Token)
admin.site.register(Token, FunTokenAdmin)
