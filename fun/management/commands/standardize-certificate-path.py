from optparse import make_option

from django.core.management.base import BaseCommand

from certificates.models import GeneratedCertificate


class Command(BaseCommand):
    help = """Standardize certificate path.

           Remove the static string from the certificate path.

           Example:
               `/static/attestations/attestation.pdf` become
               `/attestations/attestation.pdf`
           Usage:
               ./manage.py standardize_certificate_path --settings=.. [--dry-run]
           """

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', dest='dry-run', action="store_true", default=False),)

    def handle(self, *args, **options):
        certificates = GeneratedCertificate.objects.filter(download_url__startswith='/static/')
        self.stdout.write("{} certificates path will be modified\n".format(len(certificates)))
        path_modified = 0
        for certificate in certificates:
            path_modified += 1
            certificate.download_url = certificate.download_url[7:]
            if not options['dry-run']:
                certificate.save()
        self.stdout.write("{} certificates have been modified\n".format(path_modified))
