__author__ = 'jwclark2'

import pyglet


testwindow = pyglet.window.Window()

label = pyglet.text.Label('@',x=testwindow.width//2,y=testwindow.height//2)

@testwindow.event
def on_draw():
    testwindow.clear()
    label.draw()

pyglet.app.run()

