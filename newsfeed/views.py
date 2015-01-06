import django.http
from django.views.generic import ListView, DetailView

from fun.utils import mako

from . import models


class StaffOnlyView(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            raise django.http.Http404
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


class ArticleListView(mako.MakoTemplateMixin, ListView):
    template_name = 'newsfeed/article/list.html'
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['featured_section'] = models.FeaturedSection.get_solo()
        return context

    def get_queryset(self):
        # Display all published articles. We might want to filter on language
        # and limit the queryset to the first n results in the future (see the
        # .featured() method).
        queryset = models.Article.objects.viewable()
        # We exclude the article that's selected in the featured section.
        featured_section = models.FeaturedSection.get_solo()
        if featured_section and featured_section.article:
            queryset = queryset.exclude(id=featured_section.article.id)
        return queryset
article_list = ArticleListView.as_view()


class ArticleListPreviewView(StaffOnlyView, ArticleListView):
    def get_queryset(self):
        return models.Article.objects.published_or(slug=self.kwargs['slug'])
article_list_preview = ArticleListPreviewView.as_view()


class ArticleDetailView(mako.MakoTemplateMixin, DetailView):
    template_name = 'newsfeed/article/detail.html'
    context_object_name = 'article'
    model = models.Article

    def get_queryset(self):
        return models.Article.objects.published()
article_detail = ArticleDetailView.as_view()


class ArticlePreviewView(StaffOnlyView, ArticleDetailView):
    def get_queryset(self):
        return models.Article.objects
article_preview = ArticlePreviewView.as_view()
