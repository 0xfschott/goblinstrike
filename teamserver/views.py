from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from teamserver.serializers import HttpListenerCreateSerializer, HttpListenerControlSerializer
# views.py
from django.http import JsonResponse
from django.views.generic import View
from .models import HttpListener
from .listeners import HttpListenerManager
import asyncio
from drf_yasg import openapi
from .utils import is_port_available
from asgiref.sync import sync_to_async
import threading

class ListenerCreateView(APIView):
    @swagger_auto_schema(
        request_body=HttpListenerCreateSerializer,
        responses={200: HttpListenerCreateSerializer()},
        operation_description="Add a new HTTP listener"
    )
    def post(self, request):
        serializer = HttpListenerCreateSerializer(data=request.data)
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
        return JsonResponse({'message': f'Listener {listener.id} on port {port} started successfully.'})

@swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="listener_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID of the HTTP listener to delete",
                required=True,
            ),
        ],
        responses={
            200: "HTTP listener deleted successfully",
            404: "Listener not found",},
        operation_description="Delete a HTTP listener"
    )
class ListenerDeleteView(APIView):
    def delete(self, request, listener_id):
        try:
            listener = HttpListener.objects.get(id=listener_id)
            HttpListenerManager.stop_listener(listener)
            listener.delete()
        except HttpListener.DoesNotExist:
            return JsonResponse({'error': 'Listener not found'}, status=404)

        return JsonResponse({'message': 'Listener deleted successfully'})

class HttpListenerView(APIView):
    @swagger_auto_schema(
        request_body=HttpListenerCreateSerializer,
        responses={200: HttpListenerCreateSerializer()},
        operation_description="Add a new HTTP listener"
    )
    def post(self, request):
        serializer = HttpListenerCreateSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            port = serializer.validated_data.get('port')
            
            listener = HttpListener(name, port)
            t = threading.Thread(target=listener.start)
            t.start()
            return Response({"message": f"Listener {name} started on port {port}."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    