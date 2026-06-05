import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Quiniela, Seleccion, Participante


class QuinielaConsumer(AsyncWebsocketConsumer):
    salas = {}  # {slug: {channel_name: nombre}}

    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'quiniela_{self.slug}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        QuinielaConsumer.salas.setdefault(self.slug, {})[self.channel_name] = None
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'join':
            nombre = data.get('nombre', 'Anónimo')
            await self._save_participante(nombre)
            QuinielaConsumer.salas[self.slug][self.channel_name] = nombre
            await self._broadcast_users()

        elif data.get('type') == 'start_draw':
            await self._handle_start_draw()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        QuinielaConsumer.salas.get(self.slug, {}).pop(self.channel_name, None)
        if not QuinielaConsumer.salas.get(self.slug):
            QuinielaConsumer.salas.pop(self.slug, None)
        else:
            await self._broadcast_users()

    @database_sync_to_async
    def _save_participante(self, nombre):
        quiniela = Quiniela.objects.get(slug=self.slug)
        Participante.objects.get_or_create(quiniela=quiniela, nombre=nombre)

    async def _handle_start_draw(self):
        result = await self._perform_draw()
        if 'error' in result:
            await self.send(text_data=json.dumps({'type': 'error', 'message': result['error']}))
            return

        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'draw.started', 'resultados': result['resultados']}
        )

    @database_sync_to_async
    def _perform_draw(self):
        quiniela = Quiniela.objects.get(slug=self.slug)


        participantes = list(quiniela.participantes.all())
        num_participantes = len(participantes)

        if num_participantes < quiniela.numero_participantes:
            return {'error': f'Faltan participantes ({num_participantes}/{quiniela.numero_participantes})'}

        selecciones = list(Seleccion.objects.order_by('id'))
        num_selecciones_por_participante = len(selecciones) // num_participantes

        # Dividir en bombos y tomar una selección aleatoria por bombo para cada participante
        bombos = [
            selecciones[i * num_participantes:(i + 1) * num_participantes]
            for i in range(num_selecciones_por_participante)
        ]

        resultados = []
        for bombo in bombos:
            random.shuffle(bombo)
            for i, participante in enumerate(participantes):
                participante.selecciones.add(bombo[i])

        quiniela.sorteada = True
        quiniela.save()

        for participante in participantes:
            resultados.append({
                'participante_id': participante.id,
                'participante': participante.nombre,
                'selecciones': [
                    {'id': s.id, 'nombre': s.nombre}
                    for s in participante.selecciones.all()
                ],
            })

        return {'resultados': resultados}

    async def _broadcast_users(self):
        users = [n for n in QuinielaConsumer.salas.get(self.slug, {}).values() if n]
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'quiniela.users', 'users': users}
        )

    async def quiniela_users(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users'],
            'count': len(event['users']),
        }))

    async def draw_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'draw_started',
            'resultados': event['resultados'],
        }))
