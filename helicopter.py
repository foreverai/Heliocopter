'''
ADDED
-Added obstacle collisions
-Created widget tree refeerences

TODO
-Add texture to walls
-Add collisions
-Make first part of wall straight (based on time_first_ob if possible)
-Add distance measurement

'''

import kivy
kivy.require('1.8.0')

#if this line is removed theres a'Fatal Python error: (pygame parachute) Segmentation Fault'
#Yet window isn't used in the main file?
from kivy.core.window import Window

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import ListProperty, NumericProperty, \
	ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.popup import Popup
from kivy.modules import inspector
from random import randrange
import random

class StartPopUp(Popup):
    app = ObjectProperty(None)
    'Popup size'
    popup_size = ListProperty([.2, .2])
           
    def start_click(self):
        self.app.game.start_game() 
        
class Background(Widget):
    game = ObjectProperty(None)
    'Speed of scrolling'
    back_scroll_speed = NumericProperty(0.05)
    
    'Background Image'
    texture = CoreImage('Images/background.png').texture
    texture.wrap = 'repeat'
    
    start_position = NumericProperty(0)
    texture_coords = ListProperty([-0.0, 0.0, -1.0, 0.0, -1.0, -1.0, -0.0, -1.0])    #initial co-ordinates of background
    
    def __init__(self, **kw):
        super(Background, self).__init__(**kw)
            
    def scroll_background(self, *l):
        self.texture_coords = -(self.start_position * self.back_scroll_speed), 0, -(self.start_position * self.back_scroll_speed + 1), 0,  -(self.start_position * self.back_scroll_speed + 1), -1, -(self.start_position * self.back_scroll_speed), -1
        self.start_position += self.back_scroll_speed           

class Tunnel(Widget):
    game = ObjectProperty(None)
    points_a=ListProperty([]); points_b=ListProperty([])
    x_list=[]; y_list=[]
    x_start=-300; x_end=1400; x_step=100
    #for later, we can slowly increase y end to make the gap between the walls thinner
    y_start=0; y_end=200; y_diff=600-y_end

    #maybe also increase velocity slowly
    velocity=5

    update_y=False

    def __init__(self, *args, **kwargs):
        super(Tunnel, self).__init__(*args, **kwargs)
        self.points_a = self.initialise_points()
        self.points_b = self.make_points_b(self.points_a)

    def make_points_b(self, l):
        x=l[::2]
        y=l[1::2]
        new_y=[i+self.y_diff for i in y]
        return self.merge_lists(x,new_y)

    def initialise_points(self):
        self.x_list=range(self.x_start,self.x_end,self.x_step)
        self.y_list=self.generate_random_list()
        return self.merge_lists(self.x_list, self.y_list)

    def generate_random_list(self):
        y=[]
        for i in range(self.x_start,self.x_end,self.x_step):
            y.extend([random.randint(self.y_start,self.y_end)])
        return y

    def merge_lists(self, x, y):
        list=[]
        for i in range(len(x)):
            list.extend([x[i]])
            list.extend([y[i]])
        return list

    def flow_x(self,x):
        self.update_y=False
        x_list=[]
        x_length=len(x)
        x_limit=self.x_end-self.x_step
        for i in range(x_length):
            x_list.extend([x[i]-self.velocity])
        if(x[-1]<=x_limit):
            x_list.pop(0)
            x_list.extend([self.x_end])
            self.update_y=True
        return x_list

    def flow_y(self,y):
        y_list=[]
        y_length=len(y)
        if(self.update_y):
            for i in range(y_length-1):
                y_list.extend([y[i+1]])
            y_list.extend([random.randint(self.y_start,self.y_end)])
            return y_list
        return y

    def move(self):
        self.x_list=self.flow_x(self.x_list)
        self.y_list=self.flow_y(self.y_list)
        a_list=self.merge_lists(self.x_list,self.y_list)
        b_list=self.make_points_b(a_list)
        self.points_a=a_list
        self.points_b=b_list

class Obstacle(Widget):
    game = ObjectProperty(None)
    'size of obstacle'
    obstacle_height = NumericProperty(80)
    obstacle_width = NumericProperty(30)
    sizing = ReferenceListProperty(obstacle_width , obstacle_height)
    
    'obstacle speed, needs to be the same as tunnel speed'
    velocity = ListProperty([5, 0])
    
    'distance between obstacles'
    distance = NumericProperty(300)
    
    #Has the next obstacle been addeed?
    next_added = BooleanProperty(False)
    
    def __init__(self, **kw):
        super(Obstacle, self).__init__(**kw)
        self.start_position() 
    
    #Runs when an instance of the widget is created
    def start_position(self):
        pos_x = self.game.get_right()  #x-co-ordinate of new obstacle
        #Hacky way to link obstacles to wall
        #better way?
        self.tunnel_top = self.game.tunnel.points_b[23] - self.obstacle_height/2  #obstacle can be half way into wall
        self.tunnel_bot = self.game.tunnel.points_a[23] - self.obstacle_height/2
        pos_y = randrange(self.tunnel_bot, self.tunnel_top, 1)  #y-co-ordinate of new obstacle 
        self.pos = pos_x, pos_y
        self.size = self.sizing      #Otherwise size is 100,100 (although visibly doesn't look this size
            
    #Check if obstacle should be added
    def add_check(self):
        screen_right = self.game.get_right()
        current_distance = screen_right - self.pos[0]   #Distance between right hand side of screen and current x co-ordinate of obstacle
        cond1 = current_distance > self.distance
        cond2 = self.next_added == False
        if cond1 and cond2:
            self.game.add_obstacle()
            self.next_added = True
            
    #Check if obstacle should be removed
    def remove_check(self):
        screen_left = 0 - self.obstacle_width  #x-coordinate of left side of screen minus obstacle width
        if self.pos[0] < screen_left:   #0 indicates first position in position list (which is the x_co-ordinate)
            self.game.remove_obstacle()

    def update(self):
        self.add_check()
        self.remove_check() 
        self.pos = Vector(*self.pos) - Vector(*self.velocity)    #current position plus velocity
        
