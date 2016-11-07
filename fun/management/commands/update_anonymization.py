"""
A management command to update the anon ids after the secret key modifications.

We have 2 tables containing anon ids :
 * student.models.AnonymousUserId
 * submissions.models.StudentItem

Hopfully, this will solve the issues about :
 * submissions impossible to retrieve for grading
 * "anonymous id doesn't match computed..." spamming error
"""

import hashlib
from datetime import datetime
import json
import os
from optparse import make_option
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import commit, set_autocommit

from courses.models import Course
from student.models import AnonymousUserId
from submissions.models import StudentItem

from backoffice.utils import get_course_key


from opaque_keys.edx.keys import CourseKey


OLD_SECRET_KEY = ""
NEW_SECRET_KEY = settings.SECRET_KEY

COMMIT_EACH_N = 1000

# we want to remove logging about "id doesn't match computed id" during the script execution
#log = logging.getLogger("student.models")
#log.setLevel(logging.CRITICAL)


class NoAutocommitContext(object):
    """A context manager to remove auto-commit for database.

    We use this to prevent base blocking during a few hours.

    WARNING : using this manager, you need to call "commit()"
    every now and then to effectively update the data.
    """
    def __enter__(self):
        print "Disabling autocommit"
        set_autocommit(False)

    def __exit__(self, *args):
        commit()
        print("commited last items")

        print "Re-enabling auto-commit"
        set_autocommit(True)


