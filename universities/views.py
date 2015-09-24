from django.views.generic import ListView, DetailView

from fun.utils import mako

from universities.models import University
from universities.courses_utils import get_university_courses


class UniversityLandingView(mako.MakoTemplateMixin, ListView):
    template_name = 'universities/index.html'
    context_object_name = 'universities'

    def get_queryset(self):
        return University.objects.have_page()


class UniversityDetailView(mako.MakoTemplateMixin, DetailView):
    template_name = 'universities/detail.html'
    context_object_name = 'university'

    def get_queryset(self):
        return University.objects.have_page()

    def get_context_data(self, **kwargs):
        context = super(UniversityDetailView, self).get_context_data(**kwargs)
        context['courses'] = get_university_courses(
            user=self.request.user,
            university_code=self.object.code
        )
        return context


university_landing = UniversityLandingView.as_view()
university_detail = UniversityDetailView.as_view()
