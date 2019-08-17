from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync


class SocketConsumer(WebsocketConsumer):
    def connect(self):
        print('connected!!')
        self.accept()

        self.send(text_data='hi')

    def disconnect(self, close_code):
        print('disconnected :(')
        pass

    def receive(self, text_data):
	    # TODO
        event = json.loads(text_data)

        event_type = event['type']
        data = event['data']
        print(data)

        if event_type == 'startSession':
            # TODO: actually write event handlers
            #this_boxes_socket = sockets[this_box_number]
            async_to_sync(self.channel_layer.group_send)(
                data['boxNumber'],
                {
                    'type': 'startSession',
                    'data': data
                }
            )
            
        

        self.send(text_data=json.dumps(event))




class BoxConsumer(WebsocketConsumer):
    def connect(self):
        self.box_name = self.scope['url_route']['kwargs']['box_name']

        async_to_sync(self.channel_layer.group_add)(
            self.box_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.box_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)