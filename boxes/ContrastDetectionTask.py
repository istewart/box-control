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
        print('handling isi')
        if self.session and not self.session.is_ended:
            print('in a session so chilling')
            consumer_task = asyncio.ensure_future(
                self.handle_incoming())
            producer_task = asyncio.ensure_future(
                self.session.run_isi())
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        else:
            await self.handle_incoming()

    async def handle_incoming(self):
        #just await getting message and then event handle
        event = await self.websocket.recv() 
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
            self.session.toggle_pause()
        else:
            print(f'Unknown response_type: {response_type}')


class ContrastDetectionTask:
    def __init__(self, websocket, sessionData):
        self.websocket = websocket
        self.is_ended = False
        self.is_paused = False
        self.session_id = sessionData['session_id']

        self.setup_exp()

        self.define_task_vars()
        
        self.setup_monitor()
        self.gen_conds()
        self.setup_stim()
        self.setup_daq()

        self.session_timer = clock.MonotonicClock()
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        
        #create a trial handler
        self.trials = data.TrialHandler(
            self.size_int_response, 1, method='sequential')
        self.trials.data.addDataType('Response')
        self.exp.addLoop(self.trials)



    def setup_daq(self):
        #TODO
        pass


    def define_task_vars(self):
        #TODO: session all this
        self.stim_delay = .2 #in s
        self.stim_time = .6 #in s
        self.response_window = 1 # in s
        self.isimin = 3 # in s
        self.isimax = 8 #in s
        self.grace_time = 1 #in s
        self.water_time = 20 #in ms
    


    def setup_monitor(self):
        self.expInfo['monitor_height'] = 13 #in cm
        self.expInfo['monitor_width'] = 22.5 #cm
        self.expInfo['monitor_dist'] = 10 #in cm
        
        #initialize
        self.monitor = monitors.Monitor(
            'Default',
            width=self.expInfo['monitor_width'],
            distance=self.expInfo['monitor_dist']
            )
        self.win = visual.Window(
            fullscr=False,
            monitor=self.monitor,
            units="pix",
            size=[1280, 720]
            )
        
        FR = self.win.getActualFrameRate()
        self.expInfo['FR'] = FR 
        self.pix_per_deg = (self.win.size[1]/
            (np.degrees(
                np.arctan(
                    self.expInfo['monitor_height']/self.expInfo['monitor_dist']
                    ))))  



    def setup_stim(self):
        #TODO: this all needs to be stored somehow
        position = np.array([-15,15])
        sf = .08
        self.tf=2
        #I guess just define the grating and such?
        self.phase_increment = self.tf/self.expInfo['FR']
        self.stim_on_frames = int(self.stim_time*self.expInfo['FR'])
        
        self.grating = visual.GratingStim(
            win=self.win,
            size=10*self.pix_per_deg,
            pos=position*self.pix_per_deg,
            sf=sf/self.pix_per_deg,
            units='pix',
            ori=180+45,
            mask='circle',
        )     
        


    def setup_exp(self):
        base_dir = 'C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/'
        self.expInfo = {'mouse':'Mfake','date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S')}

        self.filename = base_dir + self.expInfo['date']+'_' + self.expInfo['mouse']

        self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
            dataFileName = self.filename,
            extraInfo = self.expInfo)



    def gen_conds(self):
        #TODO: make session data determine this
        #TODO: save this?
        tf = 2 #temporal frequency
        sizes = [0,20]
        intensities = {}
        intensities[0] = [0]
        intensities[20] = [2,8,16,32,64,80]
        intensities[10] = [2,16,32,64, 100]
        #create trial conditions
        self.size_int_response = []
        for temp in range(50):
            mini_size_int_response = []
            for _ in range(4):
                for s in sizes:
                    for ins in intensities[s]:
                        mini_size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0})
            random.shuffle(mini_size_int_response)
            self.size_int_response += mini_size_int_response



    def teardown_daq(self):
        pass



    def close(self):
        self.exp.saveAsWideText(self.filename)
        self.trials.saveAsWideText(self.filename + '_trials')
        self.teardown_daq()



    async def present_grating(self):
        phase = 0
        s = time.time()
        for frame in range(self.stim_on_frames):                   
            phase += self.phase_increment
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
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = None
        last_send = time.time()

        #send init trial info 
        await self.websocket.send(json.dumps({
            'type': 'initTrial',
            'data': {
                'session_id': self.session_id,
                'trial_number': self.trials.thisN,
                'contrast': trial['intensity'],
                'stim_size': trial['size'],
                'is_optogenetics': False,
            }}))
        
        while trial_still_running:
            if time.time()-last_send > .02:
                await self.websocket.send(json.dumps({'type': 'updateData',
                    'data': {
                        'session_id': self.session_id,
                        'trial_number': self.trials.thisN,
                        'timestamp': self.session_timer.getTime(),
                        'is_stim':0,
                        'is_licking':np.random.randint(2),
                        'is_false_alarm': 0,
                        'is_port_open':np.random.randint(2),
                        'is_led_on': 0,
                        'is_tone': 0,
                        }}))
                last_send = time.time()

            current_time = self.trial_timer.getTime()
            
            if current_time <= self.stim_delay:
                continue

            elif (current_time >= self.stim_delay and 
                  current_time <=
                    self.stim_time+self.stim_delay-.2):
                print(trial['intensity'], trial['size'])
                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size']*self.pix_per_deg)
                await self.present_grating()
                
                
            elif current_time >= self.stim_time + self.stim_delay:
                self.grating.setContrast(0)
                self.grating.draw()

                responded = self.check_lick()

            if responded:
                responded = True,
                if trial['corr_response']:
                    self.deliver_reward()
                
                response_time = current_time
                print(response_time)
                trial_still_running = False
                self.trials.data.add('Response', 1)
                self.trials.data.add('RespTime', response_time)

            elif current_time >= 1.7:

                trial_still_running = False
                responded = False
                self.trials.data.add('Response', 0)

            self.win.flip()

        #TODO: actually run this at end of ISI???
        await self.websocket.send(json.dumps({
            'type': 'endTrial',
            'data': {
                'session_id': self.session_id,
                'trial_number': self.trials.thisN,
                'is_licked': responded,
                'response_time': response_time
            }}))



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
        print('isi is happening')
        if self.is_paused:
            return
        isi = np.random.randint(self.isimin, self.isimax)
        self.isi_timer.reset()
        false_alarm_times = []

        last_send = time.time()
        
        while self.isi_timer.getTime() < isi:
            last_send = await self.send_socket(last_send)

            #handle actual isi
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = self.check_lick()
                if responded:
                    print('false alarm!')
                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()

        #TODO: is this right place to save data
        self.trials.addData('fa_times', false_alarm_times)





if __name__ == '__main__':
    Box()
    #ContrastDetectionTask()