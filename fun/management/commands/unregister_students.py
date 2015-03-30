# -*- coding: utf-8 -*-

import codecs
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment


class Command(BaseCommand):
    help = """ Unregister students by email address for a course.

    Example:
    unregister_students --course fun/0101/trim4 --input-file unregister_students_list

    The input file has one user email adress by line.

    """
    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='store',
                    dest='course',
                    type='string'),
        make_option('-i', '--input-file',
                    action='store',
                    dest='input_file',
                    default=False),)

    err_msg = u"Tried to unenroll email {} into course {}, but the user enrollment was not found\n"
    success_msg = u"Successfully unenrolled email {} into course {}\n"

    def handle(self, *args, **options):
        if not all([options['course'], options['input_file']]):
            raise CommandError('All arguments are mandatory')

        course_key = CourseKey.from_string(options['course'])
        unenrolled = 0
        untouched = 0

        with codecs.open(options['input_file'], 'r', 'utf-8') as input_file:
            for student_email in input_file:
                try:
                    student_email = student_email.strip('\n')
                    CourseEnrollment.objects.get(user__email=student_email.strip('\n'),
                                                 course_id=course_key,
                                                 is_active=True).delete()
                    unenrolled += 1
                    self.stdout.write(self.success_msg.format(student_email,
                                                              options['course']))
                except CourseEnrollment.DoesNotExist:
                    self.stderr.write(self.err_msg.format(student_email,
                                                          options['course']))
                    untouched += 1
                    continue
        self.stdout.write("TOTAL : \n{} unregistered students\n{} untouched\n".format(unenrolled,
                                                                                      untouched))
