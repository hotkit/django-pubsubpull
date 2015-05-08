# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import pubsubpull.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pubsubpull', '0002_auto_20150508_0430'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(related_name='requests', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='updatelog',
            name='new',
            field=pubsubpull.models.JSONB(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='updatelog',
            name='old',
            field=pubsubpull.models.JSONB(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='updatelog',
            name='request',
            field=models.ForeignKey(related_name='changes', blank=True, to='pubsubpull.Request', null=True),
            preserve_default=True,
        ),
    ]
