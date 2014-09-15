# -*- coding: utf-8 -*-

from django.conf.urls import url, include, patterns

# Behind the scene Django determines the 404 view by looking for handler404,
# handler500 in your root URLconf. That why we import handlers here.
from cms.urls import handler404, handler500

urlpatterns = patterns( '',

    (r'^selftest/', include('selftest.urls')),

    (r'^', include('cms.urls')),
)
