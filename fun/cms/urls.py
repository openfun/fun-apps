# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include, patterns

import openassessment.fileupload.urls
from . import urls_videoupload

# Behind the scene Django determines the 404 view and the 500 view
# by looking for handler404, handler500 in your root URLconf.
# That's why we import handlers here.
from cms.urls import handler404, handler500 # pylint: disable=unused-import


urlpatterns = patterns('',
    # Ora2 file upload
    url(r'^openassessment/storage', include(openassessment.fileupload.urls)),

    # Videoupload dashboard
    (r'^videoupload/{}/'.format(settings.COURSE_KEY_PATTERN), include(urls_videoupload, namespace='videoupload')),
)


# Other base urls
urlpatterns += patterns('',
    (r'^', include('cms.urls')),
    (r'^', include('fun.common_urls')),
)
