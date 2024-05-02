# models.py
import random
from django.db import models
import asyncio
from aiohttp import web

class Listener(models.Model):
    name = models.CharField(max_length=100)

class HttpListener(Listener):
    port = models.IntegerField()

class Goblin(models.Model):
    name = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100)
    ip = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    os_version = models.CharField(max_length=100)

    @classmethod
    def create(cls, hostname, ip, os, os_version):
        goblin = cls(hostname=hostname, ip=ip, os=os, os_version=os_version)
        goblin.name = random.choice([
            "Grizlik", "Snikkle", "Gromp", "Fizzletoe", "Noggin",
            "Sprocket", "Zizzix", "Wizzlecrank", "Gobblin", "Snaggletooth",
            "Blister", "Wart", "Snicklesnack", "Squib", "Toadwart",
            "Razzle", "Glimmer", "Splinter", "Snickerdoodle", "Squizzlefang"
        ])
        return goblin
