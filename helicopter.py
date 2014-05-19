#ADDED
#Scrolling background
#Replaced Helicopter.start() with Helicopter.__init__()
#Added game over label

#TODO
#End (when the top/bottom is hit)
#Center game over label
#Allow game to restart

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty, \
	ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.label import Label

class Helicopter(Widget):
    general_velocity = NumericProperty(1)
    general_acceleration = NumericProperty(0.1)

    velocity_x = NumericProperty(0); velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    acceleration_x = NumericProperty(0); acceleration_y = NumericProperty(0)
    acceleration = ReferenceListProperty(acceleration_x, acceleration_y)

    touched_down = BooleanProperty(False)
    count = NumericProperty(0)

    def move(self):
        if self.touched_down:
            self.acceleration = Vector(0,self.acceleration_y + self.general_acceleration)
            self.velocity = Vector(0,self.general_velocity) + Vector(*self.acceleration)
            self.pos = Vector(*self.velocity) + self.pos

        else:
            self.acceleration = Vector(0,self.acceleration_y - self.general_acceleration)
            self.velocity = Vector(0,-self.general_velocity) + Vector(*self.acceleration)
            self.pos = Vector(*self.velocity) + self.pos

class HelicopterGame(Widget):
    helicopter = ObjectProperty(None)
    back_scroll_speed = NumericProperty(0.1)
    
    #The __init__ runs when the object is first called.  so you don't need to run a 'start' method as such
    #Watch out of the two '_ _' at the start and end of init.  Missing them off screwed me a few times.
    #Initiates instance
    def __init__(self, **kw):
        super(HelicopterGame, self).__init__(**kw)
        
        #Instructions for drawing scrolling background
        with self.canvas.before:
        	texture = CoreImage('Images/background.png').texture
        	texture.wrap = 'repeat'
        	self.scroll_back = Rectangle(texture=texture, size=self.size, pos=self.pos)
        	
        	Clock.schedule_interval(self.update, 0)
        	
        #Draws initial helicopter
        self.helicopter.center = self.center						#Game Runs without this code, can it be removed?						
        self.helicopter.velocity = Vector(4, 0).rotate(270)         #Game Runs without this code, can it be removed?	
            
    #Moves the vertice co-ordinates of scroll_back        
    def scroll_background(self, *l):
        t = Clock.get_boottime()
        self.scroll_back.tex_coords = -(t * self.back_scroll_speed), 0, -(t * self.back_scroll_speed + 1), 0,  -(t * self.back_scroll_speed + 1), -1, -(t * self.back_scroll_speed), -1 
        
    def update(self, dt):
        #stop if hit top and bottom
        if (self.helicopter.y < 0) or (self.helicopter.top > self.height):
            self.end()
        else:
        	self.scroll_background()
        	self.helicopter.move()

    def on_touch_down(self, touch):
        self.helicopter.touched_down = True

    def on_touch_up(self, touch):
        self.helicopter.touched_down = False 

    def end(self):
		game_over = Label(text = 'GAME OVER')
		self.add_widget(game_over)


class HelicopterApp(App):
    def build(self):
    	#Window size gives the window size to HelicopterGame.__init__() 
    	#Otherwise the buildings are only in the bottom left of the screen
        game = HelicopterGame(size=Window.size)
        return game


if __name__ == '__main__':
    HelicopterApp().run()