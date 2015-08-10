"""
    APIs exposed by pubsubpull.
"""
from __future__ import absolute_import

from async.api import schedule
from django.db import connection

from pubsubpull import _join_with_project_path

from slumber.connector.api import get_model
from slumber.connector.ua import get

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

