#TODO
#Acceleration
#Endend (when the top/bottom is hit)
#Background scrolling

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty, \
	ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.vector import Vector

class Helicopter(Widget):
    up = NumericProperty(90)
    down = NumericProperty (270)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    touched_down = BooleanProperty(False)

    def move(self):
    	if self.touched_down:
    		self.velocity = Vector(4,0).rotate(self.up)
        	self.pos = Vector(*self.velocity) + self.pos
        else:
   			self.velocity = Vector(4,0).rotate(self.down)
   			self.pos = Vector(*self.velocity) + self.pos

class HelicopterGame(Widget):
    helicopter = ObjectProperty(None)

    def start(self):
        self.helicopter.center = self.center
        self.helicopter.velocity = Vector(4, 0).rotate(270)

    def update(self, dt):
        #stop if hit top and bottom
        if (self.helicopter.y < 0) or (self.helicopter.top > self.height):
            self.end()
        else:
        	self.helicopter.move()

    def on_touch_down(self, touch):
        self.helicopter.touched_down = True

    def on_touch_up(self, touch):
        self.helicopter.touched_down = False 

    def end(self):
    	print "You lose!"


class HelicopterApp(App):
    def build(self):
    	game = HelicopterGame()
    	game.start()
    	Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    HelicopterApp().run()