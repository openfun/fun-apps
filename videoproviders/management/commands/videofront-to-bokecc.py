from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from opaque_keys.edx.keys import CourseKey
from libcast_xblock import LibcastXBlock
import xmodule.modulestore.django
from videoproviders.api import ClientError

from videoproviders.api.videofront import Client as videofrontclient
from videoproviders.api.bokecc import BokeccUtil

import requests
import json
from tempfile import NamedTemporaryFile
import hashlib

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
        make_option('-s', '--chunksize',
                    metavar='CHUNKSIZE',
                    dest='chunksize',
                    default=(4096 * 1024), # 4Mb max is recommended (http://doc.bokecc.com/vod/dev/uploadAPI/upload02/)
                    help='Chunk size for upload and download'),
    )

    def handle(self, *args, **options):

        course_key_string = options['courseid']
        if not course_key_string:
            raise CommandError("You must specify a course id")
        chunksize = options['chunksize']

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
                    #hdsource = filter(lambda vs: vs['res'] == 5400 , video['video_sources'])
                    hdsource = filter(lambda vs: vs['res'] == 900, video['video_sources'])
                    if len(hdsource)>=1 :
                        print 'Video hdsource' , hdsource[0]['url']
                        self.process_video(video['video_sources'][0]['url'], video['title'], video['id'], course_id,chunksize)
                        #self.process_video(hdsource[0]['url'],video['title'],video['id'],chunksize)
            except ClientError as e:
                print 'Error fetching video ({0}) Message ({1})'.format(video_id, e.message)

    def process_video(self,videofronthdurl,videofronttitle,videofrontid,course_id, cs):
        local_filename = videofronthdurl.split('/')[-1]

        print 'Processing video at {0} with name:{1} and id:{2} '.format(videofronthdurl, videofronttitle, videofrontid)

        bcc = BokeccVideoUploader(cs)
        # Check first if video exists already on bokeecc
        videoexists = bcc.check_video_exists(videofrontid)
        if videoexists is not None:
            print 'Video with videofront Id:{1} is already on Bokecc with ID {2} '.format(videofrontid,videoexists['id'])

        # If not then download it from videofront
        r = requests.get(videofronthdurl, stream=True)
        f = NamedTemporaryFile()
        chunkcount = 0
        filesize = r.headers['Content-length']
        filemd5 = hashlib.md5()
        for chunk in r.iter_content(chunk_size=cs):
            if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    filemd5.update(chunk)
                    chunkcount += 1
                    print '(' + str(chunkcount) +'/' + str(int(filesize)/cs+1) + ')',

        # Use title as videofrontid as it is the only field that is searcheable later
        # Keep the id in description just in case some would rename the files
        video = bcc.create_video(videofrontid,f.tell(),local_filename, filemd5.hexdigest(),videofrontid)
        if video:
            bcc.upload_video(video['videoid'],video['chunkurl'],f,local_filename)
            # Make sure we change this video an put in in the course playlist
            bcc.set_video_in_playlist(video['videoid'],course_id)
        f.close()

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

