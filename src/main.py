import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from functools import partial
import numpy as np
import cv2
import sys,os, cPickle
from threading import Thread
from levels import main_game,original_game
import datetime
import MUSE_server as mps
from kivy.config import Config
import keyboard
kivy.require('1.9.0')


def SelfReport(path):
    global server,round_set,user_id, round_id, quit

    fatigue_history = []
    fatigue = []
    round_id = None

    while (True):  # making a loop

            if keyboard.is_pressed('a'):  # if key 'q' is pressed
                fatigue.append(round_id-1)

            if quit:
                list_fatigue =  sorted(list(set(fatigue)))
                fatigue_score =  list(np.arange(len(list_fatigue)))
                for i in range(len(list_fatigue)):
                     if i == 0:
                         fatigue_history += [fatigue_score[i]] * (list_fatigue[i])
                     elif i < len(list_fatigue)-1:
                         fatigue_history += [fatigue_score[i]] * (list_fatigue[i]-list_fatigue[i-1])
                     else:
                         fatigue_history += [fatigue_score[-1]]*(round_id-len(fatigue_history))
                if not list_fatigue:
                    fatigue_history = [0]*round_id

                with open(path + '.csv', 'w') as f:
                   for i in fatigue_history:
                     f.write((str(i)+'\n'))
                f.close()
                break




def readMuse(path):
    global server,round_set,user_id, round_id, quit
    intro = open('test', 'w')
    server = mps.initialize(intro)
    server.start()
    round_id = None
    prev_round = round_id
    while(True):
        if round_id != prev_round:
            eeg_name = ('/').join((path,str(round_set) + "_" + str(round_id)))
            out = open(eeg_name, 'w')
            server.f = out
            prev_round = round_id
        if quit:
            server.stop()
            break


def readFrames(path):

    global round_set,user_id, round_id, quit,modality, store_data_path
    frameCounter=1
    cap = cv2.VideoCapture(0)
    frame_struct = []
  
    while(True):
        ret, frame = cap.read()
        if frameCounter%10 == 0:
            #cv2.imshow('frame',frame)
            if round_set > len(frame_struct)-1:
                    frame_struct.append([])
            frame_struct[round_set].append(frame)
            fname = str(round_set)+"_"+str(round_id)+"_"+str(frameCounter)+"_"+str(datetime.datetime.time(datetime.datetime.now()))+".jpg"
            cv2.imwrite(os.path.join(path, fname), frame)
        frameCounter+=1

        if quit:
            filename = store_data_path+"/images/user_"+user_id+'_'+modality+"/data"
            np.save(filename,frame_struct)
            break

    # When everything done, release the capture
    cap.release()
    sys.exit()
    #cv2.destroyAllWindows()


# Initialize Variables
class WisconsinGame(FloatLayout):

    def __init__(self, **kwargs):
        super(WisconsinGame, self).__init__(**kwargs)
        
        global round_set,round_id,modality,game_type
        round_set = 0

        self.trial = 0
        round_id = self.trial

        if game_type =='o':
            self.levels_all = original_game()
        else:
            self.levels_all = main_game()

        #print   "LEVELS:",self.levels_all

        self.countdown_time = 6 #seconds (1 -->7)
        self.level_change_ratio = 4 #trials to change the level
        self.total_trials = len(self.levels_all) * self.level_change_ratio#66  #total trials

        self.score = 0
        self.score_total = 0

        self.question_in_level = 0

        self.data = []
        self.choice = ""
        self.clock = 0
        self.correct = 0
        #self.errors = 0
        self.rule_change_round = 1
        self.persistent_errors = 0
        self.non_persistent_errors = 0
        self.error_persistant = 0

        global response_given 
        response_given = False

        self.valid_response = False

        self.commands_all = {}
        self.commands_all['color'] = ["red","green","blue","yellow","magenta"]
        self.commands_all['number'] = ["one","two","three","four","five"]
        self.commands_all['shape'] = ["circle","triangle","cross","star","heart"]

        self.commands = {}


        self.ids['b1'].disabled = True       
        self.ids['b2'].disabled = True       
        self.ids['b3'].disabled = True       
        self.ids['b4'].disabled = True     
        self.ids['b5'].disabled = True     

        self.level = 0 #gamelevel
        self.prev_level = None
        self.prev_ids = None
        self.buttons_disabled = []
        self.level_change()

        self.major_modality = modality#self.modalities[np.random.randint(3)]
        self.major_stimuli = np.random.permutation(self.commands.keys())[0]
        self.stimuli_type = ''
        
        self.next_round("")

        
