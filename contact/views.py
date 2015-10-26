from django.core.urlresolvers import reverse

import contact_form.views

from contact.forms import ContactForm


class ContactFormView(contact_form.views.ContactFormView):
    form_class = ContactForm
    template_name = 'contact/contact_form.html'

    def get_success_url(self):
        return reverse('contact:contact_form_sent')
