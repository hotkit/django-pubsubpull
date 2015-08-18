"""
    APIs exposed by pubsubpull.
"""
from __future__ import absolute_import
import json
from urlparse import urlparse, urlunparse, urljoin

from async.api import schedule
from django.db import connection
from slumber.connector.api import get_model
from slumber.connector.ua import get

from slumber.scheme import from_slumber_scheme

from pubsubpull import _join_with_project_path
from pubsubpull.models import ChangeSubscription


def add_trigger_function():
    """Used for older versions of Postres, or test runs where there are no
        migrations.
    """
    cursor = connection.cursor()
    sql = open(_join_with_project_path("trigger-function.sql")).read()
    cursor.execute(sql)


def change_detect(model):
    """Enable change detection on the requested model.
    """
    cursor = connection.cursor()
    sql = open(_join_with_project_path("trigger-attach.sql")).read()
    sql = sql.format(db_table=model._meta.db_table)
    cursor.execute(sql)
    return sql


def pull(model, callback, callback_kwargs=None, **kwargs):
    """Start a job pulling data from one service to this one.
    """
    if callback_kwargs is None:
        callback_kwargs = {}
    kwargs['callback_kwargs'] = callback_kwargs
    if 'pull_priority' in kwargs:
        schedule('pubsubpull.async.pull_monitor',
                 args=[model, callback], kwargs=kwargs, priority=kwargs['pull_priority'])
    else:
        schedule('pubsubpull.async.pull_monitor',
                 args=[model, callback], kwargs=kwargs)


def pull_up(model, callback, callback_kwargs=None, **kwargs):
    """Start a job monitoring new instance from latest instance.
    """
    if callback_kwargs is None:
        callback_kwargs = {}
    kwargs['callback_kwargs'] = callback_kwargs
    model_instance = get_model(model)
    instance_url = model_instance._operations['instances']
    _, json_data = get(instance_url)
    kwargs['floor'] = json_data['page'][0]['pk']
    schedule('pubsubpull.async.pull_monitor', args=[model, callback], kwargs=kwargs)


def pull_down(model, callback, callback_kwargs=None, **kwargs):
    """Start a job pulling data from latest to beginning instance.
    """
    if callback_kwargs is None:
        callback_kwargs = {}
    kwargs['callback_kwargs'] = callback_kwargs
    kwargs['delay'] = 0
    schedule('pubsubpull.async.pull_monitor', args=[model, callback], kwargs=kwargs)


def _get_data_from_slumber(update_log_url):
    """ get data from given url, accept both http and slumber scheme
    """
    _, json_data = get(from_slumber_scheme(update_log_url))
    return json_data


def _get_base_url(url):
    parts = urlparse(url)
    return urlunparse((parts.scheme, parts.netloc, '', '', '', ''))


def async_monitor(update_log_url, update_log_model_url):
    """ schedule jobs in ChangeSubscription model corresponding to update_log_model_url
    """
    json_data = _get_data_from_slumber(update_log_url)
    relative_instance_url = json_data['fields']['instance_url']['data']
    table = json_data['fields']['table']['data']
    base_url = _get_base_url(from_slumber_scheme(update_log_url))
    instance_url = urljoin(base_url, relative_instance_url)

    subscriptions = ChangeSubscription.objects.filter(
        update_log_model_url=update_log_model_url,
        table=table
    )

    for subscription in subscriptions:
        schedule(subscription.callback,
                 args=[instance_url],
                 kwargs=json.loads(subscription.callback_kwargs))


def monitor_model(update_log_model_url, model_url, table,
                  callback, callback_kwargs=None):
    if callback_kwargs is None:
        callback_kwargs = {}

    pull_down(model_url, callback, callback_kwargs=callback_kwargs)
    ChangeSubscription.objects.create(update_log_model_url=update_log_model_url,
                                      table=table,
                                      callback=callback,
                                      callback_kwargs=json.dumps(callback_kwargs))


def monitor_service(update_log_model_url):
    callback_kwargs = {'update_log_model_url': update_log_model_url}
    pull_up(update_log_model_url,
            'pubsubpull.api.async_monitor',
            callback_kwargs=callback_kwargs)

