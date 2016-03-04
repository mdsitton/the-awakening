
from .engine import Engine
import pyglet

from pyglet import gl

from gem import vector

import ctypes as ct
import math

# This is to make up for some missing functionality from GEM and fix some bugs
class Vector(vector.Vector):

    def clone(self):
        return Vector(self.size, data=self.vector[:]) # fix slight bug since vector contents are not copied

    def distance(self, other):
        return self.magnitude(self - other)

    def __eq__(self, vecB):
        if isinstance(vecB, Vector):
            for i in range(self.size):
                if self.vector[i] != vecB.vector[i]:
                    return False
            else:
                return True
        else:
            return NotImplemented

    def __ne__(self, vecB):
        if isinstance(vecB, Vector):
            for i in range(self.size):
                if self.vector[i] != vecB.vector[i]:
                    return True
            else:
                return False
        else:
            return NotImplemented

    @property
    def x(self):
        return self.vector[0]

    @x.setter
    def x(self, val):
        self.vector[0] = val

    @property
    def y(self):
        return self.vector[1]

    @y.setter
    def y(self, val):
        self.vector[1] = val

    @property
    def z(self):
        return self.vector[2]

    @z.setter
    def z(self, val):
        self.vector[2] = val

    @property
    def w(self):
        return self.vector[3]

    @w.setter
    def w(self, val):
        self.vector[3] = val

# monkey patch it
vector.Vector = Vector

class Rect(object):
    def __init__(self, minVec, maxVec):
        self.min = minVec
        self.max = maxVec

    def check_aabb(self, rect2):
        return (self.max.x >= rect2.min.x and
               rect2.max.x >= self.min.x and

               self.max.y >= rect2.min.y and
               rect2.max.y >= self.min.y)


class BoundingBoxMixin(object):
    def __init__(self):
        self.ctPoints = None
        self.bbColor = (1.0, 1.0, 1.0)

    def set_bb_color(self, r, g, b):
        self.bbColor = (r, g, b)

    def render_bounding_box(self):
        gl.glLineWidth(1.0)

        points = [
            self.rect.min.x, self.rect.min.y,
            self.rect.max.x, self.rect.min.y,

            self.rect.max.x, self.rect.min.y,
            self.rect.max.x, self.rect.max.y,

            self.rect.max.x, self.rect.max.y,
            self.rect.min.x, self.rect.max.y,

            self.rect.min.x, self.rect.max.y,
            self.rect.min.x, self.rect.min.y,
        ]


        self.ctPoints = (gl.GLfloat * len(points))(*points)
        point_ptr = ct.cast(self.ctPoints, ct.c_void_p)

        gl.glColor3f(*self.bbColor)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, point_ptr)
        gl.glDrawArrays(gl.GL_LINES, 0, len(points)//2)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)


class SelectionBox(BoundingBoxMixin):
    def __init__(self):
        super(SelectionBox, self).__init__()
        self.rect = Rect(Vector(2), Vector(2))

    def set_start(self, vec):
        self.rect.min = vec.clone()

    def set_end(self, vec):
        self.rect.max = vec.clone()

    def get_selected(self, objects):
        selected = []

        rect = Rect(self.rect.min.clone(), self.rect.max.clone())

        if self.rect.min.x > self.rect.max.x:
            rect.min.x = self.rect.max.x
            rect.max.x = self.rect.min.x

        if self.rect.min.y > self.rect.max.y:
            rect.min.y = self.rect.max.y
            rect.max.y = self.rect.min.y

        for obj in objects:
            rec = obj.rect
            if rect.check_aabb(rec):
                selected.append(obj)

        return selected

    def render(self):
        self.render_bounding_box()

class Unit(BoundingBoxMixin):
    def __init__(self, imgPath, name):
        super(Unit, self).__init__()
        img = pyglet.image.load('data/player.png')
        self.sprite = pyglet.sprite.Sprite(img)
        self.pos = Vector(2)
        self.rect = Rect(Vector(2), Vector(2))
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.set_bb_color(0.0, 0.0, 0.0)
        self.update_rect()

    def update_rect(self):
        self.rect.min = self.pos
        self.rect.max.x = self.pos.x + self.width
        self.rect.max.y = self.pos.y + self.height

    def set_pos(self, vec):
        self.pos = vec.clone()

        self.update_rect()

    def update(self, dt):
        self.sprite.x = self.pos.x
        self.sprite.y = self.pos.y


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
        self.selected = None
        self.unitsSelected = []

        self.mousePos = Vector(2)
        self.currentClick = Vector(2)
        self.mouseButtons = []

        self.keys = []

    def process_events(self, event, data):
        if event == 'mouse_move':
            x, y = data
            self.mousePos.x = x
            self.mousePos.y = y

        elif event == 'mouse_down':
            button, modifiers = data
            self.mouseButtons.append(button)
            self.currentClick = self.mousePos.clone()
        elif event == 'mouse_up':
            button, modifiers = data
            self.mouseButtons.remove(button)
            if self.currentClick.x == self.mousePos.x and self.currentClick.y == self.mousePos.y:
                self.unitsSelected = []
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
            unit.set_pos(self.mousePos)
            self.units.append(unit)
        elif pyglet.window.key.M in self.keys:
            speedPerTick = 100.0 * dt
            for obj in self.unitsSelected:
                objMin = obj.pos

                delta = self.mousePos - objMin

                distance = delta.magnitude()

                if distance > speedPerTick:
                    ratio = speedPerTick / distance
                    move = delta * ratio
                    final = objMin + move

                else:
                    final = self.mousePos

                obj.set_pos(final)
        elif pyglet.window.key.DELETE in self.keys:
            for obj in self.unitsSelected:
                self.units.remove(obj)
            self.unitsSelected = []

        if 1 in self.mouseButtons:
            if not self.selecting:
                if self.currentClick != self.mousePos:
                    self.selecting = True
                    self.select.set_start(self.mousePos)
        else:
            if self.selecting:
                self.selecting = False

        if self.selecting:
            self.select.set_end(self.mousePos)
            self.unitsSelected = self.select.get_selected(self.units)

        for unit in self.units:
            unit.update(dt)

    def render(self):
        self.engine.window.switch_to()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)

        for unit in self.units:
            if unit in self.unitsSelected:
                unit.render_bounding_box()
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
