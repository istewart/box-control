from psychopy import visual,clock, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
#import nidaqmx as ni
import websockets
import asyncio
import json
import time

my_url = "ws://0.0.0.0:8000/sockets/box/TODO/"


class Box:
    def __init__(self):
        self.session = None
        asyncio.get_event_loop().run_until_complete(self.run_ws())

    async def run_ws(self):
        #create the websocket connection
        while True:
            async with websockets.connect(my_url) as websocket:
                print('new websocket connection!')
                self.websocket = websocket

                while True:
                    await self.handle_isi()

                    if self.session and not self.session.is_ended:
                        await self.session.run_trial()
            


    async def handle_isi(self):
        if self.session and not self.session.is_ended:
            #TODO: this isn't quitting as it should
            consumer_task = asyncio.ensure_future(
                self.handle_incoming()
            )
            producer_task = asyncio.ensure_future(
                self.session.run_isi()
            )

            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            print('done: ' + str(done))
            print('pending: ' + str(pending))

            for task in pending:
                task.cancel()
        else:
            await self.handle_incoming()

    async def handle_incoming(self):
        #just await getting message and then event handle
        print('waiting for event')
        event = await self.websocket.recv() 
        print('event gotten')
        self.handle_event(event)               

    def handle_event(self, event):
        response_event = json.loads(event)

        response_type = response_event['type']
        response_data = response_event['data']

        if response_type == 'startSession':
            print('creating a session')
            self.session = ContrastDetectionTask(
                self.websocket,
                response_data,
            )
        elif response_type == 'stopSession':
            self.session.stop()
        elif response_type == 'pauseSession':
            print('pausing')
            self.session.toggle_pause()
        else:
            print(f'Unknown response_type: {response_type}')