def old_current_anon_ids(student, course_id):
    """ Compute anonymous id with the old secret key and the current one.

    This is quite ugly, because we need to use a test function
    to override the SECRET_KEY setting.

    anonymous_id_for_user makes poor man's caching in a dictionary, so we
    need to reset the dict before using the function.
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


def remove_already_existing_csv():
    """ Removes the CSV backup files."""
    try:
        os.remove("/tmp/anon_ids.csv")
    except OSError:
        print("Unknown file /tmp/anon_ids.csv")

    try:
        os.remove("/tmp/student_items.csv")
    except OSError:
        print("Unknown file /tmp/student_items.csv")


def _init_csv():
    """Create the first lines of the backup CSVs."""
    with open("/tmp/anon_ids.csv", "a") as f:
        f.write("# AnonymousUserId dump file\n")
        f.write("# {}\t{}\t{}\t{}\n".format("course_key_string",
                                        "user_primary_key",
                                        "username",
                                        "anonymous_id"))

    header = "# {}\t{}\t{}\t{}\n"
    header = header.format("course_key_string",
                           "student_anonymous_id",
                           "item_id", "current_anon")
    with open("/tmp/student_items.csv", "a") as f:
        f.write("# StudentItem dump file\n")
        f.write(header)


def save_db_anon():
    """
    Save data from tables:
      * AnonymousUserId in file /tmp/anon_ids.csv
      * StudentItem in file /tmp/student_items.csv
    """
    _init_csv()

    print("counting elements in anon ids")
    count = AnonymousUserId.objects.count()
    print("count ok")

    print("getting anon ids")
    annon_ids = AnonymousUserId.objects.iterator()
    print("anon ids ok")

    with open("/tmp/anon_ids.csv", "a") as f:
        with open("/tmp/student_items.csv", "a") as g:
            for index, annon_id in enumerate(annon_ids):
                course_id = annon_id.course_id
                user = annon_id.user
                db_anonymous_user_id = annon_id.anonymous_user_id

                if (index+1) % COMMIT_EACH_N == 0:
                    print("Saved {} / {}".format(index, count))

                f.write("{}\t{}\t{}\t{}\n".format(unicode(course_id),
                                            user.pk,
                                            user.username,
                                            db_anonymous_user_id))

                old_anon, current_anon = old_current_anon_ids(user, course_id)

                old_anon_student_items = StudentItem.objects.filter(student_id=old_anon)
                for old_anon_student_item in old_anon_student_items:
                    student_id = old_anon_student_item.student_id
                    course_key_string = old_anon_student_item.course_id
                    item_id = old_anon_student_item.item_id

                    g.write("{}\t{}\t{}\t{}\n".format(course_key_string,
                                                      student_id,
                                                      item_id, current_anon))


def restore_db_anon_ids():
    """
    Restore data to tables:
      * AnonymousUserId from file /tmp/anon_ids.csv

    We need to manipulate the commit configuration and
    commit manually each COMMIT_EACH_N in order to not block the base.
    """

    with NoAutocommitContext():
        with open("/tmp/anon_ids.csv", "r") as f:
            f.next()
            f.next()
            for index, line in enumerate(f):
                data = line.strip().split("\t")
                course_key_string, user_pk, _, saved_anonymous_user_id = data

                if course_key_string.lower() == "none":
                    # in dev I have some none in course key string...
                    # we will need to investigate more before continuing...
                    print(" X course not found in data line: {}".format(data))
                    continue
                course_key = get_course_key(course_key_string)
                user = User.objects.get(pk=user_pk)

                anon_user = AnonymousUserId.objects.get(course_id=course_key, user=user)
                anon_user.anonymous_user_id = saved_anonymous_user_id
                anon_user.save()

                message = "OK Restoring anonymous user id, student_pk {} with anonymous id {}"
                print(message.format(user_pk, saved_anonymous_user_id))

                if (index + 1) % COMMIT_EACH_N == 0:
                    commit()
                    print("      => commited transactions")

    print("End restore_db_anon_ids")


def restore_student_items():
    """
    Restore data to tables:
        * StudentItem from file /tmp/student_items.csv

    We need to manipulate the commit configuration and
    commit manually each COMMIT_EACH_N in order to not block the base.
    """
    with NoAutocommitContext():
        with open("/tmp/student_items.csv", "r") as f:
            f.next()
            f.next()
            for index, line in enumerate(f):
                data = line.strip().split("\t")
                course_key_string, old_user_anon_id, item_id, updated_anon_id = data

                try:
                    student_item = StudentItem.objects.get(course_id=course_key_string,
                                                           student_id=updated_anon_id,
                                                           item_id=item_id)
                except StudentItem.DoesNotExist:
                    message = " X Unknown student db with course id: {} -- student_id: {} -- item: {}"
                    print(message.format(course_key_string, updated_anon_id, item_id))
                else:
                    student_item.student_id = old_user_anon_id
                    student_item.save()

                    message = "OK Restoring student item, student_id: {} -> {}"
                    print(message.format(updated_anon_id, old_user_anon_id))

                if (index + 1) % COMMIT_EACH_N == 0:
                    commit()
                    print("      => commited transactions")

    print("End restore_student_items")


def restore_data():
    """ Change the anonyous user id to match the new secret key

    WARNING : these function only switch anonymous id from one secret key to the other.
    It doesn't restore the database in the old configuration (some ids will be wrong).
    DO NOT USE IN PRODUCTION
    """
    with NoAutocommitContext():
        annon_ids = AnonymousUserId.objects.iterator()
        for index, annon_id in enumerate(annon_ids):
            course_id = annon_id.course_id
            user = annon_id.user
            db_anonymous_user_id = annon_id.anonymous_user_id

            # update student item with new ID
            current_anon, old_anon = old_current_anon_ids(user, course_id)

            old_anon_student_items = StudentItem.objects.filter(student_id=old_anon)
            old_anon_student_items.update(student_id=current_anon)
            if old_anon_student_items:
                print("Updating student item for {} -> {}".format(old_anon, current_anon))

            if db_anonymous_user_id == old_anon:
                # update the AnonymousUserId with the new one
                annon_id.anonymous_user_id = current_anon
                print("Updating anonymous user ID {} -> {}".format(old_anon, current_anon))
                annon_id.save()

            if (index+1) % COMMIT_EACH_N == 0:
                commit()
                print("      => commited transactions")

    print("End data migration")


def primary_keys_ok(course_id):
    """ Show the primary key of the first anonymous_id and first student_item with the correct key

    Dump data in the file /tmp/secret_key_primary_keys_ok.json
    With the file we can analyze the primary_keys repartition to
    find the pivot (old / new secret key used) in all the tables.
    """
    ck = CourseKey.from_string(course_id)

    users_ok_pk = []  # users primary keys
    items_ok_pk = []  # student_items ok primary_keys

    for anon_user_id in AnonymousUserId.objects.filter(user__courseenrollment__course_id=ck):
        ident = anon_user_id.anonymous_user_id

        old_ident, current_ident = old_current_anon_ids(anon_user_id.user, anon_user_id.course_id)
        if current_ident == ident:
            users_ok_pk.append(anon_user_id.user.pk)

            items_ok_pk.extend(
                StudentItem.objects.filter(student_id=current_ident).values_list("pk", flat=True))

    oks = {"student_items": items_ok_pk, "user_ids": users_ok_pk}
    filename = ck.to_deprecated_string().replace('/', '-')
    json.dump(oks, open("/tmp/secret_key_primary_keys_ok-%s.json" % filename, "w"))


def migrate_data(course_id):
    """ Change the anonyous user id to match the new secret key"""
    print("migrating %s" % course)
    ck = CourseKey.from_string(course_id)

    with NoAutocommitContext():

        annon_ids = AnonymousUserId.objects.filter(user__courseenrollment__course_id=ck)
        print("%s: %d" % (ck, annon_ids.count()))
        for index, annon_id in enumerate(annon_ids):
            user = annon_id.user
            db_anonymous_user_id = annon_id.anonymous_user_id

            # update student item with new ID
            old_anon, current_anon = old_current_anon_ids(user, course_id)
            # current_anon, old_anon = old_current_anon_ids(user, course_id)

            old_anon_student_items = StudentItem.objects.filter(student_id=old_anon)
            old_anon_student_items.update(student_id=current_anon)
            if old_anon_student_items:
                print("Updating student item for {} -> {}".format(old_anon, current_anon))

            if db_anonymous_user_id == old_anon:
                # update the AnonymousUserId with the new one
                annon_id.anonymous_user_id = current_anon
                print("Updating anonymous user ID {} -> {}".format(old_anon, current_anon))
                annon_id.save()

            if (index + 1) % COMMIT_EACH_N == 0:
                commit()
                print("      => commited transactions")

    print("End data migration")


def create_SQL_restore(course_id):
    """Create SQL statements file to restore AnonymousUserId objects."""
    ck = CourseKey.from_string(course_id)
    anon_ids = AnonymousUserId.objects.filter(user__courseenrollment__course_id=ck)
    with open("/tmp/restore_AnonymousUserId-%s.sql" % ck.to_deprecated_string().replace('/', '-'), "w") as sqlfile:
        sqlfile.write('START TRANSACTION;\n')
        for anon_id in anon_ids:
            sqlfile.write('UPDATE student_anonymoususerid SET anonymous_user_id="%s" where id=%d;\n' % (
                    anon_id.anonymous_user_id, anon_id.id))
        sqlfile.write('COMMIT;\n')


class Command(BaseCommand):
    help = """
                Command to update anon ids after the secret key update.
                -------------------------------------------------------

             Usage : < --migrate >

             To use it :

                One action is mandatory, choose between :
                  1 - migrate: to migrate the data
                  2 - backup: to backup to CSV files
                  3 - restore: to restore databases from CSV files
                  4 - stats: to dump primary keys in order to find the pivot

                optional :
                  1 - remove_csv: remove already existing CSV before performing backup

            Example:

                ./manage.py lms --settings=fun.lms_dev update_anonymization --migrate
                ./manage.py lms --settings=fun.lms_dev update_anonymization --backup --remove_csv
           """

    option_list = BaseCommand.option_list + (
        make_option('-m', '--migrate',
                    action='store_true',
                    dest='migrate',
                    default=False,
                    ),
        make_option('-b', '--backup',
                    action='store_true',
                    dest='backup',
                    default=False,
                    ),
        make_option('-r', '--restore',
                    action='store_true',
                    dest='restore',
                    default=False,
                    ),
        make_option('--remove_csv',
                    action='store_true',
                    dest='remove',
                    default=False,
                    ),
        make_option('--stats',
                    action='store_true',
                    dest='stats',
                    default=False,
                    ),
        make_option('--create-sql-restore',
                    action='store_true',
                    dest='create-sql-restore',
                    default=False,
                    ),
        make_option('--course',
                    action='store',
                    dest='course',
                    ),
        )

    def handle(self, *args, **options):
        if options["backup"]:
            print("Backuping data")
            if options["remove"]:
                print("Removing already existing CSVs")
                remove_already_existing_csv()

            save_db_anon()
            print("End data backup")

        if options["migrate"]:
            print("Migrating data")
            migrate_data()
            print("End data migration")

        if options["restore"]:
            print("Restoring data")
            restore_student_items()
            restore_db_anon_ids()
            print("End data restoration")

        if options["create-sql-restore"]:
            print("Creating SQL restore file")
            create_SQL_restore(course_id=options['course'])
            print("End")

        if options["stats"]:
            print("Dumping primary keys")
            if "course" in options :
                primary_keys_ok(course_id=options['course'])
            else :
                courses = Course.objects.all()
                for course in courses:
                    primary_keys_ok(course)

            print("End primary keys dump")