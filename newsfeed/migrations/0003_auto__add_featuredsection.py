# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeaturedSection'
        db.create_table('newsfeed_featuredsection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='a_+', null=True, to=orm['newsfeed.Article'])),
            ('language', self.gf('django.db.models.fields.CharField')(default='fr', max_length=8)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('newsfeed', ['FeaturedSection'])


    def backwards(self, orm):
        # Deleting model 'FeaturedSection'
        db.delete_table('newsfeed_featuredsection')


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
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'newsfeed.featuredsection': {
            'Meta': {'object_name': 'FeaturedSection'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'a_+'", 'null': 'True', 'to': "orm['newsfeed.Article']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '8'})
        }
    }

    complete_apps = ['newsfeed']