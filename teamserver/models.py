# models.py
import random
from django.db import models
import asyncio
from aiohttp import web
from django.utils import timezone

class Listener(models.Model):
    name = models.CharField(max_length=100)

class HttpListener(Listener):
    port = models.IntegerField()

class GoblinMetadata(models.Model):
    goblin_id = models.IntegerField()
    hostname = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    os_version = models.CharField(max_length=100)
    architecture = models.CharField(max_length=100)
    process = models.CharField(max_length=100)
    process_id = models.CharField(max_length=100)
    integrity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

class GoblinTask(models.Model):
    command = models.CharField(max_length=50)
    arguments = models.TextField(null=True, blank=True)
    is_pending = models.BooleanField(default=True)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return f"{'Pending' if self.is_pending else 'Completed'}"

class GoblinTaskResult(models.Model):
    task = models.OneToOneField(GoblinTask, on_delete=models.CASCADE, related_name='task', null=True, blank=True)
    result = models.TextField(null=True, blank=True)

class Goblin(models.Model):
    name = models.TextField()
    last_seen = models.DateTimeField(null=True,)
    tasks = models.ManyToManyField(GoblinTask, blank=True, related_name='assigned_goblins')
    metadata = models.OneToOneField(GoblinMetadata, on_delete=models.CASCADE, related_name='goblin', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If the goblin is newly registered
        if not self.name:
            self.name = random.choice([
                "Grizlik", "Snikkle", "Gromp", "Fizzletoe", "Noggin",
                "Sprocket", "Zizzix", "Wizzlecrank", "Gobblin", "Snaggletooth",
                "Blister", "Wart", "Snicklesnack", "Squib", "Toadwart",
                "Razzle", "Glimmer", "Splinter", "Snickerdoodle", "Squizzlefang"
            ])
        super(Goblin, self).save(*args, **kwargs)

    def check_in(self):
        print(f"Checking in Goblin: {self.id}")
        self.last_seen = timezone.now()
        self.save()

    def get_pending_tasks(self):
        print("Get pending tasks")
        try:
            tasks = self.tasks.filter(is_pending=True).order_by('id')
            print(list(tasks))
        except Exception as e:
            print(e)
            print("No tasks found")
            return []
        return tasks