# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'University.dm_api_key'
        db.delete_column('universities_university', 'dm_api_key')

        # Deleting field 'University.dm_user_id'
        db.delete_column('universities_university', 'dm_user_id')


    def backwards(self, orm):
        # Adding field 'University.dm_api_key'
        db.add_column('universities_university', 'dm_api_key',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'University.dm_user_id'
        db.add_column('universities_university', 'dm_user_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    models = {
        'universities.university': {
            'Meta': {'ordering': "('-score', 'id')", 'object_name': 'University'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificate_logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'description': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'detail_page_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'partnership_level': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'prevent_auto_update': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['universities']