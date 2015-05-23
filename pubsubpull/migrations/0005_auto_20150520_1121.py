# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0004_auto_20150520_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='duration',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='started',
            field=models.DateTimeField(default=datetime.date(1970, 1, 1), auto_now_add=True),
            preserve_default=False,
        ),
    ]
