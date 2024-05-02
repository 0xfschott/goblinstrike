import asyncio
from aiohttp import web
from .models import HttpListener
import multiprocessing

class HttpListenerManager:
    listeners = {}
    listeners_procs = {}

    @classmethod
    def initialize_listeners(cls):
        http_listeners = HttpListener.objects.all()
        for listener in http_listeners:
            cls.start_listener(listener)

    @classmethod
    def start_listener(cls, listener):
        if listener.id not in cls.listeners:
            http_listener = HttpListener.objects.get(id=listener.id)
            http_listener_instance = cls.create_listener_instance(http_listener)
            cls.listeners[listener.id] = http_listener_instance
            proc = multiprocessing.Process(target=http_listener_instance.start, args=())
            proc.start()
            cls.listeners_procs[listener.id] = proc
            
    @classmethod 
    def stop_listener(cls, listener):
        cls.listeners_procs[listener.id].terminate()

    @classmethod
    def check_state(cls, listener):
        if listener.id not in cls.listeners:
            http_listener = HttpListener.objects.get(id=listener.id)
            http_listener_instance = cls.create_listener_instance(http_listener)
            return http_listener_instance.check_state()

    @classmethod
    def create_listener_instance(cls, http_listener):
        return HttpListenerHandler(http_listener.name, http_listener.port)

class HttpListenerHandler:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.runner = self.init_server()
        self.listener = None
        self.stop_signal = True
        self.loop = None

    def init_server(self):
        async def handle_implant(request):
            return web.Response(text='Hello, world')

        app = web.Application()
        app.add_routes([web.get('/', handle_implant)])
        return web.AppRunner(app)

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.runner.setup())
        self.listener = web.TCPSite(self.runner, '0.0.0.0', self.port)
        self.loop.run_until_complete(self.listener.start())
        self.loop.run_forever()
        self.loop.close()

    def check_state(self):
        if self.listener and self.listener._server is not None and self.listener._server.sockets:
            return True
        return False
        
                       