
from .engine import Engine
from pyglet import gl

class Game(object):
    def __init__(self):
        self.engine = Engine()

        self.engine.add_listener(self.process_events)
        self.engine.register_run(self.do_run)

    def process_events(self, event, data):
        if event == 'on_close':
            self.engine.stop()

    def update(self, dt):
        pass

    def render(self):
        self.engine.window.make_current()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)
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
