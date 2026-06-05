import json
from channels.generic.websocket import AsyncWebsocketConsumer


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
            QuinielaConsumer.salas[self.slug][self.channel_name] = data.get('nombre', 'Anónimo')
            await self._broadcast_users()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        QuinielaConsumer.salas.get(self.slug, {}).pop(self.channel_name, None)
        if not QuinielaConsumer.salas.get(self.slug):
            QuinielaConsumer.salas.pop(self.slug, None)
        else:
            await self._broadcast_users()

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
