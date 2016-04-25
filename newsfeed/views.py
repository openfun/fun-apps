# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext_lazy as _

from edxmako.shortcuts import render_to_response

from pure_pagination import Paginator, EmptyPage
from microsite_configuration import microsite

from fun.utils.views import staff_required

from . import models



ARTICLES_PER_PAGE = 10

def get_articles():
    """
    List viewable articles for the current site.

    Note: We might want to filter on language and limit the queryset to the
    first n results in the future (see the .featured() method).

    Returns:
        queryset
    """
    return filter_queryset_for_site(models.Article.objects.viewable())

def paginate(queryset, page_nb, article_per_page):
    """
    Returns :
     * a page (a slice of the queryset), with the asked number of articles, at the right offset.
     * the featured article if the first page is asked or None otherwise

    Note: we use pure_pagination to handle all the complex stuff
    """

    featured = None
    if page_nb == 1:
        featured = queryset[:1]
        featured = featured[0] if len(featured) > 0 else None

    queryset = queryset[1:]
    paginator = Paginator(queryset, article_per_page)

    try:
        paginated = paginator.page(page_nb)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated = paginator.page(paginator.num_pages)

    return paginated, featured


def top_news(count=5):
    """Return Top count news if available or fill result list with None for further boolean evaluation."""
    articles = get_articles()[:count]
    return [articles[idx] if len(articles) > idx else None for idx in range(count)]

def article_list(request):
    # We exclude the article that's selected in the featured section.
    return render_articles(get_articles(), request.GET)

@staff_required
def article_list_preview(request, slug):
    qs = filter_queryset_for_site(models.Article.objects.published_or(slug=slug))
    return render_articles(qs, request.GET)

def parse_request(get_dict):
    page = get_dict.get("p", "")
    page = int(page) if page.isdigit() else 1
    nb_items = get_dict.get("n", "")
    nb_items = int(nb_items) if nb_items.isdigit() else ARTICLES_PER_PAGE
    return page, nb_items

def render_articles(articles_queryset, get_dict):
    page, nb_items = parse_request(get_dict)
    articles, featured = paginate(articles_queryset, page, nb_items)

    start = 1 + (page-1)*nb_items + (0 if articles.number==1 else 1)
    end = len(articles.object_list) + start - (1 if articles.number!=1 else 0)

    return render_to_response('newsfeed/article/list.html', {
        'articles': articles,
        "featured_article": featured,
        'nb_items': {"start": start, "end": end},
    })

def filter_queryset_for_site(queryset):
    if settings.FEATURES['USE_MICROSITES']:
        queryset = queryset.filter(microsite=microsite.get_value('SITE_NAME'))
    return queryset


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
    email_subject = u"mailto:?subject=Actualité FUN: %s&body=%s" % (
            article.title, url)
    category_articles = []
    queryset = queryset.exclude(id=article.id)
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


class NewsFeed(Feed):
    title = _(u"Fun latest published news")
    link = "/news/feed/"
    description = _(u"Latests news published on fun-mooc.fr")
    feed_type = Rss201rev2Feed
    __name__ = 'FUNNEWSRSS'

    def get_site(self):
        protocol = 'https://'
        site = settings.SITE_NAME
        return protocol, site

    def items(self, request):
        return models.Article.objects.published()

    def item_title(self, article):
        return article.title

    def item_link(self, article):
        return article.get_absolute_url()

    # This will be rendered by aggregators
    def item_description(self, article):
        protocol, site = self.get_site()
        return render_to_string('newsfeed/feed/feed.html', {
                'article': article,
                'protocol': protocol,
                'site': site,
                })
