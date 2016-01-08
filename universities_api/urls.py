from .routers import UniversityAPIRouter
from .api import UniversityAPIView


router = UniversityAPIRouter()
router.register(r'api/universities', UniversityAPIView)
urlpatterns = router.urls
