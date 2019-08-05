from channels.routing import route
from experiments.consumers import websocket_consumer

channel_routing = [
    route("websocket.receive", websocket_consumer),
]