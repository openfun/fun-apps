# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Course', fields ['key']
        db.create_unique('backoffice_course', ['key'])


    def backwards(self, orm):
        # Removing unique constraint on 'Course', fields ['key']
        db.delete_unique('backoffice_course', ['key'])


    models = {
        'backoffice.course': {
            'Meta': {'object_name': 'Course'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'null': 'True', 'to': "orm['universities.University']"})
        },
        'backoffice.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'teachers'", 'to': "orm['backoffice.Course']"}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        }
    }

    complete_apps = ['backoffice']
