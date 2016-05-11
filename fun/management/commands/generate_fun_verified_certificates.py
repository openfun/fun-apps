from django.core.management.base import BaseCommand

from backoffice.certificate_manager.tasks_verified import iter_generated_course_verified_certificates
from opaque_keys.edx.keys import CourseKey

class Command(BaseCommand):
    args = '<course_id course_id>'
    help = 'generate FUN verified certificates for a course'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for course_key_string in args:
            course_id = CourseKey.from_string(course_key_string)
            for status in iter_generated_course_verified_certificates(course_id):
                print status
