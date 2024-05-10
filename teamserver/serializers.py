from rest_framework import serializers
from .models import Goblin, HttpListener, GoblinMetadata, GoblinTask, GoblinTaskResult

class HttpListenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HttpListener
        fields = '__all__'

class GoblinMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoblinMetadata
        fields = '__all__'

class GoblinTaskSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    arguments = serializers.CharField()
    class Meta:
        model = GoblinTask
        fields = ['id', 'command', 'arguments', 'file']

class GoblinTaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoblinTaskResult
        fields = '__all__'

class GoblinRawTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoblinTask
        fields = ['command']

class GoblinSerializer(serializers.ModelSerializer):
    metadata = GoblinMetadataSerializer()
    tasks = GoblinTaskSerializer(many=True, read_only=True)
    last_seen = serializers.DateTimeField(format=None, allow_null=True)

    class Meta:
        model = Goblin
        fields = ['id', 'name', 'last_seen', 'metadata', 'tasks']