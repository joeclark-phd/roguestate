
import dependencies.pyglet as pyglet
import tiles


testwindow = pyglet.window.Window()


adventurer = pyglet.sprite.Sprite( tiles.tiles["adventurer"],x=testwindow.width//2,y=testwindow.height//2 )


@testwindow.event
def on_draw():
    testwindow.clear()
    adventurer.draw()

pyglet.app.run()

# TODO copy stuff from old game