#Evaluate answer according to current major modality
    def check_result(self):
        if self.stimuli_type in ['red','circle','one'] and  self.choice == "b1":
           self.correct += 1  
           self.valid_response = True
           self.error_persistant = 0
        elif self.stimuli_type in ['green','triangle','two'] and  self.choice == "b2":
           self.correct += 1  
           self.valid_response = True
           self.error_persistant = 0
        elif self.stimuli_type in ['blue','cross','three'] and  self.choice == "b3":
            self.correct += 1  
            self.valid_response = True
            self.error_persistant = 0
        elif self.stimuli_type in ['yellow','star','four'] and  self.choice == "b4":
            self.correct += 1  
            self.valid_response = True
            self.error_persistant = 0
        elif self.stimuli_type in ['magenta','heart','five'] and  self.choice == "b5":
            self.correct += 1  
            self.valid_response = True
            self.error_persistant = 0
        else:
            self.valid_response = False
            #self.errors+=1
            if self.trial == self.rule_change_round +1 or self.trial == self.rule_change_round:
                self.non_persistent_errors +=1
                self.error_persistant = 1
            else:
                self.persistent_errors +=1
                self.error_persistant = 2
       
        if self.valid_response == True and self.question_in_level >2:
            #print "Clock",self.clock
            self.score = float(self.level+1)/float((self.clock+1)*(self.question_in_level-2))
            self.score_total += self.score
            #print "SCORE", self.score
            #print "SCORE TOTAL", self.score_total
        else:
            self.score = 0
       

#Change object's opacity
    def chage_opacity(self,wid_id,_):
                self.ids[wid_id].opacity = 0

#Give audiovisual feedback
    def feedback(self):
        if self.valid_response == True:
            self.ids['feedback'].source = "../AppData/correct.png"
            sound = SoundLoader.load('../AppData/'+'correct.wav')
            sound.play()   
        else:    
            self.ids['feedback'].source = "../AppData/wrong.png"
            sound = SoundLoader.load('../AppData/'+'wrong.wav')
            sound.play()   
        self.ids['feedback'].opacity = 1
        Clock.schedule_once(partial(self.chage_opacity,'feedback'), 1)

#Capture when a button is pressed
    def button_pressed(self):
        global response_given
        response_given = True

