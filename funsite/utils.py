# -*- coding: utf-8 -*-

from collections import namedtuple

from django.utils.translation import pgettext, ugettext as _

BreadcrumbsItem = namedtuple('BreadcrumbsItem', ['path', 'name'])


def breadcrumbs(url, current_page):
    """
    Returns a BreadcrumbsItem list of pairs (path, i18ned name) of length from 2 to 3
    as the breadcrumb for current url
    The tricky part is the replacement of edX's courses page by our.
    When length is 3. The first item is the home page.
            The last item is the current page. The middle item, if present, points to the parent
            page of the current page.
    See tests.test_breadcrumbs to understand awaited behaviour
    """
    mapping = {
        'contact': _("Contact"),
        'courses': _("All courses"),    # edX page
        'cours': _("All courses"),      # FUN page
        'news': pgettext("fun-news", "News"),
        'universities': _("Universities"),
    }
    result = [BreadcrumbsItem(path='/', name=_(u"Home"))]

    items = url.split('/')[1:]  # split and remove first backslash

    if len(items) > 1 and items[1] and items[0] != 'accounts':
        if items[0] == 'courses':
            items[0] = 'cours'

        result.append(BreadcrumbsItem(path='/%s/' % items[0], name=mapping[items[0]]))

    result.append(BreadcrumbsItem(path='#', name=current_page))
    return result

