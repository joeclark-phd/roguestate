
import pyglet


testwindow = pyglet.window.Window()

label = pyglet.text.Label('@',x=testwindow.width//2,y=testwindow.height//2)

@testwindow.event
def on_draw():
    testwindow.clear()
    label.draw()

pyglet.app.run()

# TODO copy stuff from old game
