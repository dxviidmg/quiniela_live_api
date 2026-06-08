import logging

import mercadopago
from django.conf import settings
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Quiniela, Seleccion, Participante, DIVISORES_48
from .serializers import QuinielaSerializer, ParticipanteSerializer, SeleccionSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_preference(request):
    pool_id = request.data.get('pool_id')
    lobby_url = request.data.get('lobby_url')
    
    if not pool_id or not lobby_url:
        return Response({'error': 'pool_id y lobby_url son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    preference_data = {
        "items": [{
            "title": "Seguimiento Premium con Amigos – Quina Live",
            "quantity": 1,
            "unit_price": 10,
            "currency_id": "MXN",
        }],
        "back_url": f"{settings.FRONTEND_URL}{lobby_url}",
        "auto_return": "approved",
        "external_reference": pool_id,
    }
    
    result = sdk.preference().create(preference_data)
    
    if result.get("status") != 200 and result.get("status") != 201:
        error_msg = result.get("response", {}).get("message", "Error desconocido de Mercado Pago")
        return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
    
    init_point = result.get("response", {}).get("init_point")
    if not init_point:
        return Response({"error": "No se pudo crear la preferencia de pago"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"init_point": init_point})


@api_view(['GET'])
def paises_por_bombo(request):
    participantes = request.query_params.get('participantes')
    if not participantes or int(participantes) not in DIVISORES_48:
        return Response({'error': f'participantes debe ser uno de {DIVISORES_48}'}, status=status.HTTP_400_BAD_REQUEST)
    participantes = int(participantes)
    selecciones = list(Seleccion.objects.order_by('id'))
    num_bombos = len(selecciones) // participantes
    resultado = {}
    for i in range(num_bombos):
        grupo = selecciones[i * participantes:(i + 1) * participantes]
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
