from django.core.management import call_command

from certificates.tests.factories import GeneratedCertificateFactory
from certificates.models import CertificateStatuses
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms
from certificates.models import GeneratedCertificate

@skipUnlessLms
class StandardizeCertificatePathTestCase(ModuleStoreTestCase):
    def test_standardize_certifiacte_path(self):
        GeneratedCertificateFactory(user=UserFactory(),
                                    status=CertificateStatuses.downloadable,
                                    download_url='/static/attestations/attestation.pdf')
        call_command('standardize-certificate-path')
        certificate = GeneratedCertificate.objects.get()
        self.assertEqual(certificate.download_url, '/attestations/attestation.pdf')
