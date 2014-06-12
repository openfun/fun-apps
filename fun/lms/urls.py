from django.conf import settings
from django.conf.urls import url, include, patterns
from django.conf.urls.static import static

# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = patterns( '', 
  (r'^university/', include('universities.urls')),
  (r'^contact/', include('contact.urls')),
  (r'^', include('lms.urls'))
)

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

