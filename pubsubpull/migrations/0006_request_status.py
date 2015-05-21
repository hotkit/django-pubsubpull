# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0005_auto_20150520_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='status',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
