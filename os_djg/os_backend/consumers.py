import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ProcessManagerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.send(text_data=json.dumps({"message": "connected"}))
        print(self.channel_layer)
        # 加入组
        await self.channel_layer.group_add(
            'system_timer_group',
            self.channel_name
        )

    async def disconnect(self, close_code):
        # 离开组
        await self.channel_layer.group_discard(
            'system_timer_group',
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def send_timer_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
