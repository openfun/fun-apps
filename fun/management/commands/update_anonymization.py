"""
A management command to update the anon ids after the secret key modifications.

We have 2 tables containing anon ids :
 * student.models.AnonymousUserId
 * submissions.models.StudentItem

Hopfully, this will solve the issues about :
 * submissions impossible to retrieve for grading
 * "anonymous id doesn't match computed..." spamming error
"""

from datetime import datetime
import hashlib
import json
import logging
import os
from optparse import make_option

from django.db.transaction import commit, set_autocommit
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from courses.models import Course
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, AnonymousUserId
from submissions.models import StudentItem

from backoffice.utils import get_course_key


OLD_SECRET_KEY = ""
NEW_SECRET_KEY = settings.SECRET_KEY
SAVE_PATH = '/tmp/'

COMMIT_EACH_N = 1000


def old_current_anon_ids(student, course_id):
    """ Compute anonymous id with the old secret key and the current one.
    """

    old_hasher = hashlib.md5()
    new_hasher = hashlib.md5()
    old_hasher.update(OLD_SECRET_KEY)
    new_hasher.update(NEW_SECRET_KEY)
    old_hasher.update(unicode(student.id))
    new_hasher.update(unicode(student.id))
    old_hasher.update(course_id.encode('utf-8'))
    new_hasher.update(course_id.encode('utf-8'))
    old_digest = old_hasher.hexdigest()
    new_digest = new_hasher.hexdigest()

    return old_digest, new_digest


def get_AnonymousUserIds(course_id):
    ck = CourseKey.from_string(course_id)
    enrollments = CourseEnrollment.objects.filter(course_id=ck).values_list('user__id', flat=True)
    ids = AnonymousUserId.objects.filter(course_id=ck, user__id__in=enrollments)
    return ids


def get_filename(prefix, course_id):
    return "%s/%s-%s.sql" % (SAVE_PATH, prefix, course_id.replace('/', '-'))


def create_StudentItem_SQL_restore(course_id):
    """Create SQL statements file to restore StudentItem objects
    to state before any changes."""
    anon_ids = get_AnonymousUserIds(course_id)
    with open(get_filename('restore_StudentItem', course_id), 'w') as sqlfile:
        sqlfile.write('START TRANSACTION;\n')
        for anon_id in anon_ids:
            old_anon, current_anon = old_current_anon_ids(anon_id.user, course_id)

            for row in StudentItem.objects.filter(student_id=old_anon):
                assert old_anon == row.student_id
                sqlfile.write('UPDATE submissions_studentitem SET student_id="%s" WHERE id=%d;\n' %
                    (old_anon, row.id))

        sqlfile.write('COMMIT;\n')


def create_StudentItem_SQL_update(course_id):
    """Create SQL statements file to update StudentItem objects
    to change `student_id` field generated with OLD_SECRET_KEY to value
    generated with NEW_SECRET_KEY."""
    anon_ids = get_AnonymousUserIds(course_id)
    with open(get_filename('update_StudentItem', course_id), 'w') as sqlfile:
        sqlfile.write('START TRANSACTION;\n')
        for anon_id in anon_ids:
            old_anon, current_anon = old_current_anon_ids(anon_id.user, course_id)

            for row in StudentItem.objects.filter(student_id=old_anon):
                assert old_anon == row.student_id
                sqlfile.write('UPDATE submissions_studentitem SET student_id="%s" WHERE id=%d;\n' %
                    (current_anon, row.id))

        sqlfile.write('COMMIT;\n')


def create_AnonymousUserId_SQL_restore(course_id):
    """Create SQL statements file to restore AnonymousUserId objects
    to state before any changes."""
    anon_ids = get_AnonymousUserIds(course_id)
    with open(get_filename('restore_AnonymousUserId', course_id), 'w') as sqlfile:
        sqlfile.write('START TRANSACTION;\n')
        for anon_id in anon_ids:
            sqlfile.write('UPDATE student_anonymoususerid SET anonymous_user_id="%s" WHERE id=%d;\n' % (
                    anon_id.anonymous_user_id, anon_id.id))
        sqlfile.write('COMMIT;\n')


