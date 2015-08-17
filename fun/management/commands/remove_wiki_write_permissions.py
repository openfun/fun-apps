from django.core.management.base import BaseCommand, CommandError

import wiki.models.urlpath
import wiki.models.article
from course_wiki.utils import course_wiki_slug

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


class Command(BaseCommand):

    help = """Remove write authorizations from all wiki articles from the given
courses. This should be doable via the wiki settings view, but a bug in
django-wiki prevents inheriting read/write permission changes.
"""
    args = "<course_id_1> <course_id_2>..."

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Define at least one course_id argument")

        for course_key_string in args:
            course_key = CourseKey.from_string(course_key_string)
            course = modulestore().get_course(course_key)
            slug = course_wiki_slug(course)

            # Note that this requires one request per argument and could be optimised
            urlpaths = wiki.models.urlpath.URLPath.objects.select_related("article").filter(slug=slug)
            if not urlpaths:
                self.stdout.write(
                    "---- Wiki article '{}' for course {} could not be found\n".format(slug, course_key_string)
                )
                continue
            for urlpath in urlpaths:
                urlpath.article.group_write = False
                urlpath.article.other_write = False
                urlpath.article.save()
                urlpath_descendants = urlpath.article.descendant_objects()
                (wiki.models.article.Article.objects.filter(urlpath__in=urlpath_descendants)
                                                    .update(group_write=False, other_write=False))
                self.stdout.write(
                    "++++ Write permissions removed from wiki '{}' for course {}\n".format(slug, course_key_string)
                )
