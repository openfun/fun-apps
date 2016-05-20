# -*- coding: utf-8 -*-

from opaque_keys.edx.keys import AssetKey
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore

CERTIFICATE_SCHEMA_VERSION = 1

# This is a slighly modified copy of edx-platform/cms/djangoapps/contentstore/views/tests/test_certificates.py:HelperMethods
# that we can not import from lms context


# pylint: disable=no-member
class HelperMethods(object):
    """
    Mixin that provides useful methods for certificate configuration tests.
    """
    def _create_fake_images(self, asset_keys):
        """
        Creates fake image files for a list of asset_keys.
        """
        for asset_key_string in asset_keys:
            asset_key = AssetKey.from_string(asset_key_string)
            content = StaticContent(
                asset_key, "Fake asset", "image/png", "data",
            )
            contentstore().save(content)

    def _add_course_certificates(self, count=1, signatory_count=0):
        """
        Create certificate for the course.
        """
        signatories = [
            {
                'name': 'Name ' + str(i),
                'title': 'Title ' + str(i),
                'signature_image_path': '/c4x/test/CSS101/asset/Signature{}.png'.format(i),
                'organization': 'FUN',
                'id': i
            } for i in xrange(0, signatory_count)

        ]

        # create images for signatory signatures except the last signatory
        for idx, signatory in enumerate(signatories):
            if len(signatories) > 2 and idx == len(signatories) - 1:
                continue
            else:
                self._create_fake_images([signatory['signature_image_path']])

        certificates = [
            {
                'id': i,
                'name': 'Name ' + str(i),
                'description': 'Description ' + str(i),
                'org_logo_path': '/c4x/test/CSS101/asset/org_logo{}.png'.format(i),
                'signatories': signatories,
                'version': CERTIFICATE_SCHEMA_VERSION,
                'is_active': True
            } for i in xrange(0, count)
        ]
        self._create_fake_images([certificate['org_logo_path'] for certificate in certificates])
        self.course.certificates = {'certificates': certificates}
        self.course.save()
        self.store.update_item(self.course, self.user.id)
