"""
Generate CSV files for submission and assessment data
"""
import os
import shutil
import tempfile
from django.core.management.base import CommandError
from openassessment.management.commands import upload_oa_data


class Command(upload_oa_data.Command):
    """
    Create and upload CSV files for submission and assessment data.
    """

    help = 'Create a CSV files for submission and assessment data.'
    args = '<COURSE_ID [OUTPUT_DIRECTORY]>'

    def handle(self, *args, **options):
        """
        Execute the command.

        Args:
            course_id (unicode): The ID of the course to use.
        Raises:
            CommandError

        """
        if len(args) < 1:
            raise CommandError(u'Usage: generate_oa_data {}'.format(self.args))
        output_directory = "/tmp"
        if len(args) >= 2:
            output_directory = args[1].decode('utf-8')

        course_id = args[0].decode('utf-8')
        output_path = self.dump(course_id, output_directory)
        self.stdout.write(u"Archive of course {} created in {}\n".format(course_id, output_path))

    def dump(self, course_id, output_directory):
        csv_dir = tempfile.mkdtemp()
        try:
            output_path = self.dump_unsafe(course_id, output_directory, csv_dir)
            return output_path
        finally:
            # Assume that the archive was created in the directory,
            # so to clean up we just need to delete the directory.
            shutil.rmtree(csv_dir)

    def dump_to(self, course_id, path):
        output_path = self.dump(course_id, "/tmp")
        shutil.move(output_path, path)

    def dump_unsafe(self, course_id, output_directory, csv_dir):
        self._dump_to_csv(course_id, csv_dir)
        archive_path = self._create_archive(csv_dir)
        output_path = os.path.join(output_directory, os.path.basename(archive_path))
        shutil.move(archive_path, output_path)
        return output_path
