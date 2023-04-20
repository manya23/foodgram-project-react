from rest_framework import viewsets, mixins


class BaseGetView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    pass
