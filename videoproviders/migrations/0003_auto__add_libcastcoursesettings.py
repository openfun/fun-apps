# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LibcastCourseSettings'
        db.create_table('videoproviders_libcastcoursesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('directory_slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('stream_slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('videoproviders', ['LibcastCourseSettings'])


    def backwards(self, orm):
        # Deleting model 'LibcastCourseSettings'
        db.delete_table('videoproviders_libcastcoursesettings')


    models = {
        'universities.university': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'University'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificate_logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'description': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'dm_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'dm_user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['universities.University']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'})
        },
        'videoproviders.dailymotionauth': {
            'Meta': {'object_name': 'DailymotionAuth'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'api_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'expires_at': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'university': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['universities.University']", 'unique': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'videoproviders.libcastauth': {
            'Meta': {'object_name': 'LibcastAuth'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'university': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['universities.University']", 'unique': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'videoproviders.libcastcoursesettings': {
            'Meta': {'object_name': 'LibcastCourseSettings'},
            'course': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'directory_slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream_slug': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['videoproviders']