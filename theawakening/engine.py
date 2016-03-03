from pyglet import window
import pyglet

class Engine(object):
    def __init__(self):
        self.title = "The Awakening"

        self.listeners = []
        self.cursor_rel = False

        self.runFunc = lambda dt: None

        # These classes need to access variables contained within Engine
        # Without really changing how they function to much. Defining them
        # in the init of Engine is the simplest way to do this.
        class MyWindow(window.Window):
            def on_resize(wself, width, height):
                self.broadcast_event('resize', (width, height))

            def on_key_release(wself, symbol, modifiers):
                self.broadcast_event('key_up', (symbol, modifiers))

            def on_key_press(wself, symbol, modifiers):
                self.broadcast_event('key_down', (symbol, modifiers))

            def on_mouse_motion(wself, x, y, dx, dy):
                if self.is_cursor_relative():
                    data = (dx, dy)
                else:
                    data = (x, y)
                self.broadcast_event('mouse_move', data)

            def on_mouse_drag(wself, x, y, dx, dy, buttons, modifiers):
                if self.is_cursor_relative():
                    data = (dx, dy)
                else:
                    data = (x, y)
                self.broadcast_event('mouse_move', data)

            def on_mouse_press(wself, x, y, button, modifiers):

                self.broadcast_event('mouse_move', (x, y))
                self.broadcast_event('mouse_down', (button, modifiers))

            def on_mouse_release(wself, x, y, button, modifiers):
                self.broadcast_event('mouse_up', (button, modifiers))

            def on_mouse_scroll(wself, x, y, dx, dy):
                self.broadcast_event('mouse_scroll', (x, y, dx, dy))

            def on_close(wself):
                self.broadcast_event('on_close', None)

            def on_window_close(wself, window):
                self.broadcast_event('window_close', window)

        class NewEventLoop(pyglet.app.EventLoop):
            def idle(inself):
                dt = inself.clock.update_time()
                redraw_all = inself.clock.call_scheduled_functions(dt)

                self.runFunc(dt)

                return 0

        self.window = MyWindow(1280, 720, resizable=True,
                caption=self.title, fullscreen=False)
        self.window.set_vsync(False)

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
