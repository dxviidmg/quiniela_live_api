import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Quiniela, Seleccion, Participante


class QuinielaConsumer(AsyncWebsocketConsumer):
    rooms = {}  # {group_name: [{nombre, identificador}]}

    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'quiniela_{self.slug}'
        self.nombre = None

        if self.group_name not in self.rooms:
            self.rooms[self.group_name] = []

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._send_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'join':
            nombre = data.get('nombre', 'Anónimo')
            identificador = data.get('identificador', '')

            nombres_en_sala = [u['nombre'] for u in self.rooms[self.group_name]]
            if nombre in nombres_en_sala:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'El nombre ya está en uso. Elige otro.'}))
                return

            max_participantes = await self._get_max_participantes()
            if len(self.rooms[self.group_name]) >= max_participantes:
                await self.send(text_data=json.dumps({'type': 'error', 'message': f'La quiniela ya está llena ({len(self.rooms[self.group_name])}/{max_participantes}).'}))
                return

            self.nombre = nombre
            self.identificador = identificador
            self.rooms[self.group_name].append({'nombre': nombre, 'identificador': identificador})
            await self._broadcast_users()

        elif data.get('type') == 'start_draw':
            await self._handle_start_draw()

    async def disconnect(self, close_code):
        if self.nombre:
            self.rooms[self.group_name] = [
                u for u in self.rooms.get(self.group_name, []) if u['nombre'] != self.nombre
            ]
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self._broadcast_users()

    async def _send_user_list(self):
        users = [u['nombre'] for u in self.rooms.get(self.group_name, [])]
        await self.send(text_data=json.dumps({'type': 'user_list', 'users': users, 'count': len(users)}))

    async def _broadcast_users(self):
        users = [u['nombre'] for u in self.rooms.get(self.group_name, [])]
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

    @database_sync_to_async
    def _get_max_participantes(self):
        return Quiniela.objects.get(slug=self.slug).numero_participantes

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
        usuarios = self.rooms.get(self.group_name, [])
        num_participantes = len(usuarios)

        if num_participantes < quiniela.numero_participantes:
            return {'error': f'Faltan participantes ({num_participantes}/{quiniela.numero_participantes})'}

        selecciones = list(Seleccion.objects.order_by('id'))
        num_selecciones_por_participante = len(selecciones) // num_participantes

        bombos = [
            selecciones[i * num_participantes:(i + 1) * num_participantes]
            for i in range(num_selecciones_por_participante)
        ]

        resultados = []
        for u in usuarios:
            participante, _ = Participante.objects.get_or_create(
                quiniela=quiniela, nombre=u['nombre'],
                defaults={'identificador': u.get('identificador', '')}
            )
            participante.identificador = u.get('identificador', '')
            participante.save()
            resultados.append(participante)

        for bombo in bombos:
            random.shuffle(bombo)
            for i, participante in enumerate(resultados):
                participante.selecciones.add(bombo[i])

        quiniela.sorteada = True
        quiniela.save()

        return {'resultados': [
            {
                'participante_id': p.id,
                'participante': p.nombre,
                'selecciones': [
                    {'id': s.id, 'nombre': s.nombre, 'codigo': s.codigo}
                    for s in p.selecciones.all()
                ],
            }
            for p in resultados
        ]}

    async def draw_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'draw_started',
            'resultados': event['resultados'],
        }))
