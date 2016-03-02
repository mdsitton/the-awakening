
from .engine import Engine
import pyglet

from pyglet import gl

import ctypes as ct

class SelectionBox(object):
    def __init__(self):
        self.startX = 0
        self.startY = 0

        self.endX = 0
        self.endY = 0

        self.ctPoints = None

    def set_start(self, x, y):
        self.endX = self.startX = float(x)
        self.endX = self.startY = float(y)

    def set_end(self, x, y):
        self.endX = float(x)
        self.endY = float(y)
    
    def get_selected(self, objects):
        selected = []
        
        if self.startX > self.endX:
            x1 = self.endX
            x2 = self.startX
        else:
            x2 = self.endX
            x1 = self.startX

        if self.startY > self.endY:
            y1 = self.endY
            y2 = self.startY
        else:
            y2 = self.endY
            y1 = self.startY
        
        for obj in objects:
            rec = obj.rect
            if rec.x1 >= x1 and rec.x2 <= x2 and rec.y1 >= y1 and rec.y2 <= y2:
                selected.append(obj)
        
        return selected

    def render(self):
        gl.glLineWidth(1.0)

        points = [
            self.startX, self.startY,
            self.endX, self.startY,

            self.endX, self.startY,
            self.endX, self.endY,

            self.endX, self.endY,
            self.startX, self.endY,

            self.startX, self.endY,
            self.startX, self.startY,
        ]


        self.ctPoints = (gl.GLfloat * len(points))(*points)
        point_ptr = ct.cast(self.ctPoints, ct.c_void_p)

        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, point_ptr)
        gl.glDrawArrays(gl.GL_LINES, 0, len(points)//2)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

class Rect(object):
    def __init__(self, x1,y1,x2,y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class Unit(object):
    def __init__(self, imgPath, name):
        img = pyglet.image.load('data/player.png')
        self.sprite = pyglet.sprite.Sprite(img)
        self.posX = 0
        self.posY = 0
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.update_rect()
       
    def update_rect(self): 
        self.rect = Rect(self.posX, self.posY, self.posX + self.width, self.posY + self.height)
    
    def set_pos(self, x, y):
        self.posX = x
        self.posY = y
        self.sprite.x = x
        self.sprite.y = y
        
        self.update_rect()
    
    def render(self):
        self.sprite.draw()

class Game(object):
    def __init__(self):
        self.engine = Engine()

        self.engine.add_listener(self.process_events)
        self.engine.register_run(self.do_run)
        self.units = []

        self.selecting = False
        self.select = SelectionBox()
        self.select.set_start(0,0)
        self.selected = None

        self.mouseX = 0
        self.mouseY = 0
        self.mouseButtons = []

        self.keys = []

    def process_events(self, event, data):
        if event == 'mouse_move':
            if self.engine.is_cursor_relative():
                self.mouseRelX = data[0]
                self.mouseRelY = data[1]
            else:
                self.mouseX = data[0]
                self.mouseY = data[1]

        elif event == 'mouse_down':
            button, modifiers = data
            self.mouseButtons.append(button)
        elif event == 'mouse_up':
            button, modifiers = data
            self.mouseButtons.remove(button)
        elif event == 'key_down':
            self.keys.append(data[0])
        elif event == 'key_up':
            self.keys.remove(data[0])
        elif event == 'resize':
            width, height = data
            self.resize(width, height)
        elif event == 'on_close':
            self.engine.stop()

    def resize(self, width, height):
        self.width = width
        self.height = height
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def update(self, dt):
        if pyglet.window.key.E in self.keys:
            unit = Unit('data/player.png', 'unit')
            unit.set_pos(self.mouseX, self.mouseY)
            self.units.append(unit)

        if 1 in self.mouseButtons:
            if not self.selecting:
                self.selecting = True
                self.select.set_start(self.mouseX, self.mouseY)
        else:
            if self.selecting:
                self.selecting = False

        if self.selecting:
            self.select.set_end(self.mouseX, self.mouseY)

    def render(self):
        self.engine.window.switch_to()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)
        
        
        if not self.selecting:
            units = self.units
        else:
            units = self.select.get_selected(self.units)
        
        for unit in units:
            unit.render()
        
        if self.selecting:
            self.select.render()
        self.engine.window.flip()

    def do_run(self, dt):
        self.update(dt)
        self.render()

    def run(self):
        self.engine.run()


def main():
    game = Game()
    game.run()
