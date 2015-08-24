from django.views.generic import ListView, DetailView

from fun.utils import mako

from universities.models import University
from universities.courses import get_university_courses



class UniversityMixin(object):

    def get_queryset(self):
        return University.objects.have_page()


class UniversityLandingView(mako.MakoTemplateMixin, UniversityMixin, ListView):
    template_name = 'universities/index.html'
    context_object_name = 'universities'


class UniversityDetailView(mako.MakoTemplateMixin, UniversityMixin, DetailView):
    template_name = 'universities/detail.html'
    context_object_name = 'university'

    def get_context_data(self, **kwargs):
        context = super(UniversityDetailView, self).get_context_data(**kwargs)
        context['courses'] = get_university_courses(
            user=self.request.user,
            university_code=self.object.code
        )
        return context


university_landing = UniversityLandingView.as_view()
university_detail = UniversityDetailView.as_view()
