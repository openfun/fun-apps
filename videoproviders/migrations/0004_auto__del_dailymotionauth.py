# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'DailymotionAuth'
        db.delete_table('videoproviders_dailymotionauth')


    def backwards(self, orm):
        # Adding model 'DailymotionAuth'
        db.create_table('videoproviders_dailymotionauth', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('api_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('university', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['universities.University'], unique=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('expires_at', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('videoproviders', ['DailymotionAuth'])


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
        }
    }

    complete_apps = ['videoproviders']
