import factory
from factory import fuzzy

from ..models import TermsAndConditions, TranslatedTerms


class TranslatedTermsFactory(factory.DjangoModelFactory):

    tr_text = fuzzy.FuzzyText(length=255)
    language = 'fr'

    class Meta(object):
        model = TranslatedTerms


class TermsAndConditionsFactory(factory.DjangoModelFactory):
    name = name = fuzzy.FuzzyText(length=20)
    version = factory.Sequence("{0}".format)
    text = fuzzy.FuzzyText(length=255)

    translated_terms = factory.RelatedFactory(TranslatedTermsFactory, 'term')

    class Meta(object):
        model = TermsAndConditions
