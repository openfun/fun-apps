# -*- coding: utf-8 -*-

# This is useful for one-time scripts that need to run within a django
# environment.
# E.g: ./manage.py run-script ../sample_data_from_database.py --option=value arg1 arg2
from django.core.management.base import BaseCommand, CommandError

import imp
import sys


class Command(BaseCommand):

    help = """Run a non-django script with django settings."""
    args = "<path_to_script.py> [<script_args>...]"

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Path to script to run is required")
        sys.argv = list(args)
        imp.load_source("__main__", args[0])
