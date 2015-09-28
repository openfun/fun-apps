"""
View which can render and send email from a contact form.
"""

from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView

from contact.forms import ContactForm


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
        return reverse('contact:contact_form_sent')
