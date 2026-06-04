from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Quiniela, Seleccion, Participante, Bombo
from .serializers import QuinielaSerializer, ParticipanteSerializer, BomboSerializer


class BomboViewSet(ListModelMixin, GenericViewSet):
    queryset = Bombo.objects.prefetch_related('seleccion_set').all()
    serializer_class = BomboSerializer


class QuinielaViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Quiniela.objects.all()
    serializer_class = QuinielaSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['post'])
    def unirse(self, request, slug=None):
        quiniela = self.get_object()
        if quiniela.sorteada:
            return Response({'error': 'La quiniela ya fue sorteada'}, status=status.HTTP_400_BAD_REQUEST)
        if quiniela.participantes.count() >= quiniela.numero_participantes:
            return Response({'error': 'Lugares llenos'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ParticipanteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(quiniela=quiniela)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def sortear(self, request, slug=None):
        quiniela = self.get_object()
        if quiniela.sorteada:
            return Response({'error': 'Ya fue sorteada'}, status=status.HTTP_400_BAD_REQUEST)
        if quiniela.participantes.count() != quiniela.numero_participantes:
            return Response({'error': 'Faltan jugadores'}, status=status.HTTP_400_BAD_REQUEST)

        asignaciones = request.data.get('asignaciones', [])
        for asignacion in asignaciones:
            participante = quiniela.participantes.get(id=asignacion['participante_id'])
            participante.selecciones.set(asignacion['selecciones_ids'])

        quiniela.sorteada = True
        quiniela.save()
        return Response(QuinielaSerializer(quiniela).data)