class Helicopter(Widget):
    game = ObjectProperty(None)
    
    'Helicopter physics'
    general_velocity = NumericProperty(2)
    general_acceleration = NumericProperty(0.6)
    
    'helicopter size'
    sizing = ListProperty([0.08, 0.1])
    
    start_position = ([])
    
    start_x = NumericProperty(0)
    start_y = NumericProperty(0)
    start_position = ReferenceListProperty(start_x, start_y)
    
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    acceleration_x = NumericProperty(0)
    acceleration_y = NumericProperty(0)
    acceleration = ReferenceListProperty(acceleration_x, acceleration_y)

    touched_down = BooleanProperty(False)
    got_start_pos = BooleanProperty(False)
        
    #ensures helicopter isn't moving when game is restarted
    #positions helicopter in start position
    def initilise(self):
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.acceleration_y = 0
        #bit of a hacky way to get start position of helicopter for game restart
        #better way?
        if self.got_start_pos == False:
            self.start_position = self.pos
            self.got_start_pos = True
        self.pos = self.start_position              
        
    def on_touch_down(self, touch):
        self.touched_down = True

    def on_touch_up(self, touch):
        self.touched_down = False     
        
    def move(self):
        if self.touched_down:
            self.acceleration = Vector(0,self.acceleration_y + self.general_acceleration)
            self.velocity = Vector(0,self.general_velocity) + Vector(*self.acceleration)
            self.pos = Vector(*self.velocity) + self.pos

        else:
            self.acceleration = Vector(0,self.acceleration_y - self.general_acceleration)
            self.velocity = Vector(0,-self.general_velocity) + Vector(*self.acceleration)
            self.pos = Vector(*self.velocity) + self.pos
    
    #Passed HelicopterGame at a method level.  How to pass it to whole class?
    #Like for StartPopUp
    def alive_check(self):
        #obstacle collision
        for obstacle in self.game.obstacles:
            if self.collide_widget(obstacle):
                self.game.end_game()
        #Dead
        if (self.y < 0) or (self.top > self.game.height):
            self.game.end_game()
        #Alive    
        else:
            return True 
        
class HelicopterGame(Widget):
    app = ObjectProperty(None)
    helicopter = ObjectProperty(None)
    background = ObjectProperty(None)
    tunnel = ObjectProperty(None)
    obstacles = ListProperty([])
    
    'time until first obstacle'
    time_first_ob = NumericProperty(2)   
    game_state = BooleanProperty(False)
    
    #Runs when popup is clicked        
    def start_game(self):
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
            self.obstacles = self.obstacles[1:] 
        self.helicopter.initilise()
        self.game_state = True  
        Clock.schedule_once(self.add_obstacle, self.time_first_ob)   #adds obstacle after certain time, unscheduled in end_game if game ends before event fires
    
    #Runs on game start and when conditions are met in Obstacle() thereafter    
    def add_obstacle(self, *args):
        new_obstacle = Obstacle() 
        self.add_widget(new_obstacle)
        self.obstacles = self.obstacles + [new_obstacle]   
    
    #Runs when conditions are met in Obstacle()        
    def remove_obstacle(self):
        self.remove_widget(self.obstacles[0])
        self.obstacles = self.obstacles[1:]    #not sure what this line does, moves next obstacle to start of array?
    
    #Runs when alive_check detects a collision    
    def end_game(self):
        Clock.unschedule(self.add_obstacle)
        self.helicopter.touched_down = False    #Need this line as the on_touch_up event isn't fired when the helicopter crashes
        self.game_state = False
        self.app.start_popup()     
    
    def update(self, dt):
        if self.game_state:
            self.helicopter.alive_check()     
            self.background.scroll_background()
            self.helicopter.move()
            self.tunnel.move()  
            for obstacle in self.obstacles:
                obstacle.update()   

class HelicopterApp(App):
    game = ObjectProperty()
    startpopup = ObjectProperty()

    def build(self):
        self.game = HelicopterGame()
        self.startpopup = StartPopUp()

        Clock.schedule_once(self.start_popup, 1)
        Clock.schedule_interval(self.game.update, 1/60)
        
        inspector.create_inspector(Window, self.game)

        return self.game

    def start_popup(self, *args):    
        self.startpopup.open() 

if __name__ == '__main__':
    HelicopterApp().run()