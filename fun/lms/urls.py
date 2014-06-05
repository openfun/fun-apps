from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls.static import static

# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = patterns( '', 
  (r'^university/', include('universities.urls')),
  (r'^', include('lms.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

