# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0006_request_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('callback', models.CharField(max_length=128)),
                ('callback_kwargs', models.CharField(max_length=1024)),
                ('table', models.CharField(max_length=64)),
                ('update_log_model_url', models.CharField(max_length=1024)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
