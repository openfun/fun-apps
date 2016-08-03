# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'YoutubeCourseSettings'
        db.create_table('videoproviders_youtubecoursesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('xmodule_django.models.CourseKeyField')(max_length=255, db_index=True)),
            ('playlist_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('videoproviders', ['YoutubeCourseSettings'])

        # Adding model 'YoutubeAuth'
        db.create_table('videoproviders_youtubeauth', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['universities.University'], unique=True, null=True, blank=True)),
            ('client_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('token_expiry', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('videoproviders', ['YoutubeAuth'])


    def backwards(self, orm):
        # Deleting model 'YoutubeCourseSettings'
        db.delete_table('videoproviders_youtubecoursesettings')

        # Deleting model 'YoutubeAuth'
        db.delete_table('videoproviders_youtubeauth')


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
        },
        'videoproviders.videouploaderdeactivationperiod': {
            'Meta': {'object_name': 'VideoUploaderDeactivationPeriod'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'videoproviders.youtubeauth': {
            'Meta': {'object_name': 'YoutubeAuth'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'client_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'token_expiry': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'university': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['universities.University']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'videoproviders.youtubecoursesettings': {
            'Meta': {'ordering': "('course_id',)", 'object_name': 'YoutubeCourseSettings'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_id': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['videoproviders']