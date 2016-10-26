"""
    Asynchronous jobs.
"""
from __future__ import absolute_import

from datetime import timedelta
from urlparse import urljoin

from async.api import schedule
from slumber.connector.api import get_model
from slumber.connector.ua import get

try:
    from django.utils import timezone
except ImportError:  # pragma: no cover
    from datetime import datetime as timezone


def pull_monitor(model_url, callback, delay=None, page_url=None, floor=0,
                 pull_priority=5, job_priority=5, callback_kwargs=None):
    """Used to look for instances that need to be pulled.

    This only works with models who use an auto-incremented primary key.
    """
    if callback_kwargs is None:
        callback_kwargs = {}
    if delay is None:
        delay = dict(minutes=1)
    if not page_url:
        model = get_model(model_url)
        instances_url = model._operations['instances']
    else:
        instances_url = page_url
    _, json = get(instances_url or page_url)
    latest, highest = None, floor
    for item in json['page']:
        highest = max(item['pk'], highest)
        latest = item['pk']
        if latest > floor:
            schedule(callback, args=[urljoin(instances_url, item['data'])],
                     kwargs=callback_kwargs, priority=job_priority)
    if 'next_page' in json and latest > floor:
        schedule('pubsubpull.async.pull_monitor', args=[model_url, callback],
                 kwargs=dict(callback_kwargs=callback_kwargs,
                             delay=delay, floor=floor, job_priority=job_priority,
                             page_url=urljoin(instances_url, json['next_page']),
                             pull_priority=pull_priority),
                 priority=pull_priority)
        print("Got another page to process", json['next_page'], floor)
    if not page_url and delay:
        run_after = timezone.now() + timedelta(**delay)
        schedule('pubsubpull.async.pull_monitor', args=[model_url, callback],
                 run_after=run_after, priority=pull_priority,
                 kwargs=dict(callback_kwargs=callback_kwargs,
                             delay=delay, floor=highest, job_priority=job_priority,
                             pull_priority=pull_priority))
        print("Looking for new instances above", highest)
