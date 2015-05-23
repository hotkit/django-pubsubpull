# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import pubsubpull.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pubsubpull', '0001_initial'),
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
        migrations.CreateModel(
            name='UpdateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=1, choices=[(b'I', b'INSERT'), (b'U', b'UPDATE'), (b'T', b'TRUNCATE'), (b'D', b'DELETE')])),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('old', pubsubpull.fields.JSONB(null=True, blank=True)),
                ('new', pubsubpull.fields.JSONB(null=True, blank=True)),
                ('request', models.ForeignKey(related_name='changes', blank=True, to='pubsubpull.Request', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]
