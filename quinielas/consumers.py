import json
from channels.generic.websocket import AsyncWebsocketConsumer


class QuinielaConsumer(AsyncWebsocketConsumer):
    salas = {}

    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'quiniela_{self.slug}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        QuinielaConsumer.salas.setdefault(self.slug, set()).add(self.channel_name)
        await self.accept()
        await self._broadcast_count()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        QuinielaConsumer.salas.get(self.slug, set()).discard(self.channel_name)
        if not QuinielaConsumer.salas.get(self.slug):
            QuinielaConsumer.salas.pop(self.slug, None)
        else:
            await self._broadcast_count()

    async def _broadcast_count(self):
        count = len(QuinielaConsumer.salas.get(self.slug, set()))
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'quiniela.count', 'count': count}
        )

    async def quiniela_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_count',
            'count': event['count'],
        }))
