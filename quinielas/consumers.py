import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Quiniela, Seleccion, Participante


class QuinielaConsumer(AsyncWebsocketConsumer):
    # No usar memoria local para multi-instancia. Los datos se gestionan en Redis y DB.

    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'quiniela_{self.slug}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        # Obtener lista de usuarios desde la base de datos
        users = await self._get_users_in_room()
        await self.send(text_data=json.dumps({'type': 'user_list', 'users': users, 'count': len(users)}))

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'join':
            nombre = data.get('nombre', 'Anónimo')
            
            # Verificar si el nombre ya existe usando la base de datos
            if await self._nombre_exists_in_room(nombre):
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'El nombre ya está en uso. Elige otro.'}))
                return
            
            max_participantes = await self._get_max_participantes()
            usuarios_actuales = await self._get_users_in_room()
            
            if len(usuarios_actuales) >= max_participantes:
                await self.send(text_data=json.dumps({'type': 'error', 'message': f'La quiniela ya está llena ({len(usuarios_actuales)}/{max_participantes}).'}))
                return
            
            await self._save_participante(nombre)
            users = await self._get_users_in_room()
            await self.send(text_data=json.dumps({'type': 'user_list', 'users': users, 'count': len(users)}))
            await self._broadcast_users()

        elif data.get('type') == 'start_draw':
            await self._handle_start_draw()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self._broadcast_users()

    @database_sync_to_async
    def _get_max_participantes(self):
        return Quiniela.objects.get(slug=self.slug).numero_participantes

    @database_sync_to_async
    def _get_users_in_room(self):
        """Obtener lista de nombres de participantes desde la base de datos."""
        quiniela = Quiniela.objects.get(slug=self.slug)
        return list(quiniela.participantes.values_list('nombre', flat=True))

    @database_sync_to_async
    def _nombre_exists_in_room(self, nombre):
        """Verificar si un nombre ya existe en la quiniela."""
        quiniela = Quiniela.objects.get(slug=self.slug)
        return quiniela.participantes.filter(nombre=nombre).exists()

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
                    {'id': s.id, 'nombre': s.nombre, 'codigo': s.codigo}
                    for s in participante.selecciones.all()
                ],
            })

        return {'resultados': resultados}

    @database_sync_to_async
    def _broadcast_users(self):
        """Broadcast a todos los usuarios conectados actualmente."""
        users = []
        quiniela = Quiniela.objects.filter(slug=self.slug).first()
        if quiniela:
            users = list(quiniela.participantes.values_list('nombre', flat=True))
        
        # Enviar a todos los miembros del grupo (incluyendo el actual)
        self.channel_layer.group_send(
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
