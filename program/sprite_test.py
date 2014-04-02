# This file WAS here to demonstrate a bug: image.blit() is working, but sprite.draw() seems to be broken.
# I have used sprite.draw() before, and this code worked on my other computer.
# The difference, as it turned out, was my AMD video card.  A tweak to pyglet/sprite.py fixed it.
# I'm leaving this code here for now, to make sure I haven't broken the game for others!


import pyglet

window = pyglet.window.Window()
robot = pyglet.image.load('robot.jpg')
sprite = pyglet.sprite.Sprite(robot,x=400,y=200)


@window.event
def on_draw():
    window.clear()
    robot.blit(100,100)  # you should see one robot on the left
    sprite.draw()  # and another robot on the right

pyglet.app.run()