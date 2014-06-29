'''
ADDED
-Modified tunnel to mesh
-Made first part of tunnel straight
-Added tunnel collisions
-Mode tunnel gap get smaller

TODO
-Change points to percentages
-Tidy up code could probably jsut generate bottom list, and do bottom list plus gap for top list
-Add texture to walls
-Alter how tunnel collisions/new obstacle position is calculated
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
    
    vertices_top = ListProperty([])
    indices_top = ListProperty([])
    vertices_bot = ListProperty([])
    indices_bot = ListProperty([])
    new_bot_y = NumericProperty()
    
    'gap between top and bottom terrain'
    gap = NumericProperty(500)
    'tunnel speed needs to be the same as obstacle speed'
    velocity = NumericProperty(5)
    'the speed at which the gap gets smaller'
    gap_change = NumericProperty(0.1)
    i = 1
    
    def __init__(self, **kw):
        super(Tunnel, self).__init__(**kw)
        self.generate_bot()
        self.generate_top()
    
    def initilise(self):
        self.gap = 500
        self.vertices_bot = [] 
        self.vertices_top = []
        self.indices_bot = [] 
        self.indices_top= []
        self.generate_bot()
        self.generate_top()
    
    def generate_bot(self):
        self.vertices_bot = -100, 0, 0, 0
        self.indices_bot.append(1)
        for x in range(-100, 900, 50):
            self.i = self.i+1
            y = 50
            self.vertices_bot.extend([x, y, 0, 0])
            self.indices_bot.append(self.i)
        self.vertices_bot.extend([900, 0, 0, 0])
        self.indices_bot.extend([self.i+1,])    
        self.i = 1
        
    def generate_top(self):
        self.vertices_top = -100, 600, 0, 0
        self.indices_top.append(1)
        for x in range(-100, 900, 50):
            self.i = self.i+1
            y = self.gap+50
            self.vertices_top.extend([x, y, 0, 0])
            self.indices_top.append(self.i)
        self.vertices_top.extend([900, 600, 0, 0])
        self.indices_top.extend([self.i+1])    
        self.i = 1
    
    def move_bot(self):
        list_length = len(self.vertices_bot)
        new_point = len(self.vertices_bot) - 4
        lower_bound = self.vertices_bot[81] - 40
        upper_bound = self.vertices_bot[81] + 40
        top = upper_bound + self.gap
        if lower_bound < 0:
            lower_bound = 0
        if top > self.game.height:
            upper_bound = int(self.game.height - self.gap)           
        vx = 900
        self.new_bot_y = randrange(lower_bound, upper_bound, 1)
        tx = 0
        ty = 0
        for x in range(4, list_length-4, 4):
            if self.vertices_bot[x] < -100:
                self.vertices_bot.insert(new_point, ty)
                self.vertices_bot.insert(new_point, tx)
                self.vertices_bot.insert(new_point, self.new_bot_y)
                self.vertices_bot.insert(new_point, vx)                
                del self.vertices_bot[x]
                del self.vertices_bot[x]
                del self.vertices_bot[x]
                del self.vertices_bot[x]
            self.vertices_bot[x] = self.vertices_bot[x] - self.velocity        
                
    def move_top(self):
        list_length = len(self.vertices_top)
        new_point = len(self.vertices_top)-4
        vx = 900
        vy = self.new_bot_y + self.gap
        tx = 0
        ty = 0
        for x in range(4, list_length-4, 4):
            if self.vertices_top[x] < -100:
                self.vertices_top.insert(new_point, ty)
                self.vertices_top.insert(new_point, tx)
                self.vertices_top.insert(new_point, vy)
                self.vertices_top.insert(new_point, vx)                
                del self.vertices_top[x]
                del self.vertices_top[x]
                del self.vertices_top[x]
                del self.vertices_top[x]   
            self.vertices_top[x] = self.vertices_top[x] - self.velocity     
                
    def update(self):
        #helicopter height + obstacle height + allowable margin
        min_gap = self.game.helicopter.height + 80 + 100
        if self.gap > min_gap:
            self.gap = self.gap - self.gap_change 
        self.move_bot()
        self.move_top()
        
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
        self.tunnel_top = int(self.game.tunnel.vertices_top[73] - self.obstacle_height/2)  #obstacle can be half way into wall
        self.tunnel_bot = int(self.game.tunnel.vertices_bot[73] - self.obstacle_height/2)
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
    general_velocity = NumericProperty(1)
    general_acceleration = NumericProperty(0.2)
    
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
    
    def obstacle_collision(self):
        for obstacle in self.game.obstacles:
            if self.collide_widget(obstacle):
                self.game.end_game()
    
    'very hacky, need to fix'
    def tunnel_collision(self):
        cond1 = self.get_top() > self.game.tunnel.vertices_top[21]
        cond2 = self.y < self.game.tunnel.vertices_bot[21]
        if cond1 or cond2:
            self.game.end_game()
                    
    def alive_check(self):
        self.obstacle_collision()
        self.tunnel_collision()
        
class HelicopterGame(Widget):
    app = ObjectProperty(None)
    helicopter = ObjectProperty(None)
    background = ObjectProperty(None)
    tunnel = ObjectProperty(None)
    obstacles = ListProperty([])
    
    'time until first obstacle'
    time_first_ob = NumericProperty(1)   
    game_state = BooleanProperty(False)
    
    #Runs when popup is clicked        
    def start_game(self):
        self.tunnel.initilise()
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
            self.tunnel.update()  
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