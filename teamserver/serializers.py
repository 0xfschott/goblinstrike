from rest_framework import serializers

class HttpListenerCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    port = serializers.IntegerField()

class HttpListenerControlSerializer(serializers.Serializer):
    listener_id = serializers.IntegerField()
    action = serializers.CharField(max_length=10)