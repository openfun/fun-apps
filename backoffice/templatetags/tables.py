# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

register = template.Library()


class OrderTableNode(template.Node):

    def __init__(self, col_name, col_title, tooltip, table_name):
        super(OrderTableNode, self).__init__()
        self.col_name = template.Variable(col_name)
        self.col_title = template.Variable(col_title)
        self.tooltip = template.Variable(tooltip)
        try:
            self.table_name = template.Variable(table_name)
        except IndexError:
            self.table_name = None

    def render(self, context):
        col_name = self.col_name.resolve(context)
        col_title = self.col_title.resolve(context)
        tooltip = self.tooltip.resolve(context)
        if self.table_name:
            table_name = self.table_name.resolve(context) + '-'
        else:
            table_name = ''
        query = context['request'].GET.copy()
        query[table_name + 'order'] = col_name
        css_class, glyph = '', ''
        if table_name + 'order' in query:
            if context['request'].GET.get(table_name + 'order') == col_name:
                css_class = 'colactive'
                if 'd' in context['request'].GET:
                    glyph = '<i class="glyphicon glyphicon-chevron-up"></i>'
                else:
                    glyph = '<i class="glyphicon glyphicon-chevron-down"></i>'

            if query[table_name + 'order'] == col_name:
                if table_name + 'd' in query:
                    del query[table_name + 'd']
                else:
                    query[table_name + 'd'] = '1'
        else:
            query[table_name + 'order'] = col_name
        s = '<a class="%s"  href="?%s" title="%s">%s%s</a>' % (css_class, query.urlencode(),
                force_unicode(_(tooltip)) if tooltip else '',
                force_unicode(_(col_title)),
                glyph,
                )
        return s


@register.tag
def order_col(parser, token):
    """Returns a html link to sort table column maintaining other filters

    Arguments:
        column_name: str, fieldname to order by
        column_title: str, fieldname to order by title to i18n
        tooltip: str, will add a `title`property to `<a>
        table_name: str, optionaly specify table name (allow multiple tables sorting)
        {% order column_name column_title %}
    URL arguments:
        [table_name-]order: str, fieldname
        [table_name-]d: str, reverse order flag, if set the view will sort asc else desc
        Other URL arguments are appened to created URL

    """
    try:
        tokens = token.split_contents()
        col_name = tokens[1]
        col_title = tokens[2]
        tooltip = tokens[3]
        table_name = tokens[4] if len(tokens) > 4 else ''

    except IndexError:
        raise template.TemplateSyntaxError("%r tag requires at least 2 arguments" % token.contents.split()[0])

    return OrderTableNode(col_name, col_title, tooltip, table_name)
