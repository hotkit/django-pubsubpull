"""
    Models.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from pubsubpull.fields import JSONB


class Request(models.Model):
    """A web request.
    """
    user = models.ForeignKey(User, null=True, blank=True,
        related_name='requests')


class UpdateLog(models.Model):
    """Store a change to a single row in a table.
    """
    table = models.CharField(max_length=200)
    when = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(Request, null=True, blank=True,
        related_name='changes')
    old = JSONB(null=True, blank=True)
    new = JSONB(null=True, blank=True)

    def save(self, **kw):
        raise ValidationError("Instances of this class cannot be using Django")

    def __unicode__(self):
        if self.old and self.new:
            type = "UPDATE"
        elif self.old:
            type = "DELETE"
        else:
            type = "INSERT"
        return u"%s %s @ %s" % (type, self.table, self.when)
