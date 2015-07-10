# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render

from .utils import get_fun_faq_collection


def index(request):

    # Query mongo to build faq structure
    faq = get_fun_faq_collection()
    article_tree = faq.distinct('category')
    for category in article_tree:
        category['sections'] = faq.find({'category.id': category['id']}).distinct('section')
        for section in category['sections']:
            section['articles'] = faq.find({'section.id': section['id']})

    return render(request, 'faq/faq.html', {
        'article_tree': article_tree,
    })


def article(request, article_id):

    faq = get_fun_faq_collection()
    article = faq.find_one({'id': int(article_id)})
    if not article:
        raise Http404

    return render(request, 'faq/article.html', {
        'article': article,
    })
