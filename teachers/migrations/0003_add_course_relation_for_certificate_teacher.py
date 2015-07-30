# -*- coding: utf-8 -*-
import logging

from south.v2 import DataMigration


logger = logging.getLogger(__name__)


class Migration(DataMigration):

    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for teacher in orm.Teacher.objects.all():
            try:
                _related_course = teacher.course
            except orm['courses.Course'].DoesNotExist:
                logger.warning(
                    u'Data Migration: Could not find course relation for this '
                    'teacher: "{}" - (#{})'.format(teacher.full_name, teacher.id)
                )
                continue
            # Get all teachers entries with the same name - we use to have several
            # entries when the same teacher is associated to several couses.
            teacher_entries = orm.Teacher.objects.filter(
                full_name=teacher.full_name
            )
            for teacher_entry in teacher_entries:
                try:
                    orm.CertificateTeacher.objects.create(
                        teacher=teacher,
                        course=teacher_entry.course,
                        order=teacher_entry.order,
                    )
                except Exception as e:
                    logger.warning(
                        u'Data Migration: There was an issue while creating a'
                        'teacher-certificate relation. '
                        'Teacher: "{}" - (#{}).'
                        'Error: {}'.format(teacher.full_name, teacher.id, e)
                    )


    def backwards(self, orm):
        orm.CertificateTeacher.objects.all().delete()


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
    symmetrical = True
