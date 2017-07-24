from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from opaque_keys.edx.keys import CourseKey
from libcast_xblock import LibcastXBlock
import xmodule.modulestore.django
from videoproviders.api import ClientError

from videoproviders.api.videofront import Client as videofrontclient

class Command(BaseCommand):
    help = """
       Fetch course videos and upload it to bokecc
       """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--courseid',
                    metavar='COURSEID',
                    dest='courseid',
                    default=None,
                    help='Course to fetch videos from'),
    )

    def handle(self, *args, **options):

        course_key_string = options['courseid']
        if not course_key_string:
            raise CommandError("You must specify a course id")


        course_id = CourseKey.from_string(course_key_string)
        store = xmodule.modulestore.django.modulestore()
        store =store._get_modulestore_for_courselike(course_id)

        videofront_client = videofrontclient(course_key_string)

        for xblock in store.get_items(course_id):
            try :
                if isinstance(xblock, LibcastXBlock):
                    video_id = "video_id={}".format(xblock.video_id.encode("utf-8"))
                    provider = "bokecc" if hasattr(xblock,'is_bokecc_video') and xblock.is_bokecc_video else "videofront"
                    provider = "youtube" if xblock.is_youtube_video else provider
                    ancestry = xblock_ancestry(xblock).encode("utf-8")
                    print unicode(course_id), "->", ancestry, provider, video_id

                    video = videofront_client.get_video_with_subtitles(xblock.video_id)
                    hdsource = filter(lambda vs: vs['res'] == 5400 , video['video_sources'])
                    if len(hdsource)>=1 :
                        print 'hdsource' , hdsource[0]['url']
            except ClientError as e:
                print 'Error fetching video ({0}) Message ({1})'.format(video_id, e.message)


def xblock_ancestry(item):
    from xmodule.modulestore.exceptions import ItemNotFoundError
    try:
        parent = item.get_parent()
        parent_ancestry = "" if parent is None else xblock_ancestry(parent)
    except ItemNotFoundError:
        parent_ancestry = "/ORPHAN"
    if parent_ancestry:
        parent_ancestry += u"/"
    return u"{}{}".format(parent_ancestry, item.display_name)
