# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

from microsite_configuration import microsite

from newsfeed.models import Article

from ..forms import ArticleForm
from ..utils import group_required, order_and_paginate_queryset


@group_required('fun_backoffice')
def news_list(request):
    articles = Article.objects.all().order_by('-created_at')
    if settings.FEATURES['USE_MICROSITES']:
        articles = articles.filter(microsite=microsite.get_value('SITE_NAME'))

    articles = order_and_paginate_queryset(request, articles, 'created_at')

    return render(request, 'backoffice/articles.html', {
        'articles': articles,
        'tab': 'news',
    })


@group_required('fun_backoffice')
def news_detail(request, news_id=None):
    if news_id:
        search_query = {
            'id': news_id
        }
        if settings.FEATURES['USE_MICROSITES']:
            search_query['microsite'] = microsite.get_value('SITE_NAME')
        article = get_object_or_404(Article, **search_query)
    else:
        article = None

    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES, instance=article)
        if form.is_valid():
            form.save()
            if article is None:
                return redirect('backoffice:news-detail', news_id=form.instance.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'backoffice/article.html', {
        'form': form,
        'tab': 'news',
    })
