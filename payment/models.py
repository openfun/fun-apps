# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import get_language, ugettext_lazy as _
from django.conf import settings
from docutils.core import publish_string
from pyquery import PyQuery as S
import datetime

PAYMENT_TERMS = 'verified_certificate'
MARKER = object()
## Seen with legal department it is the language of the juridiction that
## mmanages the hosting
DEFAULT_LANGUAGE = "fr"
DEFAULT_LANGUAGE_NAME = _("French")

TERMS_TEMPLATE = """
.. Ce champs est dans un format ReST (comme un wiki)
.. Ceci est un commentaire
.. http://deusyss.developpez.com/tutoriels/Python/SphinxDoc/#LIV-G


.. Les 4 lignes finales (honor, privacy, tos, legal)
.. permettent la navigation dans le contrat au niveau des ancres
.. Prière de les insérer avant les titres correspondant
.. honor = Charte utilisateurs
.. privacy = Politique de confidentialité
.. tos = Conditions générales d'utilisation
.. legal =  Mentions légales

.. Ces commentaires ci dessus peuvent être retirés
.. ils sont juste là comme aide mémoire :)


.. _honor:

.. _privacy:

.. _tos:

.. _legal:

"""

class TermsAndConditions(models.Model):
    name = models.CharField(
        max_length=100, verbose_name=_(u"Name"),
        default=PAYMENT_TERMS, db_index=True,
    )
    version = models.CharField(max_length=12, verbose_name=_(u"Terms and conditions version (semver)"))
    datetime = models.DateTimeField(default=datetime.datetime.now, verbose_name=_(u"Acceptance date"), db_index=True)
    text = models.TextField(verbose_name=_(u"Terms and conditions content (HTML allowed)"))

    def __unicode__(self):
        return u"%s v%s" % (self.name, self.version)

    class Meta:
        verbose_name = _(u"Terms and conditions")
        verbose_name_plural = _(u"Terms and conditions")
        ordering = ('-datetime',)

    def tr_text(self):
        """
        use django i18n mechanism to search for the right translation to
        present to the user. (order = user settings, cookies ...)
        Defaults to the one of reference for the country of reference if None
        available
        """
        language = get_language()
        good_one = language in settings.LANGUAGES \
            and language \
            or DEFAULT_LANGUAGE
        just_in_case=""
        to_return = None,None
        for translated_term in self.texts.all():
            if translated_term.language == language and len(translated_term.tr_text):
                to_return = unicode(translated_term.tr_text), translated_term.language
            if translated_term.language == DEFAULT_LANGUAGE:
              just_in_case = unicode(translated_term.tr_text),DEFAULT_LANGUAGE
        ## walking around ReST generating a 4.1 full html doc
        ## Accessibility
        text, lang = to_return if to_return[0] else just_in_case
        res = S(
                    "body",
                    publish_string(
                        text,
                        writer_name='html'
                    ),
                    parser='html',
        )
        res.remove_namespaces()
        doc = res.find(".document")[0]
        res(".document").attr["lang"] = lang
        return res.html()

    tr_text = text = property(tr_text)

    @classmethod
    def version_accepted(cls, name, user):
        try:
            return UserAcceptance.objects.filter(terms__name=name, user=user).latest('datetime')
        except UserAcceptance.DoesNotExist:
            return None

    @classmethod
    def get_latest(cls, name=MARKER, language = MARKER):
        if name is MARKER:
            name = PAYMENT_TERMS
        try:
            return TermsAndConditions.objects.filter(name=name).latest('datetime')
        except TermsAndConditions.DoesNotExist:
            return None

    @classmethod
    def user_has_to_accept_new_version(cls, name, user):
        # if name is None take the one that values
        name = name or PAYMENT_TERMS
        latest = TermsAndConditions.get_latest(name=name)
        if latest is None:
            return False  # terms do not exists yet, user is ok
        if latest.version == '0':  # terms of version 0 are considered as accepted
            return False
        accepted = TermsAndConditions.version_accepted(name, user)
        if accepted and accepted.terms.version == latest.version:
            return False   # user already has accepted latest version
        else:
            return latest  # user has to accept latest version

    def accept(self, user):
        accepted, created = UserAcceptance.objects.get_or_create(terms=self, user=user)
        if not created:
            if accepted.terms == self:
                return False  # user has already accepted those terms
            accepted.terms = self  # update accepted version
            accepted.save()
        return True


class UserAcceptance(models.Model):
    user = models.ForeignKey(User, related_name='terms_accepted')
    terms = models.ForeignKey(TermsAndConditions, related_name='accepted')
    datetime = models.DateTimeField(auto_now=True, verbose_name=_(u"Acceptance date"), db_index=True)

    def __unicode__(self):
        return u"%s: %s v%s" % (self.user.username, self.terms.name, self.terms.version)

    class Meta:
        verbose_name = _(u"User terms and conditions acceptance")
        unique_together = ['user', 'terms']

def legal_acceptance(user):
    COMPLIANT, NOT_COMPLIANT = True, False
    if user.is_anonymous():
        return COMPLIANT
    latest = TermsAndConditions.get_latest()
    if latest is None or latest == TERMS_TEMPLATE:
        return COMPLIANT
    try:
        latest_acceptation = UserAcceptance.objects.get(
            terms=latest,
            user=user,
        )
    except UserAcceptance.DoesNotExist:
        return NOT_COMPLIANT
    return COMPLIANT

class TranslatedTerms(models.Model):
    """Terms and conditions might have to be made available to
    any students for whom we support their language.
    """
    # XXX: use the same language as Studio
    tr_text = models.TextField(
        verbose_name=_( u"Terms and conditions.") + u" (ReStructured Text)",
        default = TERMS_TEMPLATE,
    )
    language = models.CharField(
        max_length=5,
        verbose_name=_(u"Language"),
        choices=settings.LANGUAGES,
        default={ _("french") : "fr" }
    )
    term = models.ForeignKey(
        TermsAndConditions,
        related_name = "texts",
        on_delete = models.CASCADE
    )
    def __repr__(slef):
        return u"term %d - %s" % ( slef.term.id, slef.language)

    class Meta:
        unique_together = (('term', 'language', ), )
