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

    def __str__(self):
        if self.duration is None:
            time = str(self.started)
        else:
            time = "%s @ %s" % (self.duration, self.started)
        return "%s %s %s (%s) %s" % (self.user, self.method, self.path, time, self.status or '-')

    def __unicode__(self):
        return self.__str__()


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

    @property
    def instance_url(self):
        from slumber.server import get_slumber_root
        from slumber._caches import DATABASE_TABLE_TO_SLUMBER_MODEL
        slumber_model = DATABASE_TABLE_TO_SLUMBER_MODEL[self.table]
        pk_name = slumber_model.model._meta.pk.name
        pk = self.new[pk_name] if self.new else self.old[pk_name]
        return get_slumber_root() + slumber_model.path + 'data/{}/'.format(pk)

    def __str__(self):
        if self.request:
            if self.request.user:
                request = u"%s - %s %s" % (self.request.id, self.request.user, self.request.method)
            else:
                request = u"%s - %s" % (self.request.id, self.request.method)
            return u"%s %s @ %s (%s)" % (OPERATION_TYPE[self.type], self.table, self.when, request)
        else:
            return u"%s %s @ %s" % (OPERATION_TYPE[self.type], self.table, self.when)

    def __unicode__(self):
        return self.__str__()


class ChangeSubscription(models.Model):
    callback = models.CharField(max_length=128)
    callback_kwargs = models.CharField(max_length=1024)
    table = models.CharField(max_length=64)
    update_log_model_url = models.CharField(max_length=1024)

    def __str__(self):
        return 'callback: {}, table: {}, update_log_model_url: {}'.format(
            self.callback,
            self.table,
            self.update_log_model_url
        )

    def __unicode__(self):
        return self.__str__()
