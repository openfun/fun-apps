from django.conf.urls import patterns, url

from contact import views

# namespace='contact'

urlpatterns = patterns(
    '',
    url(r'^contact$', views.ContactFormView.as_view(), name="contact"),
    url(r'^contact/sent/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'contact/contact_form_sent.html'}, name='contact_form_sent'),
)
