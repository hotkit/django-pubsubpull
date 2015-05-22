"""
    APIs exposed by pubsubpull.
"""
from __future__ import absolute_import

from async.api import schedule
from django.db import connection

from pubsubpull import _join_with_project_path


def add_trigger_function():
    """Used for older versions of Postres, or test runs where there are no
        migrations.
    """
    cursor = connection.cursor()
    sql = file(_join_with_project_path("trigger-function.sql")).read()
    cursor.execute(sql)


def change_detect(model):
    """Enable change detection on the requested model.
    """
    cursor = connection.cursor()
    sql = file(_join_with_project_path("trigger-attach.sql")).read()
    sql = sql.format(db_table=model._meta.db_table)
    cursor.execute(sql)
    return sql


def pull(model, callback, **kwargs):
    """Start a job pulling data from one service to this one.
    """
    if kwargs.has_key('pull_priority'):
        schedule('pubsubpull.async.pull_monitor',
            args=[model, callback], kwargs=kwargs, priority=kwargs['pull_priority'])
    else:
        schedule('pubsubpull.async.pull_monitor',
            args=[model, callback], kwargs=kwargs)
