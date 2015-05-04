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


def pull_monitor(model, callback):
    """Used to look for instances that need to be pulled.
    """
    now = timezone.now()
    later = now + timedelta(minutes=1)
    schedule('pubsubpull.async.pull_monitor', run_after=later, args=[model, callback])
