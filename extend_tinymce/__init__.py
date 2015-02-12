# -*- coding: utf-8 -*-

"""
Xmodule's JS assets are renamed with content hash by xmodule_assets command run by paver
when compiling all assets (see edx-platform/common/lib/xmodule/xmodule/static_content.py)
Here we replace edit.coffe (which define tinymce configuration) from `html`
xmodule by our own to extend tinymce configuration
`directionality` is the Tinymce plugin which allow writing from right to left,
is not provided by edx, then we have to symlink our version to edx-platform's tinymce plugins folder
(/edx-platform/common/static/js/vendor/tinymce/js/tinymce/plugins/)

"""

import hashlib


def initialize(REPO_ROOT, PIPELINE_JS):
    target = REPO_ROOT / 'common/lib/xmodule/xmodule/js/src/html/edit.coffee'  # original file
    content = file(target, 'r').read()
    file_hash = hashlib.md5(content).hexdigest()  # find out its hash
    for idx, jsfile in enumerate(PIPELINE_JS['module-js']['source_filenames']):
        if file_hash in jsfile:
            PIPELINE_JS['module-js']['source_filenames'][idx] = 'extend_tinymce/html-xmodule.js'  # replace
