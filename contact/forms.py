
# Imports ###########################################################

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from contact_form.forms import ContactForm as BaseContactForm


class ContactForm(BaseContactForm):
    email = forms.EmailField(max_length=100, label=_('Email address'),
                             widget=forms.TextInput(
                                 attrs={"class": "form-control", "placeholder": _('Example: john@example.com')}
                             ))
    name = forms.CharField(max_length=100, label=_('Name'),
                           widget=forms.TextInput(
                               attrs={"class": "form-control", "placeholder": _('Example: John Doe')}
                           ))
    phone = forms.CharField(label=_('Phone number'), required=False, max_length=100,
                           widget=forms.TextInput(
                               attrs={"class": "form-control", "placeholder": _('Example: +33 6 24 01 19 82')}
                           ))
    function = forms.ChoiceField(
        label=_('Function'), required=False, choices=(
            ('', ''),
            ('student', _('Student')),
            ('teacher', _('Teacher')),
            ('teaching engineer', _('Teaching Engineer')),
            ('researcher', _('Researcher')),
            ('journalist', _('Journalist')),
            ('other', _('Other')),
        ),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    inquiry = forms.ChoiceField(
        label=_('My request is about'), choices=(
            ('', ''),
            ('registration', _('Registration and activation')),
            ('tech-support', _('Technology problem')),
            ('accessibility', _('Accessibility for students with disabilities')),
            ('certification', _('Certification and exams')),
            ('account', _('My account')),
            ('institutional', _('Business developement or institutional inquiry')),
            ('other', _('Other')),
        ),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}), label=_('Message'))

    recipient_list = [settings.CONTACT_EMAIL]
    subject = _('Contact request - {}').format(settings.PLATFORM_NAME)

    def sorted_fields(self):
        return [
            self["email"],
            self["name"],
            self["phone"],
            self["function"],
            self["inquiry"],
            self["body"],
        ]

    @property
    def from_email(self):
        return self.cleaned_data['email']
