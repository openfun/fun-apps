# -*- coding: utf-8 -*-

from django.conf.urls import url, include, patterns

import openassessment.fileupload.urls

# Behind the scene Django determines the 404 view and the 500 view
# by looking for handler404, handler500 in your root URLconf.
# That's why we import handlers here.
from cms.urls import handler404, handler500 # pylint: disable=unused-import


urlpatterns = patterns('',

    (r'^selftest/', include('selftest.urls')),

    # Ora2 file upload
    url(r'^openassessment/storage', include(openassessment.fileupload.urls)),

    (r'^', include('cms.urls')),
)
