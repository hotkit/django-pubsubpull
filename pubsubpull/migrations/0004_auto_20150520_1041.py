# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0003_auto_20150512_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='method',
            field=models.CharField(default='?', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='request',
            name='path',
            field=models.TextField(default='?'),
            preserve_default=False,
        ),
    ]
