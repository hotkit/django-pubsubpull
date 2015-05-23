"""
    Models.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from pubsubpull.fields import JSONB


class Request(models.Model):
    """A web request.
    """
    user = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        null=True, blank=True, related_name='requests')
    method = models.CharField(max_length=20)
    path = models.TextField()
    started = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        if self.duration is None:
            time = str(self.started)
        else:
            time = "%s @ %s" % (self.duration, self.started)
        return "%s %s %s (%s) %s" % (self.user, self.method, self.path, time, self.status or '-')


OPERATION_TYPE = dict(I="INSERT", U="UPDATE", D="DELETE", T="TRUNCATE")

class UpdateLog(models.Model):
    """Store a change to a single row in a table.
    """
    table = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=OPERATION_TYPE.items())
    when = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(Request, null=True, blank=True,
        related_name='changes')
    old = JSONB(null=True, blank=True)
    new = JSONB(null=True, blank=True)

    def save(self, **kw):
        raise ValidationError("Instances of this class cannot be using Django")

    def __unicode__(self):
        return u"%s %s @ %s" % (OPERATION_TYPE[self.type], self.table, self.when)
