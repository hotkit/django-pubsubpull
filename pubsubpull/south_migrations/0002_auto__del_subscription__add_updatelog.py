# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Subscription'
        db.delete_table('pubsubpull_subscription')

        # Adding model 'UpdateLog'
        db.create_table('pubsubpull_updatelog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('table', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pubsubpull', ['UpdateLog'])


    def backwards(self, orm):
        # Adding model 'Subscription'
        db.create_table('pubsubpull_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('pubsubpull', ['Subscription'])

        # Deleting model 'UpdateLog'
        db.delete_table('pubsubpull_updatelog')


    models = {
        'pubsubpull.updatelog': {
            'Meta': {'object_name': 'UpdateLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'table': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pubsubpull']