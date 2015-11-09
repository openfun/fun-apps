from rest_framework.routers import DefaultRouter


class CourseAPIRouter(DefaultRouter):

    BASENAME = 'api'

    def get_default_base_name(self, viewset):
        return self.BASENAME
