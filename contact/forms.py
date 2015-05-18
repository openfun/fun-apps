
# Imports ###########################################################

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, pgettext

from contact_form.forms import ContactForm as BaseContactForm


# Classes ###########################################################

class ContactForm(BaseContactForm):
    name = forms.CharField(max_length=100, label=pgettext('contact-form', 'Name'))
    email = forms.EmailField(max_length=200, label=_('Email'))
    body = forms.CharField(widget=forms.Textarea, label=_('Body'))
    phone = forms.CharField(label=_('Phone'), required=False, max_length=100)
    function = forms.ChoiceField(label=_('Function'), required=False, choices=(
            ('', ''),
            ('student', _('Student')),
            ('teacher', _('Teacher')),
            ('teaching engineer', _('Teaching Engineer')),
            ('researcher', _('Researcher')),
            ('journalist', _('Journalist')),
            ('other', _('Other')),
        ))
    inquiry = forms.ChoiceField(label=_('Inquiry type'), choices=(
            ('', ''),
            ('registration', _('Registration and activation')),
            ('tech-support', _('Technology problem')),
            ('accessibility', _('Accessibility for students with disabilities')),
            ('certification', _('Certification and exams')),
            ('account', _('My account')),
            ('institutional', _('Business developement or institutional inquiry')),
            ('other', _('Other')),
        ))

    recipient_list = [settings.CONTACT_EMAIL]
    subject = _('Contact request - {}').format(settings.PLATFORM_NAME)

    @property
    def from_email(self):
        return self.cleaned_data['email']
