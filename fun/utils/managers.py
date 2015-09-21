from django.db import models


class ChainableManager(models.Manager):
    '''
    Helps providing chainability: `MyModel.objects.published().start_soon()`.
    Filter methods defined in Django Manager class cannot be chained to each other.
    Instead of adding our new filters to the custom manager, we add them to a custom
    queryset. But we still want to be able to access them as methods of the manager.
    '''
    queryset_class = None

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


