# -*- coding: utf-8 -*-

from django.conf import settings
import django.http
from django.views.generic import ListView, DetailView

from microsite_configuration import microsite

from fun.utils import mako

from . import models


def top_news(count=5):
    """Return Top count news if available or fill result list with None for further boolean evaluation."""
    articles = ArticleListView().get_queryset_for_site()
    return [articles[idx] if len(articles)>idx else None for idx in range(count)]

class StaffOnlyView(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            raise django.http.Http404
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


class MicrositeArticleMixin(object):
    def filter_queryset_for_site(self, queryset):
        if settings.FEATURES['USE_MICROSITES']:
            queryset = queryset.filter(microsite=microsite.get_value('SITE_NAME'))
        return queryset

class ArticleListView(mako.MakoTemplateMixin, ListView, MicrositeArticleMixin):
    template_name = 'newsfeed/article/list.html'
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['featured_section'] = models.FeaturedSection.get_solo()
        return context

    def get_queryset(self):
        # Note: We might want to filter on language and limit the queryset to
        # the first n results in the future (see the .featured() method).
        queryset = self.get_queryset_for_site()

        # We exclude the article that's selected in the featured section.
        featured_section = models.FeaturedSection.get_solo()
        if featured_section and featured_section.article:
            queryset = queryset.exclude(id=featured_section.article.id)

        return queryset

    def get_queryset_for_site(self):
        return self.filter_queryset_for_site(self.get_viewable_queryset())

    def get_viewable_queryset(self):
        return models.Article.objects.viewable()
article_list = ArticleListView.as_view()


class ArticleListPreviewView(StaffOnlyView, ArticleListView):
    def get_viewable_queryset(self):
        return models.Article.objects.published_or(slug=self.kwargs['slug'])
article_list_preview = ArticleListPreviewView.as_view()


class ArticleDetailView(mako.MakoTemplateMixin, DetailView, MicrositeArticleMixin):
    template_name = 'newsfeed/article/detail.html'
    context_object_name = 'article'
    model = models.Article

    def get_queryset(self):
        return self.filter_queryset_for_site(models.Article.objects.published())
article_detail = ArticleDetailView.as_view()


class ArticlePreviewView(StaffOnlyView, ArticleDetailView):
    def get_queryset(self):
        return self.filter_queryset_for_site(models.Article.objects.all())
article_preview = ArticlePreviewView.as_view()
