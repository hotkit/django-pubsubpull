"""
    Asynchronous jobs.
"""
from __future__ import absolute_import

from async.api import schedule
from datetime import timedelta
from slumber.connector.api import get_model
from slumber.connector.ua import get


try:
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone


def pull_monitor(model_url, callback, delay=dict(minutes=1)):
    """Used to look for instances that need to be pulled.
    """
    model = get_model(model_url)
    _, json = get(model._operations['instances'])
    for item in json['page']:
        schedule(callback, args=[item['data']])
    run_after = timezone.now() + timedelta(**delay)
    schedule('pubsubpull.async.pull_monitor', run_after=run_after, args=[model_url, callback])
