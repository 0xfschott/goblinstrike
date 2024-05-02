from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HttpListener

@receiver(post_save, sender=HttpListener)
def start_http_listener(sender, instance, **kwargs):
    print("Signal received")
    HttpListenerManager.start_listener(instance)
    t = threading.Thread(target=HttpListenerManager.start_listener, args=(instance,))
    t.start()