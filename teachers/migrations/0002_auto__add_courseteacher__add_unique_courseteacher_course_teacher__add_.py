# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CourseTeacher'
        db.create_table('teachers_courseteacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['courses.Course'])),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teachers.Teacher'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('teachers', ['CourseTeacher'])

        # Adding unique constraint on 'CourseTeacher', fields ['course', 'teacher']
        db.create_unique('teachers_courseteacher', ['course_id', 'teacher_id'])

        # Adding model 'CertificateTeacher'
        db.create_table('teachers_certificateteacher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['courses.Course'])),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teachers.Teacher'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('teachers', ['CertificateTeacher'])

        # Adding unique constraint on 'CertificateTeacher', fields ['course', 'teacher']
        db.create_unique('teachers_certificateteacher', ['course_id', 'teacher_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CertificateTeacher', fields ['course', 'teacher']
        db.delete_unique('teachers_certificateteacher', ['course_id', 'teacher_id'])

        # Removing unique constraint on 'CourseTeacher', fields ['course', 'teacher']
        db.delete_unique('teachers_courseteacher', ['course_id', 'teacher_id'])

        # Deleting model 'CourseTeacher'
        db.delete_table('teachers_courseteacher')

        # Deleting model 'CertificateTeacher'
        db.delete_table('teachers_certificateteacher')


    models = {
        'courses.course': {
            'Meta': {'object_name': 'Course'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['universities.University']"})
        },
        'teachers.certificateteacher': {
            'Meta': {'ordering': "('order', 'id')", 'unique_together': "(('course', 'teacher'),)", 'object_name': 'CertificateTeacher'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teachers.Teacher']"})
        },
        'teachers.courseteacher': {
            'Meta': {'ordering': "('order', 'id')", 'unique_together': "(('course', 'teacher'),)", 'object_name': 'CourseTeacher'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teachers.Teacher']"})
        },
        'teachers.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'teachers'", 'to': "orm['courses.Course']"}),
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

    complete_apps = ['teachers']
