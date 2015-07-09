# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    '''
    We are moving teachers and courses models from the backoffice application
    to more specific applications.
    '''

    def forwards(self, orm):
        db.rename_table('backoffice_course', 'courses_course')
        db.send_create_signal('courses', ['Course'])
        db.rename_table('backoffice_teacher', 'teachers_teacher')
        db.send_create_signal('teachers', ['Teacher'])

    def backwards(self, orm):
        db.rename_table('courses_course', 'backoffice_course')
        db.send_create_signal('backoffice', ['Course'])
        db.rename_table('teachers_teacher', 'backoffice_teachers')
        db.send_create_signal('backoffice', ['Teacher'])

    models = {}

    complete_apps = ['backoffice']
