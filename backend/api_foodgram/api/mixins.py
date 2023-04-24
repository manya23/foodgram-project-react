from rest_framework import mixins, viewsets


class BaseGetView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    pass
