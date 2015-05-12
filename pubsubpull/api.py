"""
    APIs exposed by pubsubpull.
"""
from __future__ import absolute_import

from async.api import schedule
from django.db import connection

from pubsubpull import _join_with_project_path


def change_detect(model):
    """Enable change detection on the requested model.
    """
    cursor = connection.cursor()
    sql = file(_join_with_project_path("trigger-attach.sql")).read()
    cursor.execute(sql)


def pull(model, callback, **kwargs):
    """Start a job pulling data from one service to this one.
    """
    schedule('pubsubpull.async.pull_monitor',
        args=[model, callback], kwargs=kwargs)
