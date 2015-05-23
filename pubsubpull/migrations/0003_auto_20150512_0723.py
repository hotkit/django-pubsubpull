# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from pubsubpull import _join_with_project_path


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0002_auto_20150513_0130'),
    ]

    operations = [
        migrations.RunSQL(open(_join_with_project_path("trigger-function.sql")).read()),
    ]
