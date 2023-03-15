from rest_framework import serializers
from applications.message.models import Chat, ChatMessage, PrivateMessage
from applications.user.serializers import UserCreateWithEmailSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user = UserCreateWithEmailSerializer()
        
    class Meta:
        model = ChatMessage
        fields = '__all__'
        
    def get_created_at_formatted(self, obj: ChatMessage) -> obj:
        return obj.created_at.strftime('%H:%M')


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = '__all__'
        read_only_fields = ['last_message', 'messages']

    def get_last_message(self, obj: Chat) -> ChatMessageSerializer:
        return ChatMessageSerializer(obj.message.order_by('created_at').last()).data