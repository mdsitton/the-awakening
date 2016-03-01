from pyglet import window
import pyglet

class Engine(object):
    def __init__(self):
        self.title = "The Awakening"

        self.window = window.Window(800, 600, resizable=True,
                caption=self.title, fullscreen=False)

        self.listeners = []
        self.cursor_rel = False

        self.runFunc = lambda dt: None

        @self.window.event
        def on_resize(width, height):
            self.broadcast_event('resize', (width, height))

        @self.window.event
        def on_key_release(symbol, modifiers):
            self.broadcast_event('key_up', (symbol, modifiers))

        @self.window.event
        def on_key_press(symbol, modifiers):
            self.broadcast_event('key_down', (symbol, modifiers))

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            if self.is_cursor_relative():
                data = (dx, dy)
            else:
                data = (x, y)
            self.broadcast_event('mouse_move', data)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.broadcast_event('mouse_down', (button, modifiers))

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.broadcast_event('mouse_up', (button, modifiers))

        @self.window.event
        def on_mouse_scroll(x, y, dx, dy):
            self.broadcast_event('mouse_scroll', (x, y, dx, dy))

        @self.window.event
        def on_close():
            self.broadcast_event('on_close', None)

        @self.window.event
        def on_window_close(window):
            self.broadcast_event('window_close', window)

        class NewEventLoop(pyglet.app.EventLoop):
            def idle(inself):
                dt = inself.clock.update_time()
                redraw_all = inself.clock.call_scheduled_functions(dt)

                self.runFunc(dt)

                return 0

        self.eventLoop = NewEventLoop()

    def is_cursor_relative(self):
        return self.cursor_rel

    def relative_cursor(self, enabled):
        self.cursor_rel = enabled
        self.window.set_exclusive_mouse(exclusive=enabled)

    def add_listener(self, callback):
        self.listeners.append(callback)

    def remove_listener(self, callback):
        self.listeners.remove(callback)

    def broadcast_event(self, event, data):
        for listener in self.listeners:
            listener(event, data)

    def register_run(self, callback):
        self.runFunc = callback

    def run(self):
        self.eventLoop.run()

    def stop(self):
        self.eventLoop.exit()
