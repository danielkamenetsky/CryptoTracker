import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PortfolioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "portfolio_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "portfolio_updates",
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Handle any messages from client if needed
        pass

    # Receive message from portfolio group
    async def portfolio_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'portfolio_value': event['portfolio_value']
        }))
