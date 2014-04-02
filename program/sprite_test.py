import pyglet
from pyglet.image.codecs.png import PNGImageDecoder

window = pyglet.window.Window()
robot = pyglet.image.load('robot.jpg')
sprite = pyglet.sprite.Sprite(robot,x=200,y=200)


@window.event
def on_draw():
    window.clear()
    robot.blit(100,100)
    sprite.draw()

pyglet.app.run()