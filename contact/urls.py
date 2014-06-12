from django.conf.urls import patterns, url

from contact import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ContactFormView.as_view(), name="contact"),
    url(r'^sent/$',
        'static_template_view.views.render', {'template': '../contact_form/contact_form_sent.html'},
        name='contact_form_sent'),
)
