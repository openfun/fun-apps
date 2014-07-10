"""
View which can render and send email from a contact form.
"""

# Imports ###########################################################

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

from django.shortcuts import render_to_response

from contact.forms import ContactForm


# Classes ###########################################################

class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'contact/contact_form.html'

    def form_valid(self, form):
        form.save()
        return super(ContactFormView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        return reverse('contact_form_sent')

    def render_to_response(self, context, **response_kwargs):
        context['field_id2name'] = {
            'name': _('Name'),
            'email': _('Email'),
            'body': _('Message'),
            'inquiry': _('Inquiry')
        }
        return render_to_response(self.template_name, context, **response_kwargs)
