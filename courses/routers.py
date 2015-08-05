from rest_framework.routers import DefaultRouter


class CourseAPIRouter(DefaultRouter):

    def get_default_base_name(self, viewset):
        return 'fun-courses-api'
