# -*- coding: utf-8 -*-

from django.conf import settings
import django.http
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from edxmako.shortcuts import render_to_response

from microsite_configuration import microsite

from fun.utils import mako
from fun.utils.views import staff_required

from . import models


def top_news(count=5):
    """Return Top count news if available or fill result list with None for further boolean evaluation."""
    articles = ArticleListView().get_queryset_for_site()
    return [articles[idx] if len(articles) > idx else None for idx in range(count)]

class StaffOnlyView(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_staff:
            raise django.http.Http404
        return super(StaffOnlyView, self).dispatch(request, *args, **kwargs)


def filter_queryset_for_site(queryset):
    if settings.FEATURES['USE_MICROSITES']:
        queryset = queryset.filter(microsite=microsite.get_value('SITE_NAME'))
    return queryset

class ArticleListView(mako.MakoTemplateMixin, ListView):
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
        queryset = queryset.filter(featured_section__isnull=True)

        return queryset

    def get_queryset_for_site(self):
        return filter_queryset_for_site(self.get_viewable_queryset())

    def get_viewable_queryset(self):
        return models.Article.objects.viewable()
article_list = ArticleListView.as_view()


class ArticleListPreviewView(StaffOnlyView, ArticleListView):
    def get_viewable_queryset(self):
        return models.Article.objects.published_or(slug=self.kwargs['slug'])
article_list_preview = ArticleListPreviewView.as_view()


def article_detail(request, slug):
    return render_article(models.Article.objects.published(), slug)

@staff_required
def article_preview(request, slug):
    return render_article(models.Article.objects.all(), slug)

def render_article(queryset, slug):
    article = get_object_or_404(filter_queryset_for_site(queryset), slug=slug)

    url = 'https://%s%s' % (settings.LMS_BASE, article.get_absolute_url())
    twitter_action = 'https://twitter.com/intent/tweet?text=Actu+%s:+%s+%s' % (
            settings.PLATFORM_TWITTER_ACCOUNT,
            article.title,
            url)
    facebook_action = 'http://www.facebook.com/share.php?u=%s' % (url)
    email_subject = u"mailto:?subject=Actualité France Université Numérique: %s&body=%s" % (
            article.title, url)
    category_articles = []
    if article.category:
        category_articles = list(queryset.filter(category__slug=article.category.slug)[:3])
    featured_news = queryset[:3]

    return render_to_response('newsfeed/article/detail.html', {
        'article': article,
        'article_courses': list(article.courses.all()),
        'article_links': list(article.links.all()),
        'category_articles': category_articles,
        'twitter_action': twitter_action,
        'email_subject': email_subject,
        'facebook_action': facebook_action,
        'featured_news': featured_news,
    })
