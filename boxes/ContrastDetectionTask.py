from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
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
            try:
                async with websockets.connect(my_url) as websocket:
                    print('new websocket connection!')
                    self.websocket = websocket

                    while True:
                        #TODO: make this actually run isi and recv at same time, 
                        # waiting for whichever returns first
                        #and then run trial separately
                        try:
                            response = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=.01
                            )

                            self.handle_event(response)
                        except asyncio.TimeoutError:
                            pass

                        if self.session and not self.session.is_ended:
                            await self.session.run_trial()
            except:
                print('connection lost')

                    

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
        
        #task variables
        #TODO: ALL these need to be stored?
        position = np.array([-15,15])
        sf = .08
        self.stim_delay = .2 #in s
        self.stim_time = .6 #in s
        self.response_window = 1 # in s
        self.isimin = 3 # in s
        self.isimax = 8 #in s
        self.grace_time = 1 #in s
        self.water_time = 20 #in ms
        self.tf=2
        
        self.setup_monitor()
        self.gen_conds()
        
        #and some more general variables
        self.phase_increment = self.tf/self.expInfo['FR']
        self.stim_on_frames = int(self.stim_time*self.expInfo['FR'])
        print('conditions genned')
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(
            win=self.win,
            size=10*self.pix_per_deg,
            pos=position*self.pix_per_deg,
            sf=sf/self.pix_per_deg,
            units='pix',
            ori=180+45,
            mask='circle',
        )
        
        self.setup_daq()
        
        self.idx = 0

        #create a trial handler
        self.trials = data.TrialHandler(self.size_int_response, 1, method='sequential')
        self.trials.data.addDataType('Response')
        self.exp.addLoop(self.trials)
        #asyncio.get_event_loop().run_until_complete(self.run_blocks())

    def setup_daq(self):
        #TODO
        pass
    
    def setup_monitor(self):
        #monitor variables
        monitor_width = 22.5 #in cm
        monitor_height = 13 #in cm
        monitor_dist = 10 #in cm
        
        #initialize
        self.monitor = monitors.Monitor('Default', width=monitor_width, distance=monitor_dist)
        self.win = visual.Window(fullscr=False, monitor=self.monitor, units="pix", size=[1280, 720])
        
        FR = self.win.getActualFrameRate()
        self.expInfo['FR'] = FR 
        self.expInfo['monitor_height'] = monitor_height
        self.expInfo['monitor_dist'] = monitor_dist
        self.pix_per_deg = self.win.size[1]/(np.degrees(np.arctan(monitor_height/monitor_dist)))       
        
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
                    'trial_number': 1,
                    'timestamp': time.time(),
                    'is_stim':1,
                    'is_licking':np.random.randint(2),
                    'is_false_alarm': 0,
                    'is_port_open':np.random.randint(2),
                    'is_led_on': 0,

                    }}))
            self.idx+=1
        print(time.time()-s)

    async def run_trial(self):
        #TODO: figure out what's up with which next to call and where data is
        #self.exp.nextEntry()
        trial = self.trials.next()
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = np.nan
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
            if time.time()-last_send > .01:
                await self.websocket.send(json.dumps({'type': 'updateData',
                    'data': {
                        'trial_number': self.trials.thisN,
                        'timestamp': time.time(),
                        'is_stim':0,
                        'is_licking':np.random.randint(2),
                        'is_false_alarm': 0,
                        'is_port_open':np.random.randint(2),
                        'is_led_on': 0,

                        }}))
                last_send = time.time()
            self.idx+=1

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

        await self.websocket.send(json.dumps({
            'type': 'endTrial',
            'data': {
                'is_licked': True,
                'response_time': response_time
            }}))

    def deliver_reward(self):
        pass

    def check_lick(self):
        return False

    async def run_isi(self):

        user_quit = False
        isi = np.random.randint(self.isimin,self.isimax)

        self.isi_timer.reset()
        last_send = time.time()
        false_alarm_times = []
        while self.isi_timer.getTime() < isi:
            if time.time()-last_send > .01:
                await self.websocket.send(json.dumps({'type': 'updateData',
                    'data': {
                        'trial': 1,
                        'timestamp': time.time(),
                        'is_stim':0,
                        'is_licking':np.random.randint(2),
                        'is_false_alarm': 0,
                        'is_port_open':np.random.randint(2),
                        'is_led_on': 0,

                        }}))
                last_send = time.time()

            #check for quit
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, false_alarm_times

            #handle actual isi
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = self.check_lick()
                if responded:
                    print('false alarm!')
                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
        return user_quit, false_alarm_times

if __name__ == '__main__':
    Box()
    #ContrastDetectionTask()