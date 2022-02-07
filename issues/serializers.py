from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from issues.models import Issue, Message


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class MessageSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Message
        fields = ("id", 'text', 'created_at', 'user', 'issue')


class CreateMessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = ('text',)


class CreateIssueSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ('topic', 'text')


class IssueSerializer(ModelSerializer):
    user = UserSerializer()
    messages = MessageSerializer(many=True)

    class Meta:
        model = Issue
        fields = ('id', 'topic', 'text', 'state', 'user', 'messages')
