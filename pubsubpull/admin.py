"""
    Enable admin
"""
from django.contrib import admin
from pubsubpull.models import Request, UpdateLog


admin.site.register(Request)

class UpdateLogAdmin(admin.ModelAdmin):
     raw_id_fields = ['request']
admin.site.register(UpdateLog, UpdateLogAdmin)