#Start countdouwn
    def countdown(self,_):
         global response_given
         if self.clock > self.countdown_time and response_given==False:  
            self.ids['b1'].disabled = True       
            self.ids['b2'].disabled = True       
            self.ids['b3'].disabled = True       
            self.ids['b4'].disabled = True       
            self.ids['b5'].disabled = True 
            self.ids['b5'].disabled = True# give error when predifined time has passed and terminate current timer
            self.valid_response = False
            self.persistent_errors += 1
            self.error_persistant = 2
            self.feedback()
            #self.data.append([self.trial, self.question_in_level,self.level+1, self.score, self.major_modality,self.major_stimuli, self.stimuli_type,self.valid_response, self.error_persistant ,self.clock+1, self.choice,self.perm[0],self.perm[1],self.perm[2],self.audio,self.text,self.visual,self.correct,self.non_persistent_errors, self.persistent_errors]) 
            self.data.append([self.trial, self.question_in_level,self.level+1, self.score,self.major_stimuli, self.stimuli_type, self.valid_response, self.error_persistant ,self.clock+1, self.correct,self.non_persistent_errors, self.persistent_errors]) 
            if self.trial == self.total_trials:
            #if not self.levels_all:
                Clock.schedule_once(self.log_and_terminate, 1.5)
            Clock.schedule_once(self.next_round, 1.5)
            return False

         if response_given==True:  #terminate timer when answer is given in time
            return False

         self.clock += 1
         #print self.clock


    def level_change(self):
        #print self.commands_all

    # CHANGE LEVELS RANDOMLY
        #self.level = 0
        #while self.level == 0: #disable level0
            #self.level = np.random.randint(5)

    # CHOOSE FROM PRE-SELCTED LEVEL SEQUENCES
        self.level = self.levels_all.pop(0)
        if self.prev_level == self.level:
            ids = self.prev_ids
        else:
            ids = np.random.permutation(5)
            self.prev_ids = ids

        self.prev_level = self.level

        self.commands = dict(self.commands_all)
        
        if self.level == 3:
            self.commands['color'] = [self.commands_all['color'][ids[0]],self.commands_all['color'][ids[1]],self.commands_all['color'][ids[2]],self.commands_all['color'][ids[3]]]
            self.commands['shape'] = [self.commands_all['shape'][ids[0]],self.commands_all['shape'][ids[1]],self.commands_all['shape'][ids[2]],self.commands_all['shape'][ids[3]]]
            self.commands['number'] = [self.commands_all['number'][ids[0]],self.commands_all['number'][ids[1]],self.commands_all['number'][ids[2]],self.commands_all['number'][ids[3]]]
            
            self.ids['b'+str(ids[4]+1)].disabled = True
            self.buttons_disabled = ['b'+str(ids[4]+1)]
        elif self.level == 2:
            self.commands['color'] = [self.commands_all['color'][ids[0]],self.commands_all['color'][ids[1]],self.commands_all['color'][ids[2]]]
            self.commands['shape'] = [self.commands_all['shape'][ids[0]],self.commands_all['shape'][ids[1]],self.commands_all['shape'][ids[2]]]
            self.commands['number'] = [self.commands_all['number'][ids[0]],self.commands_all['number'][ids[1]],self.commands_all['number'][ids[2]]]

            self.ids['b'+str(ids[3]+1)].disabled = True       
            self.ids['b'+str(ids[4]+1)].disabled = True
            self.buttons_disabled = ['b'+str(ids[3]+1),'b'+str(ids[4]+1)]
        elif self.level == 1 :
            self.commands['color'] = [self.commands_all['color'][ids[0]],self.commands_all['color'][ids[1]]]
            self.commands['shape'] = [self.commands_all['shape'][ids[0]],self.commands_all['shape'][ids[1]]]
            self.commands['number'] = [self.commands_all['number'][ids[0]],self.commands_all['number'][ids[1]]]
       
            self.ids['b'+str(ids[2]+1)].disabled = True       
            self.ids['b'+str(ids[3]+1)].disabled = True       
            self.ids['b'+str(ids[4]+1)].disabled = True
            self.buttons_disabled = ['b'+str(ids[2]+1),'b'+str(ids[3]+1),'b'+str(ids[4]+1)]

        elif self.level == 0 :
            self.commands['color'] = [self.commands_all['color'][ids[0]]]
            self.commands['shape'] = [self.commands_all['shape'][ids[0]]]
            self.commands['number'] = [self.commands_all['number'][ids[0]]]

            self.ids['b'+str(ids[1]+1)].disabled = True       
            self.ids['b'+str(ids[2]+1)].disabled = True       
            self.ids['b'+str(ids[3]+1)].disabled = True       
            self.ids['b'+str(ids[4]+1)].disabled = True
            self.buttons_disabled = ['b'+str(ids[1]+1),'b'+str(ids[2]+1),'b'+str(ids[3]+1),'b'+str(ids[4]+1)]

        #print
        #print "LEVEL: ",self.level+1
        #print self.commands
        #print


