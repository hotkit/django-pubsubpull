"""
    APIs used only for migrations.
"""
from __future__ import absolute_import

from django.db import connection

from pubsubpull import _join_with_project_path


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
