"""
    Asynchronous jobs.
"""
from __future__ import absolute_import

from async.api import schedule
from datetime import timedelta
from slumber.connector.api import get_model
from slumber.connector.ua import get
from urlparse import urljoin


try:
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone


def pull_monitor(model_url, callback, delay=dict(minutes=1),
        page_url=None, floor=0, pull_priority=5, job_priority=5):
    """Used to look for instances that need to be pulled.

    This only works with models who use an auto-incremented primary key.
    """
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
            schedule(callback, args=[urljoin(instances_url, item['data'])], priority=job_priority)
    if json.has_key('next_page') and latest > floor:
        schedule('pubsubpull.async.pull_monitor', args=[model_url, callback],
            kwargs=dict(delay=delay, floor=floor,
                page_url=urljoin(instances_url, json['next_page']),
                pull_priority=pull_priority, job_priority=job_priority),
            priority=pull_priority)
        print("Got another page to process", json['next_page'], floor)
    if not page_url:
        run_after = timezone.now() + timedelta(**delay)
        schedule('pubsubpull.async.pull_monitor', run_after=run_after,
            args=[model_url, callback], kwargs=dict(delay=delay, floor=highest,
                pull_priority=pull_priority, job_priority=job_priority),
            priority=pull_priority)
        print("Looking for new instances above", highest)
