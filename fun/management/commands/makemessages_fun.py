#! /usr/bin/env python
import argparse
import os
import optparse
import sys
import tempfile

from babel.messages.pofile import read_po, write_po
from babel.messages.frontend import CommandLineInterface as BabelCommandLineInterface

try:
    from django.core.management.base import BaseCommand
except ImportError:
    class BaseCommand(object):
        option_list = ()

CURRENT_DIR = os.path.dirname(__file__)
FUN_APPS_ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
FUN_APPS_TO_TRANSLATE = [
    "contact",
    "courses",
    "forum_contributors",
    "fun",
    "universities"
]
FUN_THEME_PATH = os.path.expanduser("~/themes/fun")
PATH_FUN_DJANGOPO = "%(root_path)s/locale/%(locale)s/LC_MESSAGES/django.po"
PATH_EDX_DJANGOPO = os.path.join(
    os.path.dirname(__file__),
    "../../../../edx-platform/",
    "conf/locale/%(locale)s/LC_MESSAGES/django.po"
)


class Command(BaseCommand):

    help = """Usage: makemessages_fun [-v] [-l fr|de] path1 [path2 [...]]
    
Update the %s file to make sure all fun-apps translations are
up-to-date.

You may also pass the 'all' app name to gather messages for all applications.

After you have collected the messages for an app, don't forget to run the
following command in the app folder to make sure the new translations are
properly compiled:

    django-admin.py compilemessages -l <locale>
""" % (
    PATH_FUN_DJANGOPO
)
    option_list = BaseCommand.option_list + (
        optparse.make_option('-l', '--locale',
            action="store",
            choices=("fr", "de"),
            default="fr",
            help="Select locale to process."),
        optparse.make_option('--compile',
            action="store_true",
            default=False,
            help="Run compilemessages after message collection."),
        optparse.make_option('--verbose',
            action="store_true",
            default=False,
            help="Activate verbose mode."),
    )

    def handle(self, *args, **options):
        locale = options["locale"]
        is_verbose = options["verbose"] or options["verbosity"] > 1
        run_compile = options["compile"]
        MessageMaker(self.stdout, is_verbose=is_verbose).handle(args, locale, run_compile=run_compile)

class MessageMaker(object):

    def __init__(self, stdout=None, is_verbose=False, run_compile=False):
        self.stdout = stdout or sys.stdout
        self.is_verbose = is_verbose
        self.run_compile = run_compile

    def handle(self, root_paths, locale, run_compile=False):
        for root_path in root_paths:
            if root_path == "all":
                self.make_all_messages(locale, run_compile=run_compile)
            else:
                self.make_messages(os.path.abspath(root_path), locale, run_compile=run_compile)

    def make_all_messages(self, locale, run_compile=False):
        for app_name in FUN_APPS_TO_TRANSLATE:
            self.make_messages(app_root_path(app_name), locale, run_compile=run_compile)
        # Translate theme
        self.make_messages(FUN_THEME_PATH, locale, run_compile=run_compile)

    def make_messages(self, root_path, locale, run_compile=False):
        pot_catalog = make_pot_catalog(root_path)
        path_fun_djangopo = PATH_FUN_DJANGOPO % {"locale": locale, "root_path": root_path}
        path_edx_djangopo = PATH_EDX_DJANGOPO % {"locale": locale}
        fun_catalog = read_po_catalog(path_fun_djangopo, locale)
        # TODO load edx_catalog once for all apps
        edx_catalog = read_po_catalog(path_edx_djangopo, locale)

        update_catalog(fun_catalog, edx_catalog, pot_catalog)

        self.stdout.write("Updating %s...\n" % path_fun_djangopo)
        if self.is_verbose:
            check_catalog(fun_catalog)
        write_po_catalog(fun_catalog, path_fun_djangopo)

        if run_compile:
            compile_messages(root_path, locale)

def compile_messages(path, locale):
    from fun.utils.context import cd, setenv
    import subprocess
    with cd(path):
        with setenv("DJANGO_SETTINGS_MODULE", None):
            subprocess.call(["/edx/app/edxapp/venvs/edxapp/bin/django-admin.py", "compilemessages", "-l", locale])

def app_root_path(app_name):
    return os.path.join(FUN_APPS_ROOT_DIR, app_name)

def make_pot_catalog(root_path):
    pot_path = os.path.join(tempfile.gettempdir(), "fun-django.pot")
    cfg_path = os.path.join(FUN_APPS_ROOT_DIR, "babel.cfg")
    extract_command_args = [
            "pybabel", "--quiet", "extract",
            "-o", pot_path, "-F", cfg_path,
            "--keyword=pgettext_lazy:1c,2",
            root_path
    ]
    BabelCommandLineInterface().run(extract_command_args)
    pot_catalog = read_po_catalog(pot_path, None)
    return pot_catalog

def read_po_catalog(path, locale):
    with open(path) as po_file:
        return read_po(po_file, locale=locale)

def check_catalog(catalog):
    missing_translations = sorted([
        message.id for message in catalog
        if not message.string
    ])
    if missing_translations:
        print "{} missing translations:".format(len(missing_translations))
        for missing_translation in missing_translations:
            print "    - {}".format(missing_translation)

def write_po_catalog(catalog, path):
    with open(path, "w") as catalog_file:
        write_po(catalog_file, catalog, sort_output=True)

def update_catalog(fun_catalog, edx_catalog, pot_catalog):
    """
    Update fun_catalog with the following strategy:
        - get rid of messages from pot_catalog that are already translated in edx_catalog (but not in fun_catalog).
        - add a comment to fun_catalog messages that override existing edx messages
        - update the existing fun_catalog with the messages from pot_catalog (the new catalog)
        - make sure that translations from fun_catalog that override edx_catalog messages are kept
    """
    remove_messages_that_should_not_be_translated(pot_catalog, fun_catalog, edx_catalog)
    comment_messages(pot_catalog, edx_catalog)
    comment_messages(fun_catalog, edx_catalog)
    fun_catalog.update(pot_catalog)
    keep_overriden_messages(fun_catalog, edx_catalog)

def remove_messages_that_should_not_be_translated(pot_catalog, fun_catalog, edx_catalog):
    # Filter out messages that are translated in edx_catalog but not in fun_catalog
    message_ids_to_delete = []
    for message in pot_catalog:
        if message.id not in fun_catalog and message.id in edx_catalog:
            message_ids_to_delete.append(message.id)
    for message_id in message_ids_to_delete:
        pot_catalog.delete(message_id)

def comment_messages(catalog, edx_catalog):
    for message in catalog:
        message.user_comments = []
        if message.id in edx_catalog:
            message.user_comments.append("Translated in edx by '%s'" % edx_catalog[message.id].string)

def keep_overriden_messages(fun_catalog, edx_catalog):
    # Keep obsolete messages that actually override edx messages
    overriden_message_ids = set()
    for message_id, message in fun_catalog.obsolete.iteritems():
        if message_id in edx_catalog and message.string != edx_catalog[message_id].string:
            overriden_message_ids.add(message_id)

    for message_id in overriden_message_ids:
        fun_catalog[message_id] = fun_catalog.obsolete.pop(message_id, default=None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make messages to translate for FUN")
    parser.add_argument("locale", choices=['fr', 'de'], help="Locale to translate to")
    parser.add_argument("paths", nargs='+', help="Paths to process")

    main_args = parser.parse_args()

    MessageMaker().handle(main_args.paths, main_args.locale)
