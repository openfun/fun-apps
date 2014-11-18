# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table('newsfeed_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('text', self.gf('ckeditor.fields.RichTextField')(blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='fr', max_length=8)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('edited_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('newsfeed', ['Article'])


    def backwards(self, orm):
        # Deleting model 'Article'
        db.delete_table('newsfeed_article')


    models = {
        'newsfeed.article': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Article'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'edited_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '8'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'text': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['newsfeed']