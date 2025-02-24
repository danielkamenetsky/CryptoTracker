# Import necessary tools
import time  # For waiting between requests
import requests  # To fetch data from CoinGecko
from confluent_kafka import Producer  # To send messages to Kafka

# Configuration - Easy to change later
COIN_IDS = ['bitcoin', 'ethereum']  # Coins to track
INTERVAL = 60  # Check every 60 seconds

# Connect to Kafka
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def fetch_prices():
    try:
        # Build the API URL
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COIN_IDS)}&vs_currencies=usd"
        
        # Get data from CoinGecko
        response = requests.get(url)
        
        # Return parsed JSON like {'bitcoin': {'usd': 50000}, ...}
        return response.json()
    except Exception as e:
        # Print error if API call fails
        print(f"Price fetch failed: {e}")
        return {}

def main():
    # Run forever
    while True:
        # Get latest prices
        prices = fetch_prices()
        
        # Send each price to Kafka
        for coin_id, data in prices.items():
            producer.produce(
                topic='crypto_prices',  # Kafka topic name
                key=coin_id,  # e.g., "bitcoin"
                value=str(data['usd'])  # e.g., "50000.0"
            )
        
        # Ensure messages are sent immediately
        producer.flush()
        
        # Wait before next update
        time.sleep(INTERVAL)

# Start the service when run directly
if __name__ == '__main__':
    main()
