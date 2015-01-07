"""
Generate CSV files for submission and assessment data
"""
import sys
import os
import os.path
import datetime
import shutil
import tempfile
import tarfile
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from openassessment.data import CsvWriter


class Command(BaseCommand):
    """
    Create and upload CSV files for submission and assessment data.
    """

    help = 'Create a CSV files for submission and assessment data.'
    args = '<COURSE_ID>'

    OUTPUT_CSV_PATHS = {
        output_name: "{}.csv".format(output_name)
        for output_name in CsvWriter.MODELS
    }

    PROGRESS_INTERVAL = 10

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._submission_counter = 0

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

        course_id = args[0].decode('utf-8')
        csv_dir = tempfile.mkdtemp()

        try:
            print u"Generating CSV files for course '{}'".format(course_id)
            self._dump_to_csv(course_id, csv_dir)
            print u"Creating archive of CSV files in {}".format(csv_dir)
            archive_path = self._create_archive(csv_dir)

        finally:
            # Assume that the archive was created in the directory,
            # so to clean up we just need to delete the directory.
            shutil.rmtree(csv_dir)

    def _dump_to_csv(self, course_id, csv_dir):
        """
        Create CSV files for submission/assessment data in a directory.

        Args:
            course_id (unicode): The ID of the course to dump data from.
            csv_dir (unicode): The absolute path to the directory in which to create CSV files.

        Returns:
            None
        """
        output_streams = {
            name: open(os.path.join(csv_dir, rel_path), 'w')
            for name, rel_path in self.OUTPUT_CSV_PATHS.iteritems()
        }
        csv_writer = CsvWriter(output_streams, self._progress_callback)
        csv_writer.write_to_csv(course_id)

    def _create_archive(self, dir_path):
        """
        Create an archive of a directory.

        Args:
            dir_path (unicode): The absolute path to the directory containing the CSV files.

        Returns:
            unicode: Absolute path to the archive.

        """
        tarball_name = u"{}.tar.gz".format(
            datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M")
        )
        tarball_path = os.path.join('/tmp', tarball_name)
        with tarfile.open(tarball_path, "w:gz") as tar:
            for rel_path in self.OUTPUT_CSV_PATHS.values():
                tar.add(os.path.join(dir_path, rel_path), arcname=rel_path)
        return tarball_path

    def _progress_callback(self):
        """
        Indicate progress to the user as submissions are processed.
        """
        self._submission_counter += 1
        if self._submission_counter > 0 and self._submission_counter % self.PROGRESS_INTERVAL == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
