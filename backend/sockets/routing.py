from django.urls import path

from . import consumers

websocket_urlpatterns = [
	path('sockets/box/<str:box_name>/', consumers.BoxConsumer),
    path('sockets/socket.io/', consumers.SocketConsumer),
]
