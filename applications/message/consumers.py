import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)

from applications.message.models import ChatMessage, Chat
from applications.message.serializers import ChatMessageSerializer, ChatSerializer
from applications.user.serializers import UserCreateWithEmailSerializer
from applications.user.models import User


class ChatConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    lookup_field = 'pk'

    async def disconnect(self, code):
        if hasattr(self, 'chat_subscribe'):
            await self.remove_user_from_room(self.room_subscribe)
            await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_room(self, pk, **kwargs):
        self.chat_subscribe = pk
        await self.add_user_to_room(pk)
        await self.notify_users()

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)

    @action()
    async def create_message(self, message, **kwargs):
        chat: Chat = await self.get_chat(pk=self.chat_subscribe)
        await database_sync_to_async(ChatMessage.objects.create)(
            chat=chat,
            user=self.scope['user'],
            text=message
        )
    
    @action()
    async def subscribe_to_messages_in_chat(self, pk, **kwargs):
        await self.message_activity.subscribe(chat=pk)

    @model_observer(ChatMessage)
    async def message_activity(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: ChatMessage, **kwargs):
        yield f'chat__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, chat=None, **kwargs):
        if chat is not None:
            yield f'chat__{chat}'

    @message_activity.serializer
    def message_activity(self, instance: ChatMessage, action, **kwargs):
        return dict(data=ChatMessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_members(self):
        chat: Chat = await self.get_chat(self.chat_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type': 'update_members',
                    'usuarios': await self.current_members(chat)
                }
            )

    async def update_members(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def get_chat(self, pk: int) -> Chat:
        return Chat.objects.get(pk=pk)

    @database_sync_to_async
    def current_members(self, chat: Chat) -> list:
        return [UserSerializer(user).data for user in chat.current_members.all()]

    @database_sync_to_async
    def remove_member_from_room(self, chat):
        user: User = self.scope['user']
        user.current_chats.remove(chat)

    @database_sync_to_async
    def add_user_to_chat(self, pk):
        user: User = self.scope['user']
        if not user.current_chats.filter(pk=self.chat_subscribe).exists():
            user.current_chats.add(Chat.objects.get(pk=pk))


class UserConsumer(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PatchModelMixin,
        mixins.UpdateModelMixin,
        mixins.CreateModelMixin,
        mixins.DeleteModelMixin,
        GenericAsyncAPIConsumer):

    queryset = User.objects.all()
    serializer_class = UserCreateWithEmailSerializer