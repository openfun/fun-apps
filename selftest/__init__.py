# -*- coding: utf-8 -*-

from django.conf import settings

if settings.USE_DM_CLOUD_VIDEO_PLAYER:
    from django.utils.translation import ugettext as _
    try:  # in lms context, contentstore is not in Python path, furthermore monkeypatch is not necessary
        from contentstore.views.component import _load_mixed_class, get_component_templates as edx_get_component_templates
        from xblock.plugin import PluginMissingError


        def fun_get_component_templates(course):
            """Monkey patch contentstore.views.component.contentstore.views.component.get_component_templates function
            to remove Youtube edX component and replace by our own Dailymotion xblock.
            """

            # retrieve original function result
            component_templates = edx_get_component_templates(course)

            # remove edX video component
            component_templates = [compo for compo in component_templates
                    if compo['type'] != 'video']

            dmcloud_component_template = {"type": "video", "templates": [],
                    "display_name": _("Video")}
            dmcloud_display_name = _load_mixed_class('dmcloud').display_name.default
            dmcloud_component_template['templates'].append({
                'display_name': dmcloud_display_name,
                'category': 'dmcloud',
                'boilerplate_name': None,
                'is_common': False
            })
            component_templates.append(dmcloud_component_template)
            return component_templates

        from contentstore.views import component
        component.get_component_templates = fun_get_component_templates

    except ImportError:
        pass