class BokeccVideoUploader:

    MAX_RETRY = 10

    def __init__(self, chunksize):
        self.api_salt_key, self.user_id = BokeccUtil.get_auth()
        self.chunksize = chunksize
        self.videometa = {}

    def set_video_metadata(self, videoid, filename, filesize, servicetype, md5, metadata_url, chunk_url):
        videoinfo = {
            'filename': filename,
            'filesize': filesize,
            'servicetype': servicetype,
            'md5': md5,
            'metadataurl': metadata_url,
            'chunkurl': chunk_url
        }
        self.videometa[videoid] = videoinfo

    def update_metadata(self, videoid,first=1):
        if (not self.videometa.has_key(videoid)):
            return None
        videoinfo =  self.videometa[videoid]
        data = {
            'uid': self.user_id,
            'ccvid': videoid.encode('ascii'),
            'first': first,
            'filename': videoinfo['filename'],
            'filesize': videoinfo['filesize'],
            'servicetype': videoinfo['servicetype'],
            'md5': videoinfo['md5'],
            'format': 'json'
        }
        p = requests.get(videoinfo['metadataurl'], params=data)
        if p and p.content:
            result = json.loads(p.content, 'utf-8')
            if result['result'] == 0:
                return result
        return None

    def create_video(self, title, filesize, filename, filemd5, desc):
        videoid =''
        bokecc_video = BokeccUtil.bokecc_request_get(
            'video/create',
            params={
                'userid' : self.user_id,
                'title': title,
                'filesize' : filesize,
                'filename' :  filename,
                'format': 'json',
                'description': desc
            }
        )
        if not 'error' in bokecc_video:
            if "uploadinfo" in bokecc_video:
                # Upload metadata
                videoid = bokecc_video['uploadinfo']['videoid']
                metadata_url = bokecc_video['uploadinfo']['metaurl']
                chunk_url = bokecc_video['uploadinfo']['chunkurl']
                self.set_video_metadata(videoid,
                                        filename,
                                        filesize,
                                        bokecc_video['uploadinfo']['servicetype'].encode('ascii'),
                                        filemd5,
                                        metadata_url,
                                        chunk_url)


                res = self.update_metadata(videoid, 1)
                if res is not None:
                        return bokecc_video['uploadinfo']

    def upload_video(self, videoid, uploadchunkurl, videofile,videofilename):
        fsize = videofile.tell()
        videofile.seek(0)
        chunk = videofile.read(self.chunksize)
        chunkstart = 0
        currentretry = 0
        error = ''
        self.update_metadata(videoid, 2)
        while chunk:
            data = {
                   'ccvid': videoid.encode('ascii'),
                   'format': 'json',
            }
            file = { 'file': (videofilename, bytearray(chunk), 'application/octet-stream')}
            contentrange = "bytes "+ str(chunkstart) + "-" + str(videofile.tell()) + "/" + str(fsize)
            header = {
                "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4)",
                "Content-Range": contentrange,
                'Accept': 'text/*',
                'Charset': 'UTF-8',
                'Cache-Control': 'no-cache'
            }
            print 'Uplodading file {0} to {1} - at {2} '.format(videofilename, uploadchunkurl, chunkstart)
            p = requests.post(uploadchunkurl, files=file, params=data,headers=header, stream = True)
            # Check response
            if p and p.content:
                content = json.loads(p.content, 'utf-8')
                if 'result' in content and content['result'] == 0:
                    #No error, so carry on
                    currentretry = 0
                    chunkstart = videofile.tell()
                    chunk = videofile.read(self.chunksize)
                else:
                    currentretry += 1
                    message = content['msg'].encode('utf-8')
                    if currentretry > BokeccVideoUploader.MAX_RETRY:
                        error = 'Issue while uploading file to bokecc ({0}) - at (chunk{1}) - Not retrying '\
                            .format(message, chunkstart)
                        break
                    else :
                        print 'Issue while uploading file to bokecc ({0}) - retrying (chunk{1}) '\
                            .format(message, chunkstart)
            else:
                error='General error : no response'
                break

        if error <> '':
            print error
            return False
        else:
            return True

    def set_video_in_playlist(self,videoid,course_id):
        playlistid = BokeccUtil.get_or_create_playlist(course_id)
        response = BokeccUtil.bokecc_request_get(
            'playlist/update',
            params={'playlistid': playlistid,
                    'userid' : self.user_id,
                    'format': 'json'
                    }
        )
        if not 'error' in response:
            videos = response['video']
            videoliststring = ''
            for video in videos:
                if not videoliststring == '':
                    videoliststring += ','
                videoliststring += video['id']
            response = BokeccUtil.bokecc_request_get(
                'playlist/update',
                params={'playlistid': playlistid,
                        'userid': self.user_id,
                        'video': videoliststring,
                        'format': json
                       }
                )
            return response

    def check_video_exists(self, videofrontid):
        response = BokeccUtil.bokecc_request_get(
            'videos/search',
            params={'userid': self.user_id,
                    'q': 'TITLE:'+videofrontid,
                    'format': 'json'
                    }
        )
        if not 'error' in response:
            if  response['videos']['total'] > 0:
                response['videos']['video'][0]
        return None