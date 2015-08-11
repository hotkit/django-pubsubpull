"""
    Slumber operations.
"""
from slumber.configuration import configure
from pubsubpull.models import UpdateLog


configure({})
configure(UpdateLog,
          properties_ro=['instance_url'])
