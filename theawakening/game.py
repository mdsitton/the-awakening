
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

class Game(object):
    def __init__(self):
        self.engine = Engine()

        self.engine.add_listener(self.process_events)
        self.engine.register_run(self.do_run)
        playerImg = pyglet.image.load('data/player.png')
        self.player = pyglet.sprite.Sprite(playerImg)

        self.selecting = False
        self.select = SelectionBox()
        self.select.set_start(0,0)

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
        if pyglet.window.key.W in self.keys:
            self.player.y += 50 * dt
        if pyglet.window.key.A in self.keys:
            self.player.x -= 50 * dt
        if pyglet.window.key.S in self.keys:
            self.player.y -= 50 * dt
        if pyglet.window.key.D in self.keys:
            self.player.x += 50 * dt

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
        self.player.draw()
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
