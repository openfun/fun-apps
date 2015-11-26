from django.conf.urls import patterns, url

from .routers import CourseAPIRouter
from .api import CourseAPIView


router = CourseAPIRouter()
router.register(r'api/courses', CourseAPIView)
urlpatterns = router.urls
