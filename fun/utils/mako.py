from django.shortcuts import render_to_response

class MakoTemplateMixin(object):
    """
    A mixin used to render templates with mako
    """
    def render_to_response(self, context, template_name=None, **response_kwargs):
        template_name = template_name or self.template_name
        response = render_to_response(template_name, context, **response_kwargs)
        return response
