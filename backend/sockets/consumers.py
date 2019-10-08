from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from experiments.analytics import get_overall_session_performance
from experiments.models import Animal, Session, Trial, DataPoint, StimSet
from django.forms.models import model_to_dict
import datetime

class SocketConsumer(WebsocketConsumer):
    def connect(self):
        self.name = 'browser'
        print('connected!!')
        self.accept()
        self.send(text_data=json.dumps({'hi':'hey'}))

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
        self.send(text_data=json.dumps(data))

    def initTrial(self, data):
        #called when BoxConsumers start a new trial
        self.send(text_data = json.dumps(data))

    def performanceUpdate(self, data):
        self.send(text_data=json.dumps(data))

    def initiate_session(self, data):
        this_animal = self.handle_get_animal(data['animalId'])      
        print('starting a session')
        # create the session object
        session = Session.objects.create(
            animal = this_animal,
            box_number = data['boxNumber'],
            tier = data['tier'],
            optogenetics = data['optogenetics'],
            background_lum = data['backgroundLuminensce'],
            )

        #create the stim sets
        #TODO: this is nonsense
        tier = data['tier']
        if tier==1:
            stim_sets = [
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeOne']),
                        should_lick=True,
                        overall_weight=3,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeTwo']),
                        should_lick=True,
                        overall_weight=3,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=0,
                        should_lick=False,
                    ),
                ]
        elif tier==2:
            stim_sets = [
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeOne']),
                        should_lick=True,
                        overall_weight=3,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeTwo']),
                        should_lick=True,
                        overall_weight=3,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=0,
                        should_lick=False,
                        overall_weight=2,
                    ),
                ]
        elif tier==3:
            stim_sets = [
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeOne']),
                        should_lick=True,
                        overall_weight=1,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=int(data['sizeTwo']),
                        should_lick=True,
                        overall_weight=1,
                    ),
                    StimSet.objects.create(
                        session=session,
                        stim_size=0,
                        should_lick=False,
                        overall_weight=1,
                    ),
                ]
        else:
            print('INVALID TIER')
            stim_sets = [
                    StimSet.objects.create(
                        session=session,
                        stim_size=0,
                        should_lick=2,
                    ),
                ]

        data = model_to_dict(session)
        print('dictified session', data)
        data['session_id'] = session.id
        data['stim_sets'] = [model_to_dict(stim_set) for stim_set in stim_sets]

        # TODO: check if anyone is in this channel group, send error
        async_to_sync(self.channel_layer.group_send)(
            data['box_number'],
            {
                'type': 'startSession',
                'data': data
            }
        )

    def handle_get_animal(self, animal_id):
        if len(Animal.objects.filter(id__iexact=animal_id))==0:
            # TODO: make mouse id check return an error, not just create
            # TEMP: just create one
            Animal.objects.create(id = animal_id,
                genotype='aa',
                date_of_birth=datetime.date.today(),
                sex='n',)

        return Animal.objects.filter(id__iexact=animal_id)[0]

    def pause_session(self, data):
        async_to_sync(self.channel_layer.group_send)(
            data['boxNumber'],
            {
                'type': 'pauseSession',
                'data': data
            }
        )

    def receive(self, text_data):
        event = json.loads(text_data)

        event_type = event['type']
        data = event['data']
        print('received this info from form')
        print(data)

        if event_type == 'startSession':
            self.initiate_session(data)
        if event_type == 'pauseSession':
            self.pause_session(data)

        #self.send(text_data=json.dumps(event))






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
            self.handle_update_data(data)

        elif event_type == 'initTrial':
            Trial.objects.create(**data)

            print('I am beginning a new trial')

            async_to_sync(self.channel_layer.group_send)(
                'browser',
                {
                    'type': 'initTrial',
                    'data': data,
                }
            )

        elif event_type == 'endTrial':
            trial = Trial.objects.get(
                session_id=data['session_id'],
                trial_number=data['trial_number'],
            )

            trial.is_licked = data['is_licked']
            trial.response_time = data['response_time']

            trial.save()

            session_performance = get_overall_session_performance(trial.session_id)

            async_to_sync(self.channel_layer.group_send)(
                'browser',
                {
                    'type': 'performanceUpdate',
                    'data': session_performance,
                }
            )

        else:
            print('some other event gotten')
            print(text_data)

    def handle_update_data(self,data):
        trial_number = data['trial_number']
        session_id = data.pop('session_id')
        this_trial = Trial.objects.filter(session_id = session_id, trial_number = trial_number)[0]

        DataPoint.objects.create(
            trial= this_trial,
            timestamp= data['timestamp'],
            is_stim= data['is_stim'],
            is_port_open= data['is_port_open'],
            is_tone= data['is_tone'],
            is_led_on= data['is_led_on'],
            is_licking= data['is_licking'],
            is_false_alarm= data['is_false_alarm'])

        async_to_sync(self.channel_layer.group_send)(
            'browser',
            {
                'type': 'updateData',
                'data': data
            }
        )

    def startSession(self, data):
        self.send(text_data=json.dumps(data))

    def pauseSession(self, data):
        self.send(text_data=json.dumps(data))
