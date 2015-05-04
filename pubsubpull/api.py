"""
    APIs exposed by pubsubpull.
"""
from __future__ import absolute_import

from async.api import schedule


def pull(model, callback, **kwargs):
    """Start a job pulling data from one service to this one.
    """
    schedule('pubsubpull.async.pull_monitor',
        args=[model, callback], kwargs=kwargs)
