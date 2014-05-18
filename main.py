'''
Created on 12 Oct 2013

Uses:
Widget that goes up and down on touhc event
Background that moves from right to left repeating

'''
import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, BooleanProperty
    
class Controller(Widget):
    #Starting properties
    touched_down = BooleanProperty(False)
    helicopter_velocity = NumericProperty(0)
    heli_rise_accel = NumericProperty(0.07)
    heli_fall_accel = NumericProperty(0.07)
    back_scroll_speed = NumericProperty(0.1)

    
    #Initiates instance
    def __init__(self, **kw):
        super(Controller, self).__init__(**kw)
        
        #Instructions for drawing scrolling background
        with self.canvas.before:
            texture = CoreImage('Images/background.png').texture
            texture.wrap = 'repeat'
            self.scroll_back = Rectangle(texture=texture, size=self.size, pos=self.pos)
            
            Clock.schedule_interval(self.update_game, 0)
    
    #Moves the vertice co-ordinates of scroll_back        
    def scroll_background(self, *l):
        t = Clock.get_boottime()
        self.scroll_back.tex_coords = -(t * self.back_scroll_speed), 0, -(t * self.back_scroll_speed + 1), 0,  -(t * self.back_scroll_speed + 1), -1, -(t * self.back_scroll_speed), -1  
        
    #Registers touch down even
    def on_touch_down(self, touch):
        self.touched_down = True
    
    #Registers touch up event    
    def on_touch_up(self, touch):
        self.touched_down = False 
    
    #Calculates helicopters new position    
    def helicopter_position(self):
        #Position of helicopter is increased/decreased linearly
        x = self.ids.helicopter_obj.center_x
        y = self.ids.helicopter_obj.center_y + self.helicopter_velocity
        return (x, y) 
    
    #Places helicopter in new position      
    def helicopter_update(self):
        if self.touched_down:
            self.helicopter_velocity += self.heli_rise_accel  #Adjust speed of rising helicopter 
            self.ids.helicopter_obj.center = self.helicopter_position() 
        else:
            self.helicopter_velocity -= self.heli_fall_accel  #Adjust speed of falling helicopter 
            self.ids.helicopter_obj.center = self.helicopter_position()                              
    
    #Runs on the clock schedule to update the game screen    
    def update_game(self, dt):
        self.helicopter_update() 
        self.scroll_background()                         
        
class helicopterApp(App):
    
    def build(self):
        game = Controller(size=Window.size)
        return game

if __name__ == '__main__':
    helicopterApp().run()
    
     
            
            
            
            