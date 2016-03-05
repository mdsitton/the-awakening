
from .engine import Engine
import pyglet

from pyglet import gl

from gem import vector

import ctypes as ct
import random
import math

class Rect(object):
    def __init__(self, minVec, maxVec):
        self.min = minVec
        self.max = maxVec

    def clone(self):
        return Rect(self.min.clone(), self.max.clone())

    def check_aabb(self, rect2):
        return (self.max.x >= rect2.min.x and
               rect2.max.x >= self.min.x and

               self.max.y >= rect2.min.y and
               rect2.max.y >= self.min.y)


class BoundingBoxMixin(object):
    def __init__(self):
        self.ctPoints = None
        self.ctPointT = (gl.GLfloat * 16)
        self.bbColor = (1.0, 1.0, 1.0)

    def set_bb_color(self, r, g, b):
        self.bbColor = (r, g, b)

    def render_bounding_box(self):
        gl.glLineWidth(1.0)

        self.ctPoints = self.ctPointT(
            self.rect.min.x, self.rect.min.y,
            self.rect.max.x, self.rect.min.y,

            self.rect.max.x, self.rect.min.y,
            self.rect.max.x, self.rect.max.y,

            self.rect.max.x, self.rect.max.y,
            self.rect.min.x, self.rect.max.y,

            self.rect.min.x, self.rect.max.y,
            self.rect.min.x, self.rect.min.y,
        )

        point_ptr = ct.cast(self.ctPoints, ct.c_void_p)

        gl.glColor3f(*self.bbColor)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, point_ptr)
        gl.glDrawArrays(gl.GL_LINES, 0, 8)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)


class SelectionBox(BoundingBoxMixin):
    def __init__(self):
        super(SelectionBox, self).__init__()
        self.rect = Rect(vector.Vector(2), vector.Vector(2))

    def set_start(self, vec):
        self.rect.min = vec.clone()

    def set_end(self, vec):
        self.rect.max = vec.clone()

    def get_selected(self, objects):
        selected = []

        rect = self.rect.clone()

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

        self.position = vector.Vector(2)

        self.rect = Rect(vector.Vector(2), vector.Vector(2))

        self.width = self.sprite.width
        self.height = self.sprite.height

        self.size = vector.Vector(2, data=[self.width, self.height])

        self.lenVelocity = vector.Vector(2, data=[random.random()*10, random.random()*10])
        self.mass = 1.0
        self.angVelocity = 0.0
        self.angle = 0.0
        self.momentOfInertia = (self.size.dot(self.size) * self.mass) / 12
        self.torqe = vector.Vector(2)

        self.set_bb_color(0.0, 0.0, 0.0)
        self.update_rect()

    def update_rect(self):
        self.rect.min = self.position
        self.rect.max.x = self.position.x + self.width
        self.rect.max.y = self.position.y + self.height

    def set_pos(self, vec):
        self.position = vec.clone()

    def update(self, dt):
        self.sprite.x = self.position.x
        self.sprite.y = self.position.y
        self.sprite.rotation = math.degrees(self.angle)
        self.update_rect()

    def render(self):
        self.sprite.draw()


class Particle(object):
    def __init__(self, x,y):
        pos = [x, y]
        self.position = vector.Vector(2, data=pos)
        self.velocity = vector.Vector(2, data=[random.random()*10, random.random()*10])
        self.mass = 1.0 + random.random()
        self.rect = Rect(self.position, self.position)


class Game(object):
    def __init__(self):
        self.engine = Engine()

        self.engine.add_listener(self.process_events)
        self.engine.register_run(self.do_run)
        self.units = []

        self.width = 0
        self.height = 0

        self.screenRect = Rect(vector.Vector(2), vector.Vector(2, data=[self.width, self.height]))

        self.selecting = False
        self.select = SelectionBox()
        self.selected = None
        self.unitsSelected = []

        self.mousePos = vector.Vector(2)
        self.currentClick = vector.Vector(2)
        self.mouseButtons = []

        self.points = []
        #for i in range(10):
        #    self.points.append(Particle(random.random()*self.width, self.height))
        self.ctPoints = None

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
        self.screenRect.max.x = width
        self.screenRect.max.y = height
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def update(self, dt):

        #if len(self.points) < 2000:
        #    for i in range(6):
        #        self.points.append(Particle(random.random()*self.width, self.height))

        if pyglet.window.key.E in self.keys:
            unit = Unit('data/player.png', 'unit')
            unit.set_pos(self.mousePos)
            self.units.append(unit)

        elif pyglet.window.key.Q in self.keys:
            for i in range(6):
                self.points.append(Particle(self.mousePos.x, self.mousePos.y))

        elif pyglet.window.key.M in self.keys:
            speedPerTick = 100.0 * dt
            for obj in self.unitsSelected:
                objMin = obj.position

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

        self.simulate_points(dt)
        self.simulate_bodies(dt)

    def simulate_points(self, dt):
        for point in self.points:
            if not self.screenRect.check_aabb(point.rect):
                self.points.remove(point)
                # point.__init__(random.random()*self.width, self.height)
            force = vector.Vector(2, data=[0, point.mass * -9.81])
            acceleration = force / point.mass
            point.velocity += acceleration * dt
            point.position += point.velocity * dt

    def simulate_bodies(self, dt):
        for unit in self.units:
            # calc force
            force = vector.Vector(2, data=[0,  unit.mass * -9.81])
            half = unit.size / 2
            unit.torque = half.x * force.y - half.y * force.x
            lenAcceleration = force / unit.mass
            unit.lenVelocity += lenAcceleration * dt
            unit.position += unit.lenVelocity * dt

            angAcceleration = unit.torque / unit.momentOfInertia
            unit.angVelocity += angAcceleration * dt
            unit.angle += unit.angVelocity * dt


    def render_points(self):
        renderPoints = []
        for point in self.points:
            renderPoints.extend(point.position.vector)

        self.ctPoints = (gl.GLfloat * len(renderPoints))(*renderPoints)

        point_ptr = ct.cast(self.ctPoints, ct.c_void_p)

        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, point_ptr)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(renderPoints)//2)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def render(self):
        self.engine.window.switch_to()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)

        self.render_points()

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
