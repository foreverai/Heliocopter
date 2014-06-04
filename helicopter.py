'''
ADDED
-Start popup
-Game loop
-Moved entire background (sky and buildings) to seperate widget
-Seperated all helicopter behaviour into its own widget
-Initilised helicopter position and speed

TODO
-Add walls
-Add obstacles
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
from kivy.graphics import Color, Bezier, Line
import random

class BezierLine(Widget):
    points_a=[]; points_b=[]
    x_list=[]; y_list=[]
    x_start=-300; x_end=1400; x_step=100
    #for later, we can slowly increase y end to make the gap between the walls thinner
    y_start=0; y_end=200; y_diff=600-y_end

    #maybe also increase velocity slowly
    velocity=5

    update_y=False

    def __init__(self, *args, **kwargs):
        super(BezierLine, self).__init__(*args, **kwargs)
        self.points_a = self.initialise_points()
        self.points_b = self.make_points_b(self.points_a)

        with self.canvas:
            Color(1.0, 0.0, 0.0)

            self.bezier_a = Bezier(
                    points=self.points_a,
                    segments=180,
                    loop=False,
                    )

            self.bezier_b = Bezier(
                    points=self.points_b,
                    segments=180,
                    loop=False,
                    )

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
        self.bezier_a.points=a_list
        self.bezier_b.points=b_list

class StartPopUp(Popup):
    popup_size = ListProperty([.2, .2])
    
    def __init__(self, HelicopterGame, **kw):
        super(StartPopUp, self).__init__(**kw)
        self.HelicopterGame = HelicopterGame
           
    def start_click(self):
        self.HelicopterGame.start_game() 
        
class Background(Widget):
    back_scroll_speed = NumericProperty(0.1)
    texture = CoreImage('Images/background.png').texture
    texture.wrap = 'repeat'
    #These points are from a print of self.texture_coords in def scroll_background
    #they give the intiial position of the background
    #minus parts are the co-ordinates of a flipped image of the background 
    texture_coords = ListProperty([-0.3, 0.0, -1.3, 0.0, -1.3, -1.0, -0.3, -1.0])
    
    def __init__(self, **kw):
        super(Background, self).__init__(**kw)
            
    def scroll_background(self, *l):
        t = Clock.get_boottime()
        self.texture_coords = -(t * self.back_scroll_speed), 0, -(t * self.back_scroll_speed + 1), 0,  -(t * self.back_scroll_speed + 1), -1, -(t * self.back_scroll_speed), -1              
        
class Helicopter(Widget):
    #How to change these to percentages?
    start_position = ListProperty([200, 200])
    general_velocity = NumericProperty(1)
    general_acceleration = NumericProperty(0.1)

    velocity_x = NumericProperty(0); velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    acceleration_x = NumericProperty(0); acceleration_y = NumericProperty(0)
    acceleration = ReferenceListProperty(acceleration_x, acceleration_y)

    touched_down = BooleanProperty(False)
    
    def __init__(self, **kw):
        super(Helicopter, self).__init__(**kw) 
    
    #ensures helicopter isn't moving when game is restarted
    def initilise(self):
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.acceleration_y = 0
        self.pos = self.start_position
        
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
    def alive_check(self, HelicopterGame):
        self.HelicopterGame = HelicopterGame
        #Dead
        if (self.y < 0) or (self.top > self.HelicopterGame.height):
            self.HelicopterGame.end_game()
        #Alive    
        else:
            return True 
        
class HelicopterGame(Widget):
    helicopter = ObjectProperty(None)
    background = ObjectProperty(None)
    bezierline = ObjectProperty(None)
    game_state = BooleanProperty(False)
    
    def __init__(self, **kw):
        super(HelicopterGame, self).__init__(**kw) 
        
    #runs at beginning on clock schedule and at end game    
    def start_popup(self, *args):    
        sp = StartPopUp(self)    #Passes HelicopterGame widget to popup
        sp.open() 
    
    #Runs when popup is clicked        
    def start_game(self):
        self.helicopter.initilise()
        self.game_state = True    
        self.line=BezierLine()          
                    
    def on_touch_down(self, touch):
        self.helicopter.touched_down = True

    def on_touch_up(self, touch):
        self.helicopter.touched_down = False 
    
    #Runs when alive_check detects a collision    
    def end_game(self):
        self.helicopter.touched_down = False    #Need this line as the on_touch_up event isn't fired when the helicopter crashes
        self.game_state = False
        sp = StartPopUp(self)
        sp.open()       
    
    def update(self, dt):
        if self.game_state:
            self.helicopter.alive_check(self)     #passes helicoptergame instance to method
            self.background.scroll_background()
            self.helicopter.move()    
            self.bezierline.move()

class HelicopterApp(App):
    def build(self):
        game = HelicopterGame()
        Clock.schedule_once(game.start_popup, 1)
        Clock.schedule_interval(game.update, 0)
        return game

if __name__ == '__main__':
    HelicopterApp().run()