#Draw next round
    def next_round(self,_):
        global response_given, round_id, round_set
        
        response_given = False
        self.trial += 1
        round_id = self.trial #[1,#total_trials]
        self.question_in_level += 1 #[1,#trials_in_a_round]
        
        #Initialize countdown
        self.clock = 0
        Clock.schedule_interval(self.countdown, 1)
        

        # Change Stimuli
        if self.trial%self.level_change_ratio == 1 and self.trial > 1:# and self.valid_response == True:
            #print "CHANGE STIMULI"
            self.major_stimuli = np.random.permutation(self.commands.keys())[0]

            self.ids['b1'].disabled = False       
            self.ids['b2'].disabled = False       
            self.ids['b3'].disabled = False       
            self.ids['b4'].disabled = False       
            self.ids['b5'].disabled = False
            self.question_in_level = 1
            self.buttons_disabled = []

            #global round_set            
            round_set += 1  #[1,#number_of_rounds]               
            self.rule_change_round = self.trial
            self.level_change()

        for i in ["b1","b2","b3","b4","b5"]:
            if i in self.buttons_disabled:
                self.ids[i].disabled = True
            else:
                self.ids[i].disabled = False

        #update stimulis by securing that each stimuli will represent a different button if possible
        mix_the_command = np.random.permutation(self.level+1)       

        if len(mix_the_command) >= 3: # in levels 3 and 4 all stimulis are different
            self.color = self.commands['color'][mix_the_command[0]]
            self.shape = self.commands['shape'][mix_the_command[1]]
            self.number = self.commands['number'][mix_the_command[2]]
        elif len(mix_the_command) == 2: #in level two, two of the randomly chosen stimulis represent the same button
            rand = np.random.rand()
            if rand <= 0.33:
                self.color = self.commands['color'][mix_the_command[0]]
                self.shape = self.commands['shape'][mix_the_command[0]]
                self.number = self.commands['number'][mix_the_command[1]]
            elif rand <= 0.66:
                self.color = self.commands['color'][mix_the_command[1]]
                self.shape = self.commands['shape'][mix_the_command[0]]
                self.number = self.commands['number'][mix_the_command[0]]
            else:
                self.color = self.commands['color'][mix_the_command[0]]
                self.shape = self.commands['shape'][mix_the_command[1]]
                self.number = self.commands['number'][mix_the_command[0]]
        elif len(mix_the_command) == 1:#in level 1 all stimuli represent the same button
                self.color = self.commands['color'][mix_the_command[0]]
                self.shape = self.commands['shape'][mix_the_command[0]]
                self.number = self.commands['number'][mix_the_command[0]]

        instruction = ('_').join((self.shape,self.color,self.number))
        if self.major_modality == 'v':
            self.ids['instruction'].source ='../AppData/wisconsin_visual/'+instruction+'.jpg'
        elif self.major_modality == 't':
            self.ids['instruction'].source ='../AppData/wisconsin_textual/'+instruction+'.jpg'
        else :
            self.ids['instruction'].source ='../AppData/wisconsin_auditory/black.jpg'
            sound = SoundLoader.load('../AppData/wisconsin_auditory/'+instruction+'.wav')     
            sound.play()   
            
        if self.major_stimuli =="number":
            self.stimuli_type = self.number
        elif self.major_stimuli == "shape":
            self.stimuli_type = self.shape
        else:
            self.stimuli_type = self.color

        #print self.stimuli_type, self.trial

        #print "Round:",self.trial
        #print self.major_modality
        #print self.major_stimuli
        #print self.stimuli_type

