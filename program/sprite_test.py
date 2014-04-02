# This file is here to demonstrate a bug: image.blit() is working, but sprite.draw() seems to be broken.
# I have used sprite.draw() before, and this code worked on my other computer.  The differences are an
# upgrade from Python 3.3 to 3.4, and possibly some changes to pyglet(???).  Otherwise I'm stumped.




import dependencies.pyglet as pyglet

window = pyglet.window.Window()
robot = pyglet.image.load('robot.jpg')
sprite = pyglet.sprite.Sprite(robot,x=200,y=200)


@window.event
def on_draw():
    window.clear()
    robot.blit(100,100)
    sprite.draw()

pyglet.app.run()