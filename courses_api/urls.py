
from rest_framework.routers import DefaultRouter

from .api import CourseAPIView, CourseSubjectAPIView


router = DefaultRouter()

router.register(r'api/courses', CourseAPIView, base_name='courses')
router.register(r'api/course_subjects', CourseSubjectAPIView, base_name='course_subjects')

urlpatterns = router.urls
