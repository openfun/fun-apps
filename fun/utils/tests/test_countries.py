from django.test import TestCase
from django.utils.translation import ugettext as _

from fun.utils import countries


class CountriesTests(TestCase):

    def test_get_country_name(self):
        self.assertEqual(_("France"), countries.get_country_name('FR'))
        self.assertEqual(_("Unknown"), countries.get_country_name(countries.UNKNOWN_COUNTRY_CODE))

    def test_territory_country(self):
        self.assertEqual('FR', countries.territory_country('FR'))
        self.assertEqual('FR', countries.territory_country('GP'))
        self.assertEqual('NL', countries.territory_country('NL'))
        # XZ does not exist
        self.assertEqual(countries.UNKNOWN_COUNTRY_CODE, countries.territory_country('XZ'))
