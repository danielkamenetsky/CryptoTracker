import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

# Set up logging
logger = logging.getLogger(__name__)

GROUP_NAME = 'portfolio_updates'

class PortfolioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connection attempt")
        print("WebSocket connection attempt")
        
        # Join the portfolio_updates group
        await self.channel_layer.group_add(
            GROUP_NAME,
            self.channel_name
        )
        await self.accept()
        
        logger.info("WebSocket connection accepted")
        print("WebSocket connection accepted")
        
        # Send a test message to verify client-side handling
        await self.send(text_data=json.dumps({
            'total_invested': 1000.0,
            'current_value': 1200.0,
            'total_profit': 200.0,
            'btc_price': 50000.0
        }))
        logger.info("Test message sent")
        print("Test message sent")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")
        print(f"WebSocket disconnected with code: {close_code}")
        
        # Leave the portfolio_updates group
        await self.channel_layer.group_discard(
            GROUP_NAME,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}, left group: {GROUP_NAME}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        logger.info(f"Received message from client: {text_data}")
        print(f"Received message from client: {text_data}")
        # Handle any messages from client if needed
        pass

    # Receive message from portfolio group
    async def portfolio_update(self, event):
        portfolio_data = event['data']
        logger.info(f"Received message in group {GROUP_NAME} for {self.channel_name}: {portfolio_data}")
        print(f"Received message in group {GROUP_NAME} for {self.channel_name}: {portfolio_data}")
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'portfolio_data': portfolio_data
        }))
        logger.info(f"Sent data to WebSocket client {self.channel_name}")
        print("Sent portfolio update to client")
