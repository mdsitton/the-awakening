
from .engine import Engine
import pyglet

from pyglet import gl

class Game(object):
    def __init__(self):
        self.engine = Engine()

        self.engine.add_listener(self.process_events)
        self.engine.register_run(self.do_run)
        playerImg = pyglet.image.load('data/player.png')
        self.player = pyglet.sprite.Sprite(playerImg)

        self.keys = []

    def process_events(self, event, data):
        if event == 'on_close':
            self.engine.stop()
        elif event == 'key_down':
            self.keys.append(data[0])
        elif event == 'key_up':
            self.keys.remove(data[0])

    def update(self, dt):
        if pyglet.window.key.W in self.keys:
            self.player.y += 50 * dt
        if pyglet.window.key.A in self.keys:
            self.player.x -= 50 * dt
        if pyglet.window.key.S in self.keys:
            self.player.y -= 50 * dt
        if pyglet.window.key.D in self.keys:
            self.player.x += 50 * dt
        print (self.keys)

    def render(self):
        self.engine.window.switch_to()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)
        self.player.draw()
        self.engine.window.flip()

    def do_run(self, dt):
        self.update(dt)
        self.render()
        print ('blah')

    def run(self):
        self.engine.run()


def main():
    game = Game()
    game.run()
