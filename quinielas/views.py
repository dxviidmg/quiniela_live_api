from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Quiniela, Seleccion, Participante, DIVISORES_48
from .serializers import QuinielaSerializer, ParticipanteSerializer, SeleccionSerializer


@api_view(['GET'])
def paises_por_bombo(request):
    participantes = request.query_params.get('participantes')
    if not participantes or int(participantes) not in DIVISORES_48:
        return Response({'error': f'participantes debe ser uno de {DIVISORES_48}'}, status=status.HTTP_400_BAD_REQUEST)
    participantes = int(participantes)
    selecciones = list(Seleccion.objects.order_by('id'))
    chunk_size = len(selecciones) // participantes
    resultado = {}
    for i in range(participantes):
        grupo = selecciones[i * chunk_size:(i + 1) * chunk_size]
        resultado[f"bombo_{i + 1}"] = SeleccionSerializer(grupo, many=True).data
    return Response(resultado)

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
