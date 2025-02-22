from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def send_transaction_event(action, transaction):
    message = f"{action}:{transaction.id}"
    producer.produce(
        topic='transaction_events',
        key=str(transaction.id),
        value=message
    )
    producer.flush()
