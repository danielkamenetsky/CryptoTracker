from django.db import models
from django.contrib.auth.models import User
import uuid
from confluent_kafka import Producer
# This imports the post_save and post_delete signals from django.db.models.signals which
# are used to trigger actions when a model instance is saved or deleted.
from django.db.models.signals import post_save, post_delete
# This imports the receiver decorator, a decorator 
# is a function that modifies the behavior of another function.
from django.dispatch import receiver
from .services import send_transaction_event
from django.conf import settings # Import settings

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)
    ticker = models.CharField(max_length=50)
    exchange = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=5)
    price = models.DecimalField(max_digits=10, decimal_places=5)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.ticker} - {self.transaction_id}"

# Initialize producer using settings
producer_config = {'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS}
try:
    producer = Producer(producer_config)
except Exception as e:
    print(f"Failed to initialize Kafka Producer in models.py: {e}")
    producer = None # Set producer to None if initialization fails

# This function sends a message from the Transaction model
# to the Kafka topic 'transaction_events'
@receiver(post_save, sender=Transaction)
def handle_transaction_save(sender, instance, created, **kwargs):
    action = 'created' if created else 'updated'
    send_transaction_event(action, instance)

@receiver(post_delete, sender=Transaction)
def handle_transaction_delete(sender, instance, **kwargs):
    send_transaction_event('deleted', instance)
