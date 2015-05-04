"""
    Asynchronous jobs.
"""
from __future__ import absolute_import

from async.api import schedule
from datetime import timedelta


try:
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone


def pull_monitor(model, callback, delay=dict(minutes=1)):
    """Used to look for instances that need to be pulled.
    """
    run_after = timezone.now() + timedelta(**delay)
    schedule('pubsubpull.async.pull_monitor', run_after=run_after, args=[model, callback])
