from django.urls import path
from applications.message import consumers

websocket_urlpatterns = [
    # path('ws/', consumers.UserConsumer.as_asgi()),
    path('ws/', consumers.ChatConsumer.as_asgi()),
]