#Terminate session function
    def log_and_terminate(self,_):
        global user_id, email,quit,modality,store_data_path
        quit = True
        path_save = store_data_path+'user_performance/'
        if not os.path.exists(path_save):
            os.makedirs(path_save)
        path_leaderboard =  store_data_path + "leaderbord.csv"
        leaderbord_pickle =  store_data_path+"leaderbord"

        if not os.path.exists(path_save):
            os.makedirs(path_save)
        with open(path_save + 'user_'+ user_id+'_'+modality+'_'+str(self.score_total)+'.csv','w') as f:
                    f.write("Round\tQuestion\tLevel\t Score\tStimuli\tStimuli Type\tResponse\tPersistence\tTime\tCorrect\tNON-PER Errors\tPER Errorsn\n")
                    for sample in self.data:
                        f.write((('\t').join([str(i) for i in sample])+'\n'))
        f.close

      # save cpickle file with correct,correct_red,correct_blue
        d={}
        if os.path.isfile(leaderbord_pickle):
            fo = open(leaderbord_pickle, "rb")
            d = cPickle.load(fo)
            fo.close()

        d[modality+'_'+user_id+'_'+email] = self.score_total
        fo = open(leaderbord_pickle, "wb")
        cPickle.dump(d, fo, protocol=cPickle.HIGHEST_PROTOCOL)
        fo.close()

        with open(path_leaderboard,'w') as f:
            f.write('ID\tMODALITY\tEMAIL\tSCORE\n')
            for key, value in sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=True):
                f.write((('\t').join((key.split('_')[1],key.split('_')[0],key.split('_')[2],str(value)+"\n"))))
            f.close
        
        sys.exit()


#App control function
    def on_control(self,choice):
        self.ids['b1'].disabled = True       
        self.ids['b2'].disabled = True       
        self.ids['b3'].disabled = True       
        self.ids['b4'].disabled = True     
        self.ids['b5'].disabled = True     
        self.choice = choice
        self.check_result()
        self.feedback()
        self.data.append([self.trial, self.question_in_level,self.level+1, self.score,self.major_stimuli, self.stimuli_type, self.valid_response, self.error_persistant ,self.clock+1, self.correct,self.non_persistent_errors, self.persistent_errors]) 
        # terminate session when round limit has been reached
        if self.trial >= self.total_trials:
        #if not self.levels_all:
            Clock.schedule_once(self.log_and_terminate, 1.5)
        Clock.schedule_once(self.next_round, 1.5)
       

class WisconsinApp(App):
    def build(self):
        return WisconsinGame()





def main(game,user,stimuli,data_path):
    global user_id, email, modality, round_set, round_id, quit, game_type,store_data_path

    # Config.set('graphics', 'width', str(4000))
    # Config.set('graphics', 'height', str(2000))
    Config.set('graphics', 'width', str(1000))
    Config.set('graphics', 'height', str(1000))

    # Parameter initialization
    store_data_path =data_path
    game_type = game
    round_set = 0
    quit = False

    # Create path to stote images if not there
    path_im = store_data_path+ '/images/'
    if not os.path.exists(path_im):
        os.makedirs(path_im)
        path_im = os.path.abspath(path_im)

    path_eeg = store_data_path + '/eeg/'
    if not os.path.exists(path_eeg):
        os.makedirs(path_eeg)
        path_eeg = os.path.abspath(path_eeg)

    path_self = store_data_path + '/fatigue_self_report/'
    if not os.path.exists(path_self):
        os.makedirs(path_self)
        path_self = os.path.abspath(path_self)

    email = user  # user email
    modality = stimuli  # stimuli to use

    # Find the ID of the current User
    dirs = [i for i in os.listdir(path_im) if os.path.isdir(path_im + '/' + i) and modality in i]
    user_id = str(len(dirs))


    # Create directory to store current User's images
    foldername = "/user_" + user_id + '_' + modality + "/"
    path_im = path_im + foldername
    if not os.path.exists(path_im):
        os.makedirs(path_im)
    path_eeg = path_eeg + foldername
    if not os.path.exists(path_eeg):
        os.makedirs(path_eeg)

    print "User: " + user_id, "ID: " + email

    # Run game and recording into threads
    thread1 = Thread(target=WisconsinApp().run)
    thread1.start()

    thread2 = Thread(target=readFrames, args=(path_im,))
    thread2.start()

    thread3 = Thread(target=readMuse, args=(path_eeg,))
    thread3.start()

    thread4 = Thread(target=SelfReport, args=(path_self + foldername[:-1],))
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()


if __name__ == '__main__':
   main('m','test_user','v','../../Wisconsin_Unimodal_Data/')