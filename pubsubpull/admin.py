"""
    Enable admin
"""
from django.contrib import admin
from pubsubpull.models import Request, UpdateLog


admin.site.register(Request)
admin.site.register(UpdateLog)