class ContrastDetectionTask:
    def __init__(self, websocket, sessionData):
        self.websocket = websocket
        self.is_ended = False
        self.is_paused = False
        self.session_id = sessionData['session_id']
        self.session_data = sessionData

        self.setup_exp()
        
        self.setup_monitor()
        self.gen_conds()
        self.init_stim()
        self.setup_daq()

        self.session_timer = clock.MonotonicClock()
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        
        #create a trial handler
        self.trials = data.TrialHandler(
            self.conds, 1, method='sequential',
            extraInfo = self.session_data)
        self.trials.data.addDataType('Response')
        self.exp.addLoop(self.trials)




    def setup_exp(self):
        #basic set up for file saving, may be eliminated in the future
        base_dir = 'C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/'

        #self.filename = (base_dir + 
        #    self.session_data['date']+ '_' + self.session_data['animal'])
        self.filename = 'temp'

        self.exp = data.ExperimentHandler('ContrastDetectionTask','v1',
            dataFileName = self.filename,
            extraInfo = self.session_data)


    def setup_daq(self):
        #TODO
        pass
    


    def setup_monitor(self):
        self.session_data['monitor_height'] = 13 #in cm
        self.session_data['monitor_width'] = 22.5 #cm
        self.session_data['monitor_dist'] = 10 #in cm
        
        #initialize
        #TODO: fix this all up
        self.monitor = monitors.Monitor(
            'Default',
            width=self.session_data['monitor_width'],
            distance=self.session_data['monitor_dist']
            )
        self.win = visual.Window(
            fullscr=False,
            monitor=self.monitor,
            units="pix",
            size=[1280, 720],
            color=[self.session_data['background_lum'],
                   self.session_data['background_lum'],
                    self.session_data['background_lum']]
            )
        
        self.session_data['FR'] = self.win.getActualFrameRate()
        hod = self.session_data['monitor_height']/self.session_data['monitor_dist']
        vis_deg = np.degrees(np.arctan(hod))
        self.pix_per_deg = self.win.size[1]/vis_deg



    def init_stim(self):
        self.stim_on_frames = int(
            self.session_data['stim_time']/1000*self.session_data['FR'])
        
        self.grating = visual.GratingStim(
            win=self.win,
            mask='circle'
        )     


    def gen_conds(self):
        self.conds = []
        #TODO: this structure means that if you have two conditions
        #with weight 1, they will just alternate. So you should fix that?
        tier = self.session_data['tier']
        for temp in range(25):
            mini_conds = []
            for stim_set in self.session_data['stim_sets']:
                print(stim_set)
                this_stim = stim_set.copy()
                overall_weight = this_stim.pop('overall_weight')
                #delete random fields
                this_stim.pop('id')
                this_stim.pop('session')
                #TODO, make it work
                #remove the contrast and weight fields
                for _ in range(overall_weight):
                    print(overall_weight)
                    if tier==1:
                        if this_stim['stim_size']>0:
                            contrasts = [100]
                        else:
                            contrasts = [0]

                        weights = [1]
                    elif tier==2:
                        if this_stim['stim_size']>0:
                            contrasts = [100]
                        else:
                            contrasts = [0]

                        weights = [1]
                    elif tier==3:
                        contrasts = [4, 8, 16, 64, 90]
                        weights = [1, 1, 1, 1, 1]
                    for contrast, weight in zip(contrasts, weights):
                        this_stim['contrast'] = contrast
                        [mini_conds.append(this_stim) for _ in range(weight)]
                    random.shuffle(mini_conds)
            self.conds += mini_conds


    def teardown_daq(self):
        pass


    def stop(self):
        self.is_ended = True
        self.exp.saveAsWideText(self.filename)
        self.trials.saveAsWideText(self.filename + '_trials')
        self.teardown_daq()



    async def present_grating(self, phase_increment):
        phase = 0

        s = time.time()
        for frame in range(self.stim_on_frames):                   
            phase += phase_increment
            self.grating.setPhase(phase)
            self.grating.draw()
            self.win.flip()

            await self.websocket.send(json.dumps({'type': 'updateData',
                'data': {
                    'session_id': self.session_id,
                    'trial_number': self.trials.thisN,
                    'timestamp': self.session_timer.getTime(),
                    'is_stim':1,
                    'is_licking':np.random.randint(2),
                    'is_false_alarm': 0,
                    'is_port_open':np.random.randint(2),
                    'is_led_on': 0,
                    'is_tone': 0,
                    }}))
        print(time.time()-s)



    def toggle_pause(self):
        self.is_paused = not self.is_paused


    async def run_trial(self):

        if self.is_paused:
            return

        #TODO: figure out what's up with which next to call and where data is
        #self.exp.nextEntry()
        trial = self.trials.next()
        self.setup_grating(trial)
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = None
        last_send = time.time()
        grating_presented = False

        #send init trial info 
        await self.websocket.send(json.dumps({
            'type': 'initTrial',
            'data': {
                'session_id': self.session_id,
                'trial_number': self.trials.thisN,
                'contrast': trial['contrast'],
                'stim_size': trial['stim_size'],
                'is_optogenetics': False,
            }}))
        
        while trial_still_running:
            last_send = await self.send_socket(last_send)

            current_time = self.trial_timer.getTime()
             
            if current_time <= self.session_data['stim_delay']/1000:
                continue

            #sometimes the presentation time is slightly below stim time
            #but still only present the stim once
            elif not grating_presented:
                print('this trial info: ', trial['contrast'], trial['stim_size'])
                phase_increment = trial['temporal_freq']/self.session_data['FR']

                await self.present_grating(phase_increment)
                grating_presented = True

                if self.session_data['tier']==1:
                    self.deliver_reward
                   
            else:
                self.grating.setContrast(0)
                self.grating.setSize(0)
                self.grating.draw()

                responded = self.check_lick()
            if responded:
                responded = True

                if trial['should_lick'] and self.session_data['tier']!=1:
                    self.deliver_reward()
                
                response_time = current_time
                print('time to respond was ', response_time)
                trial_still_running = False
                self.trials.data.add('Response', 1)
                self.trials.data.add('RespTime', response_time)

            elif (current_time >=
                    self.session_data['stim_time']/1000 +
                    self.session_data['stim_delay']/1000 +
                    self.session_data['response_window']/1000):

                trial_still_running = False
                responded = False
                self.trials.data.add('Response', 0)

            self.win.flip()

        await self.websocket.send(json.dumps({
            'type': 'endTrial',
            'data': {
                'session_id': self.session_id,
                'trial_number': self.trials.thisN,
                'is_licked': responded,
                'response_time': response_time
            }}))

    def setup_grating(self, trial):
        #convert location to pixels
        pos = np.array([trial['position_x'],trial['position_y']])
        self.grating.pos = pos * self.pix_per_deg
        self.grating.sf = trial['spatial_freq']/self.pix_per_deg
        self.grating.ori = trial['orientation']
        self.grating.size = trial['stim_size']*self.pix_per_deg
        self.grating.contrast = trial['contrast']/100

    def deliver_reward(self):
        #TODO
        pass


    def check_lick(self):
        #TODO
        return False


    async def send_socket(self, last_send):
        if time.time()-last_send > .01:
                await self.websocket.send(json.dumps({'type': 'updateData',
                    'data': {
                        'trial_number': self.trials.thisN,
                        'session_id': self.session_id,
                        'timestamp': self.session_timer.getTime(),
                        'is_stim':0,
                        'is_licking':np.random.randint(2),
                        'is_false_alarm': 0,
                        'is_port_open':np.random.randint(2),
                        'is_led_on': 0,
                        'is_tone': 0,
                        }}))
                last_send = time.time()
        return last_send


    async def run_isi(self):
        if self.is_paused:
            await asyncio.sleep(1)
            return

        print('isi is happening')

        isi = np.random.randint(self.session_data['isi_min']/1000, self.session_data['isi_max']/1000)
        self.isi_timer.reset()
        false_alarm_times = []

        last_send = time.time()
        
        while self.isi_timer.getTime() < isi:
            last_send = await self.send_socket(last_send)
            await asyncio.sleep(.005)

            #handle actual isi
            if self.isi_timer.getTime() > self.session_data['grace_time']/1000: #if we're out of grace period
                #check for a false alarm
                responded = self.check_lick()
                if responded:
                    print('false alarm!')
                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.session_data['isi_min']/1000,self.session_data['isi_max']/1000)
                    self.isi_timer.reset()

        #TODO: is this right place to save data
        self.trials.addData('fa_times', false_alarm_times)
        print('isi is ending')





if __name__ == '__main__':
    Box()
    #ContrastDetectionTask()