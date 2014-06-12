
# Imports ###########################################################

from django import template

from contact.forms import ContactForm


# Globals ###########################################################

register = template.Library()


# Functions #########################################################

@register.filter
def field_label(value, field_name):
    form = ContactForm(request='')
    return dict(form.fields[field_name].choices)[value]
