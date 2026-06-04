from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from .models import Quiniela
from .serializers import QuinielaSerializer


class QuinielaViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Quiniela.objects.all()
    serializer_class = QuinielaSerializer
    lookup_field = 'slug'
