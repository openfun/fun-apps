from rest_framework.routers import DefaultRouter


class UniversityAPIRouter(DefaultRouter):

    BASENAME = 'universities'

    def get_default_base_name(self, viewset):
        return self.BASENAME
