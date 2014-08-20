# -*- coding: utf-8 -*-

import StringIO

from PIL import Image

from django.http import HttpResponse

from contentserver.middleware import StaticContentServer
from xmodule.contentstore.content import StaticContentStream, StaticContent, XASSET_LOCATION_TAG
from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError


class ThumbnailStaticContentServer(StaticContentServer):
    """This middleware inherit from contentserver.middleware.StaticContentServer and will automatically
    generate thumbnail for existing asset in contentstore if request.GET contains a requested width, if not,
    it will pass the request to its parent.
    """
    def process_request(self, request):

        if request.path.startswith('/' + XASSET_LOCATION_TAG + '/'):
            if request.GET.get('width') or request.GET.get('height'):
                # generate the requested thumbnail location
                width = int(request.GET['width'])
                path = request.path.split('/')
                category = 'thumbnail'
                name = path[5].split('.')
                path[5] = "%s-w%d.%s" % (name[0], width, name[1])
                path[4] = category

                path = '/'.join(path)
                thumbnail_location = StaticContent.get_location_from_path(path)  # calculate thumbnail 'location' in gridfs
                try:  # is it already created ?
                    thumbnail_content = contentstore().find(thumbnail_location, as_stream=True)
                except NotFoundError:

                    # get original asset
                    asset_location = StaticContent.get_location_from_path(request.path)
                    try:
                        content = contentstore().find(asset_location, as_stream=True)
                    except NotFoundError:
                        return  # if original asset do not exists, let the request pass by 
                    # generate thumbnail
                    im = Image.open(StringIO.StringIO(content.copy_to_in_mem().data))
                    im = im.convert('RGB')
                    size = (width, width)  # PIL is dumb, we shall use a better tool to generate smartly framed thumbnails
                    im.thumbnail(size, Image.ANTIALIAS)
                    thumbnail_file = StringIO.StringIO()
                    im.save(thumbnail_file, 'JPEG')
                    thumbnail_file.seek(0)

                    # store thumbnail in contentstore
                    thumbnail_name = StaticContent.generate_thumbnail_name(thumbnail_location.name)
                    thumbnail_content = StaticContentStream(thumbnail_location, thumbnail_name,
                                                      'image/jpeg', thumbnail_file)

                    contentstore().save(thumbnail_content.copy_to_in_mem())

                # return found or generated tumbnail
                response = HttpResponse(thumbnail_content.copy_to_in_mem().stream_data(), content_type=thumbnail_content.content_type)
                return response

            return super(ThumbnailStaticContentServer, self).process_request(request)
