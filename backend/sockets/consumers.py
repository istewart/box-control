from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync


class SocketConsumer(WebsocketConsumer):
    def connect(self):
        self.name = 'browser'
        print('connected!!')
        self.accept()
        self.send(text_data=json.dumps({'hi':'hey'}))

        #jo
        async_to_sync(self.channel_layer.group_add)(
            self.name,
            self.channel_name
        )

    def disconnect(self, close_code):
        print('disconnected :(')
        async_to_sync(self.channel_layer.group_discard)(
            self.name,
            self.channel_name
        )


    def updateData(self, data):
        #called when BoxConsumers get new data
        event = {}
        event['data'] = data['data']
        event['type'] = 'updateData'

        self.send(text_data=json.dumps(event))


    def receive(self, text_data):
        event = json.loads(text_data)

        event_type = event['type']
        data = event['data']
        print('received this session from form')
        print(data)

        if event_type == 'startSession':
            # TODO: actually write event handlers
            # TODO: create a new db entry for a session start
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
        print(f'Received a connection for {self.box_name}')

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

    def receive(self, text_data):
        #print(f'received socket response {text_data}')
        event = json.loads(text_data)

        event_type = event['type']
        data = event['data']

        if event_type == 'updateData' or event_type == 'dataStream':
            #TODO: first add info to db
            print('I have received data updates')
            async_to_sync(self.channel_layer.group_send)(
                'browser',
                {
                    'type': 'updateData',
                    'data': data
                }
            )
        else:
            print('some other event gotten')
            print(text_data)

    def startSession(self, data):
        self.send(text_data=json.dumps(data))
