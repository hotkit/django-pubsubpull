# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from pubsubpull import _join_with_project_path


class Migration(migrations.Migration):

    dependencies = [
        ('pubsubpull', '0003_auto_20150508_0910'),
    ]

    operations = [
        migrations.RunSQL(file(_join_with_project_path("trigger-function.sql")).read()),
    ]
