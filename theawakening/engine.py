from pyglet import window
import pyglet

class SysEvents(object):
    def __init__(self, engine):
        self.engine = engine
        self.window = self.engine.window.window
        self.eventLoop = pyglet.app.EventLoop()
        self.runFunc = lambda dt: None

        @self.window.event
        def on_resize(width, height):
            self.engine.broadcast_event('resize', (width, height))

        @self.window.event
        def on_key_release(symbol, modifiers):
            self.engine.broadcast_event('key_up', (symbol, modifiers))

        @self.window.event
        def on_key_press(symbol, modifiers):
            self.engine.broadcast_event('key_down', (symbol, modifiers))

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            if self.engine.cursor.is_relative():
                data = (dx, dy)
            else:
                data = (x, y)
            self.engine.broadcast_event('mouse_move', data)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.engine.broadcast_event('mouse_down', (button, modifiers))

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.engine.broadcast_event('mouse_up', (button, modifiers))

        @self.window.event
        def on_mouse_scroll(x, y, dx, dy):
            self.engine.broadcast_event('mouse_scroll', (x, y, dx, dy))

        @self.window.event
        def on_close():
            self.engine.broadcast_event('on_close', None)

        @self.window.event
        def on_window_close(window):
            self.engine.broadcast_event('window_close', window)

        class NewEventLoop(pyglet.app.EventLoop):
            def idle(inself):
                dt = inself.clock.update_time()
                redraw_all = inself.clock.call_scheduled_functions(dt)

                self.runFunc(dt)

                # Update timout
                return inself.clock.get_sleep_time(True)

    def set_run(self, function):
        self.runFunc = function

    def run(self):
        self.eventLoop.run()

    def stop(self):
        self.eventLoop.exit()

class Window(object):
    def __init__(self, title, width, height, fullscreen):
        self.title = title
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.window = window.Window(width, height, resizable=True, caption=title, fullscreen=fullscreen)

    def make_current(self):
        self.window.switch_to()

    def set_fullscreen(self, enabled):
        self.window.set_fullscreen(fullscreen=enabled)

    def set_vsync(self, enabled):
        self.window.set_vsync(enabled)

    def set_title(self, title):
        self.window.set_caption(title)

    def flip(self):
        self.window.flip()

class Cursor(object):
    def __init__(self, engine):
        self.engine = engine
        self.window = engine.window.window
        self.rel_mode = False

    def is_relative(self):
        return self.rel_mode

    def set_relative(self, enabled):
        self.rel_mode = enabled
        self.window.set_exclusive_mouse(exclusive=enabled)

class Engine(object):
    def __init__(self):
        self.window = Window("The Awakening", 800, 600, False)
        self.cursor = Cursor(self)
        self.events = SysEvents(self)
        self.listeners = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    def remove_listener(self, callback):
        self.listeners.remove(callback)

    def broadcast_event(self, event, data):
        for listener in self.listeners:
            listener(event, data)

    def register_run(self, callback):
        self.events.set_run(callback)

    def run(self):
        self.events.run()

    def stop(self):
        self.events.stop()
