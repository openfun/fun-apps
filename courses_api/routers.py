from rest_framework.routers import DefaultRouter


class CourseAPIRouter(DefaultRouter):

    BASENAME = 'courses'

    def get_default_base_name(self, viewset):
        return self.BASENAME
