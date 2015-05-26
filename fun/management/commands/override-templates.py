from optparse import make_option
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

# List of edx-platform/fun-apps tuples that indicate relative paths of templates to override.
OVERRIDDEN_TEMPLATES = [
    (
        "lms/templates/instructor/instructor_dashboard_2/membership.html",
        "forum_contributors/templates/instructor/instructor_dashboard_2/membership.html"
    ),
    (
        "lms/templates/discussion/_js_head_dependencies.html",
        "forum_contributors/templates/discussion/_js_head_dependencies.html"
    ),
    (
        "lms/templates/discussion/_underscore_templates.html",
        "forum_contributors/templates/discussion/_underscore_templates.html"
    ),
    (
        "lms/templates/discussion/index.html",
        "forum_contributors/templates/discussion/index.html"
    ),
]

OVERRIDDEN_THEME_TEMPLATES = [
    (
        "lms/templates/courseware/course_about.html",
        "templates/courseware/course_about.html",
    ),
    (
        "lms/templates/dashboard/_dashboard_course_listing.html",
        "templates/dashboard/_dashboard_course_listing.html",
    ),
    (
        "lms/templates/registration/password_reset_complete.html",
        "templates/registration/password_reset_complete.html",
    ),
    (
        "lms/templates/registration/password_reset_confirm.html",
        "templates/registration/password_reset_confirm.html",
    ),
    (
        "lms/templates/registration/password_reset_email.html",
        "templates/registration/password_reset_email.html",
    ),
    (
        "cms/templates/500.html",
        "templates/500.html",
    ),
    (
        "lms/templates/index.html",
        "templates/index.html",
    ),
    (
        "lms/templates/login.html",
        "templates/login.html",
    ),
    (
        "lms/templates/main.html",
        "templates/main.html",
    ),
    (
        "lms/templates/main_django.html",
        "templates/main_django.html",
    ),
    (
        "lms/templates/navigation.html",
        "templates/navigation.html",
    ),
    (
        "lms/templates/register-sidebar.html",
        "templates/register-sidebar.html",
    ),
]

class Command(BaseCommand):
    help = """Override a number of edX templates with the version provided by
the openfun/fork branch from the edx-platform repository. Before running
this script, make sure your openfun/fork branch is up-to-date."""

    option_list = BaseCommand.option_list + (
        make_option('--fun-repo',
                    default=settings.FUN_BASE_ROOT,
                    help='Path to fun-apps repository.'),
        make_option('--theme-repo',
                    default=settings.ENV_ROOT / "themes" / settings.THEME_NAME,
                    help='Path to edx-theme repository.'),
        make_option('--edx-repo',
                    default=os.path.join(settings.BASE_ROOT, "edx-platform"),
                    help='Path to edx-platform repository.'),
        make_option('--branch',
                    default="openfun/fork",
                    help='edx-platform branch to fetch the templates from.'),
        make_option('--reverse',
                    action='store_true',
                    default=False,
                    help='Override the edX templates with the templates from fun-apps'),
        make_option('--verbose',
                    action='store_true',
                    default=False,
                    help='Verbose mode'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.edx_repo_path = None
        self.fun_repo_path = None
        self.theme_repo_path = None
        self.branch = None
        self.is_verbose = None

    def handle(self, *args, **options):
        self.branch = options['branch']
        self.edx_repo_path = options['edx_repo']
        self.is_verbose = options['verbose']

        self.override_all(OVERRIDDEN_TEMPLATES, options['fun_repo'], reverse=options["reverse"])
        self.override_all(OVERRIDDEN_THEME_TEMPLATES, options['theme_repo'], reverse=options["reverse"])

    def override_all(self, templates_to_override, dst_dir, reverse=False):
        for edx_relative_path, dst_relative_path in templates_to_override:
            dst_path = os.path.abspath(os.path.join(dst_dir, dst_relative_path))
            if reverse:
                self.reverse_override(edx_relative_path, dst_path)
            else:
                self.override(edx_relative_path, dst_path)

    def override(self, edx_relative_path, dst_path):
        """Copy edx-platform template (from openfun/fork branch) to destination file"""
        self.log_override(dst_path, os.path.join(self.edx_repo_path, edx_relative_path))
        with cd(self.edx_repo_path):
            file_content = subprocess.check_output([
                'git',
                'show',
                "{}:{}".format(self.branch, edx_relative_path)
            ])
        with open(os.path.join(dst_path), 'w') as fun_file:
            fun_file.write(file_content)

    def reverse_override(self, edx_relative_path, src_path):
        """Copy template from src_path to edx-platform"""
        edx_path = os.path.abspath(os.path.join(self.edx_repo_path, edx_relative_path))
        self.log_override(edx_path, src_path)
        import shutil
        shutil.copy(src_path, edx_path)

    def log_override(self, src, dst):
        self.log("Overriding {} with {}".format(dst, src))

    def log(self, message, *args):
        """Log to stdout if verbose mode is activated."""
        if self.is_verbose:
            self.stdout.write(message % args)
            self.stdout.write("\n")


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = None

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)
