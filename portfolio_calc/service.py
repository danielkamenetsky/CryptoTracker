import os
import sys
import django
import redis


# Add the project root directory to the Python path
# This is crucial for finding the transaction_tracker module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Now set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transaction_tracker.settings")
django.setup()

# Now imports will work
from confluent_kafka import Consumer
from transactions.models import Transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class PortfolioTracker:
    def __init__(self):
        self.transactions = {}  # Format: {tx_id: {'amount': 0.5, 'price': 30000}}
        self.prices = {'bitcoin': 0.0, 'ethereum': 0.0}
        self.total_invested = 0.0
        self.current_value = 0.0
        self.total_profit = 0.0
        
        # Initialize Redis connection
        try:
            self.redis = redis.Redis(host='localhost', port=6379, db=0)
            print("Redis connection initialized")
        except Exception as e:
            print(f"Redis connection error: {e}")
            self.redis = None

    # Checks if the transaction is created or deleted and updates the transactions dictionary
    def update_transaction(self, tx_id, action, amount=None, price=None):
        if action == 'created':
            self.transactions[tx_id] = {
                'amount': float(amount),  # Convert to float when storing
                'price': float(price)     # Convert to float when storing
            }
        elif action == 'deleted':
            self.transactions.pop(tx_id, None)
        
        self._calculate_totals()

    # Sets the price of the coin and recalculates the totals
    def update_price(self, coin, price):
        self.prices[coin] = float(price)  # Convert to float when storing
        self._calculate_totals()

    # Calculates the total invested, current value, and profit
    def _calculate_totals(self):
        self.total_invested = sum(
            float(tx['amount']) * float(tx['price'])
            for tx in self.transactions.values()
        )
        
        self.current_value = sum(
            float(tx['amount']) * float(self.prices['bitcoin'])
            for tx in self.transactions.values()
        )
        
        self.total_profit = self.current_value - self.total_invested
        
        self._print_status()

    # Prints the status of the portfolio
    def _print_status(self):
        # Only print if there are transactions or this is forced
        if len(self.transactions) > 0:
            print(f"\nPortfolio Status:")
            print(f"Transactions: {len(self.transactions)}")
            print(f"BTC Price: ${self.prices['bitcoin']:,.2f}")
            print(f"Invested: ${self.total_invested:,.2f}")
            print(f"Current Value: ${self.current_value:,.2f}")
            print(f"Profit: ${self.total_profit:,.2f}\n")
            
            # Update Redis with the latest values
            try:
                if self.redis:
                    self.redis.set('portfolio:current_value', str(self.current_value))
                    self.redis.set('portfolio:total_invested', str(self.total_invested))
                    self.redis.set('portfolio:total_profit', str(self.total_profit))
                    self.redis.set('portfolio:btc_price', str(self.prices['bitcoin']))
                    print("Updated Redis with latest portfolio values")
            except Exception as e:
                print(f"Redis update error: {e}")
            
            # Send to WebSocket if Django is set up
            try:
                channel_layer = get_channel_layer()
                print("Sending update to WebSocket channel")
                async_to_sync(channel_layer.group_send)(
                    "portfolio_updates",
                    {
                        "type": "portfolio_update",
                        "total_invested": float(self.total_invested),
                        "current_value": float(self.current_value),
                        "total_profit": float(self.total_profit),
                        "btc_price": float(self.prices['bitcoin'])
                    }
                )
                print("Update sent successfully")
            except Exception as e:
                print(f"WebSocket error: {e}")

# KafkaPortfolioTracker inherits from PortfolioTracker and
# listens to the transaction_events and crypto_prices topics
class KafkaPortfolioTracker(PortfolioTracker):
    def run(self):
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'portfolio-tracker',
            'auto.offset.reset': 'earliest'
        })
        
        consumer.subscribe(['transaction_events', 'crypto_prices'])
        
        try:
            while True:
                msg = consumer.poll(1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    continue
                
                if msg.topic() == 'transaction_events':
                    self._handle_transaction_message(msg)
                elif msg.topic() == 'crypto_prices':
                    self._handle_price_message(msg)
                    
        except KeyboardInterrupt:
            print("Stopping tracker...")
        finally:
            consumer.close()

    # Handles the transaction message
    def _handle_transaction_message(self, msg):
        try:
            action, tx_id = msg.value().decode().split(':')
            
            if action == 'created':
                # Get transaction from database
                tx = Transaction.objects.get(id=tx_id)
                
                # Convert Decimal to float for calculations
                self.update_transaction(
                    tx_id=tx_id,
                    action=action,
                    amount=float(tx.amount),  # Convert Decimal to float
                    price=float(tx.price)     # Convert Decimal to float
                )
            else:  # deleted
                self.update_transaction(tx_id=tx_id, action=action)
        except Exception as e:
            print(f"Transaction error: {e}")

    # Handles the price message
    def _handle_price_message(self, msg):
        try:
            coin = msg.key().decode()
            price = float(msg.value().decode())
            self.update_price(coin, price)
        except Exception as e:
            print(f"Price error: {e}")

if __name__ == '__main__':
    tracker = KafkaPortfolioTracker()
    tracker.run()