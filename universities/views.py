from django.http import Http404

from mako.exceptions import TopLevelLookupException
from edxmako.shortcuts import render_to_response
from django.views.generic import ListView, DetailView

from universities.models import University
from universities.courses import get_university_courses


class MakoTemplateMixin(object):
    """
    A mixin used to render templates with mako
    """
    def render_to_response(self, context, template_name=None, **response_kwargs):
        template_name = template_name or self.template_name
        try:
            response = render_to_response(template_name, context, **response_kwargs)
        except TopLevelLookupException:
            raise Http404("Template " + template_name + " not found")
        else:
            return response


class UniversityMixin(object):

    def get_queryset(self):
        return University.objects.filter(featured=True)


class UniversityLandingView(MakoTemplateMixin, UniversityMixin, ListView):
    template_name = 'universities/index.html'
    context_object_name = 'universities'


class UniversityDetailView(MakoTemplateMixin, UniversityMixin, DetailView):
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