def create_AnonymousUserId_SQL_update(course_id):
    """Create SQL statements file to update AnonymousUserId objects
    to change `anonymous_user_id` field generated with OLD_SECRET_KEY to value
    generated with NEW_SECRET_KEY."""
    anon_ids = get_AnonymousUserIds(course_id)
    with open(get_filename('update_AnonymousUserId', course_id), 'w') as sqlfile:
        sqlfile.write('START TRANSACTION;\n')
        for anon_id in anon_ids:
            old_anon, current_anon = old_current_anon_ids(anon_id.user, course_id)
            if anon_id.anonymous_user_id != current_anon:
                sqlfile.write('UPDATE student_anonymoususerid SET anonymous_user_id="%s" WHERE id=%d;\n' % (
                        current_anon, anon_id.id))
        sqlfile.write('COMMIT;\n')


def create_sql_files(course_id):
    print("Creating SQL files for course {}".format(course_id))
    print(" * AnonymousUserId update")
    create_AnonymousUserId_SQL_update(course_id=course_id)
    print(" * AnonymousUserId restore")
    create_AnonymousUserId_SQL_restore(course_id=course_id)
    print(" * StudentItem update")
    create_StudentItem_SQL_restore(course_id=course_id)
    print(" * StudentItem restore")
    create_StudentItem_SQL_update(course_id=course_id)
    print("End")


class Command(BaseCommand):
    help = """
                Command to update AnonymousUserId and StudentItem after a SECRET_KEY change.
                -------------------------------------------------------

            Example:

                ./manage.py lms --settings=fun.lms_dev update_anonymization --course org/course/session --create-sql-files
           """

    option_list = BaseCommand.option_list + (

        make_option('--create-sql-files',
                    action='store_true',
                    dest='create-sql-files',
                    help='Create 2 SQL files to update StudentItem and AnonymousUserId and respective backups',
                    default=False,
                    ),
        make_option('--create-sql-update-anonymous',
                    action='store_true',
                    dest='create-sql-update-anonymous',
                    default=False,
                    ),
        make_option('--create-sql-restore-anonymous',
                    action='store_true',
                    dest='create-sql-restore-anonymous',
                    default=False,
                    ),
        make_option('--create-sql-update-student',
                    action='store_true',
                    dest='create-sql-update-student',
                    default=False,
                    ),
        make_option('--create-sql-restore-student',
                    action='store_true',
                    dest='create-sql-restore-student',
                    default=False,
                    ),
        make_option('--course',
                    action='store',
                    dest='course',
                    default=False,
                    ),
        )

    def handle(self, *args, **options):
        if options["create-sql-files"]:
            if not options['course']:
                pivot = datetime(2016, 9, 19)
                courses = list(Course.objects.filter(start_date__lt=pivot, end_date__gt=pivot
                        ).values_list('key', flat=True))
                for course in courses:
                    create_sql_files(course)
            else:
                create_sql_files(options['course'])

        if options["create-sql-restore-anonymous"]:
            print("Creating SQL restore file for AnonymousStudentId")
            create_AnonymousUserId_SQL_restore(course_id=options['course'])
            print("End")

        if options["create-sql-update-anonymous"]:
            print("Creating SQL update file for AnonymousStudentId")
            create_AnonymousUserId_SQL_update(course_id=options['course'])
            print("End")

        if options["create-sql-restore-student"]:
            print("Creating SQL restore file for StudentItem")
            create_StudentItem_SQL_restore(course_id=options['course'])
            print("End")

        if options["create-sql-update-student"]:
            print("Creating SQL update file for StudentItem")
            create_StudentItem_SQL_update(course_id=options['course'])
            print("End")
