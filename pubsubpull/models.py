"""
    Models.
"""
from django.core.exceptions import ValidationError
from django.db import models


class UpdateLog(models.Model):
    table = models.CharField(max_length=200)
    when = models.DateTimeField(auto_now_add=True)

    def save(self, **kw):
        raise ValidationError("Instances of this class cannot be using Django")
