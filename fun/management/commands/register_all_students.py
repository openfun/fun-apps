# pylint: disable=missing-docstring

from optparse import make_option
import datetime
from pytz import UTC

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Q

from student.models import CourseEnrollment

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from xmodule.modulestore.django import modulestore
from xmodule.course_module import CourseDescriptor



class Command(BaseCommand):
    help = """
                Command to enroll all students to a course
                ------------------------------------------

             Usage : <--course COURSE_ID [--exclude-non-active-users] [-info-interval INTERVAL]>

             To use it :

                One argument is mandatory :
                  1 - the course id (example mycourse/2002/trim_2 )

                Two arguments are optional :
                  1 - exclude-non-active-users : you can exclude in the subsciptions
                      non active students. A non active student is a user that has not validated
                      his account, by clicling on the linked received by mail after the subsciption.

                  2 - info-interval : Print updates after n students enrolled.

            Example:

                ./manage.py lms --settings=fun.lms_dev register_all_students --course mycourse/2002/trim_2 -info-interval 80

           """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action = 'store',
                    dest = 'course',
                    type = 'string'
                    ),
        make_option('-e', '--exclude-non-active-users',
                    action = 'store_true',
                    dest = 'exclude',
                    default = False,
                   ),
        make_option('-i', '--info-interval',
                    action = 'store',
                    dest = 'info_interval',
                    type = 'int'
                   ),
        )

    def handle(self, *args, **options):

        if not options['course']:
            raise CommandError('You must specify a course id')

        COURSE_ID = options['course']

        # Print update after this many students
        if options['info_interval']:
            STATUS_INTERVAL = options['info_interval']
        else:
            STATUS_INTERVAL = 100


        print "\nEnroll all active students to '%s'" % COURSE_ID

        try:
            # CourseKeys are needed to query databases (SQL, Mongo)
            course_key = CourseKey.from_string(COURSE_ID)
            if not modulestore().get_course(course_key, depth=2):
                print "\n Course %s not found." % COURSE_ID
                return

            students = 0
            enrolled = 0
            start = datetime.datetime.now(UTC)

            # Fetch all users that are not superuser, exclude non active students if necessary
            users = User.objects.exclude(Q(is_active=options['exclude']) | Q(profile__isnull=True))

            total_students = users.count()

            for user in users:

                if enrolled % STATUS_INTERVAL == 0:
                    # Print a status update with an approximation of
                    # how much time is left based on how long the last
                    # interval took
                    diff = datetime.datetime.now(UTC) - start
                    timeleft = diff * (total_students - enrolled) / STATUS_INTERVAL
                    hours, remainder = divmod(timeleft.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    print "{0} students out of {1} were successfully enrolled to course {2} ~{3:02}:{4:02}m remaining".format(
                        enrolled, total_students,COURSE_ID, hours, minutes)

                    start = datetime.datetime.now(UTC)

                if not CourseEnrollment.objects.filter(user=user, course_id=course_key).exists():
                    CourseEnrollment.objects.create(user=user,
                                                        course_id=course_key,
                                                        is_active=True,
                                                        mode='honor')
                enrolled += 1

            print "\nSubscription progress is over : {0} students out of {1} were successfully enrolled to course {2}".format(
                        enrolled, total_students,COURSE_ID)

        except InvalidKeyError:
            print("Course id {} could not be parsed as a CourseKey;".format(COURSE_ID))
