from .routers import CourseAPIRouter
from .api import CourseAPIView, CourseScoreView


router = CourseAPIRouter()
router.register(r'api/courses', CourseAPIView)
router.register(r'api/scores/courses', CourseScoreView)
urlpatterns = router.urls
