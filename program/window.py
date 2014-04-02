import preferences # this first import will load the user's preferences from prefs.txt
import tiles # this is the first import of tiles.py so it will take some time initializing graphics
import widgets
import pyglet
from pyglet.window import key





class GameWindow( pyglet.window.Window ):
    """
    Extends the pyglet.window.Window, which opens a window and captures keypresses.
    Multiple displays or views or game states will be represented by "GameMode" objects, each
    with its set of sprites and its logic for handling keypress events.  These will be "layered"
    so that, for example, a dialog box or menu can pop up on top of the map without erasing it.
    The custom functions below essentially enable a "stack" that captures keypresses from the
    top down, and draws sprites from the bottom up.
    """

    def __init__( self, **kargs ):
        self._modes = [] # this variable will hold the "stack" of game input/output modes
        pyglet.window.Window.__init__( self, **kargs )

    def change_bottom_mode( self, gamemode ):
        """
        Destroy the current game mode and replace it.
        If you want to leave the current mode alive as an
        underlying/hidden mode ready to return to service,
        use push_mode() instead.
        Note: this clears all "overlay" modes at the same time.
        There is no way with this code to change the bottom
        mode without closing all the overlays.
        """
        self._modes = [ gamemode ]

    def push_mode( self, gamemode ):
        """
        Add an input/output mode on top of the main mode,
        for example, a dialog box or information display.
        This will leave the bottom mode (i.e. the game map)
        visible, and possibly some event handlers active,
        rather than destroying it.
        """
        self._modes.append( gamemode )

    def pop_mode( self ):
        """
        Remove the top input/output mode and its event handlers.
        Returns control to the lower mode(s) in the stack.
        """
        self._modes.pop()

    def on_key_press( self, symbol, modifiers ):
        """
        Calls the event handler for each game mode in the stack from top to bottom;
        stops when a handler returns True or it runs out of stack.
        """
        for m in self._modes[::-1]:
            if m.on_key_press( symbol, modifiers ): break # call each game mode's event handler from top to bottom

    def on_resize( self, width, height ):
        for m in self._modes[::-1]:
            if m.on_resize( width, height ): break
        super(GameWindow,self).on_resize(width,height)

    def on_draw( self ):
        """
        Other event handlers will go from the "top" mode to the bottom;
        but drawing must be done bottom-up, and window.clear() must only
        be called once; so we call them like so:
        """
        self.clear()
        for m in self._modes:
            m.on_draw()

#end GameWindow class






# GAME MODES: Each of these extends the GameMode class and represents a display routine (the draw() method)
# and some input-output handlers.  GameModes may be stacked (e.g. a menu or dialog can "pop up" over the
# regular game map/display) or they may be replaced (e.g. when player goes to an info screen).

class GameMode():
    """
    GAME MODES: Each of these extends the GameMode class and represents a display routine (the draw() method)
    and some input-output handlers.  GameModes may be stacked (e.g. a menu or dialog can "pop up" over the
    regular game map/display) or they may be replaced (e.g. when player goes to an info screen).
    """
    def __init__(self, window, game):
        self._batch = pyglet.graphics.Batch()
        self._window = window
        self._game = game
    def on_draw(self):
        self._batch.draw()
    def on_key_press(self, symbol, modifiers):
        pass
    def on_resize(self, width, height):
        pass

class SplashScreen(GameMode):
    # will display splash screen and proceed to menu on any key press
    def __init__(self, *args):
        GameMode.__init__(self, *args)
        self._splashtiles = tiles.generate_sprite_string("welcome to Rogue State University",20,200,self._batch,alphabet=1)
    def on_key_press(self,symbol,modifiers):
        self._window.change_bottom_mode(MainMenu(self._window,self._game))


class MainMenu(GameMode):
    # will display main menu
    def __init__(self, *args):
        GameMode.__init__(self, *args)
        self._menu = widgets.GraphicalMenu("new game","highscores","quit",xcenter=gwindow.width//2,ycenter=gwindow.height//2)
    def on_key_press(self,symbol,modifiers):
        if symbol in { key.UP, key.NUM_8 }:
            self._menu.option_up()
            return True
        if symbol in { key.DOWN, key.NUM_2 }:
            self._menu.option_down()
            return True
        if symbol == key.ENTER:
            if self._menu.selection == 0:
                print("starting new game.")
                self._window.change_bottom_mode(MapInterface(self._window,self._game))
            if self._menu.selection == 1:
                print("viewing high scores.")
            if self._menu.selection == 2:
                print("exiting game.")
                pyglet.app.exit()
            return True
    def on_draw(self):
        self._menu.draw()


class MapInterface(GameMode):
    # will display main game interface
    def __init__(self, *args):
        GameMode.__init__(self, *args)
        self._adventurer = pyglet.sprite.Sprite( tiles.tiles["adventurer"],x=gwindow.width//2,y=gwindow.height//2 )

    def on_key_press(self,symbol,modifiers):
        if symbol == key.ESCAPE:
            print("showing ESC menu.")
            self._window.push_mode(ESCMenu(self._window,self._game))
        if symbol == key.TAB:
            print("showing look cursor.")
        # catch directional controls
        if symbol in direction_keys:
            v,h = direction_keys[symbol] # the sign (or zero) of vertical/horizontal movement
            multiplier = 3 # the default scroll speed
            if modifiers & key.MOD_SHIFT: multiplier = 10
            if modifiers & key.MOD_CTRL: multiplier = 1
            print('moving by %sX, %sY' % (h*multiplier, v*multiplier))
        return True
    def on_resize(self,width,height):
        print('Window resized to %s x %s' % (width, height))
    def on_draw(self):
        self._adventurer.draw()

class ESCMenu(GameMode):
    # will display ESC menu
    def __init__(self, *args):
        GameMode.__init__(self, *args)
        self._menu = widgets.GraphicalMenu("never mind","quit",xcenter=gwindow.width//2,ycenter=gwindow.height//2)
    def on_key_press(self,symbol,modifiers):
        if symbol == key.ESCAPE:
            print("closing ESC menu.")
            self._window.pop_mode()
            return True
        if symbol in { key.UP, key.NUM_8 }:
            self._menu.option_up()
            return True
        if symbol in { key.DOWN, key.NUM_2 }:
            self._menu.option_down()
            return True
        if symbol == key.ENTER:
            if self._menu.selection == 0:
                print("closing ESC menu.")
                self._window.pop_mode()
            if self._menu.selection == 1:
                print("exiting game.")
                pyglet.app.exit()
            return True
        return True # this mode should intercept ALL key presses
    def on_draw(self):
        self._menu.draw()






# FOR CONVENIENCE
# a dictionary of direction keys and their correspondent vertical/horizontal components
direction_keys = { key.RIGHT:(0,1), key.NUM_6:(0,1), key.PAGEUP:(1,1), key.NUM_9:(1,1), key.UP:(1,0),
                   key.NUM_8:(1,0), key.HOME:(1,-1), key.NUM_7:(1,-1), key.LEFT:(0,-1), key.NUM_4:(0,-1),
                   key.END:(-1,-1), key.NUM_1:(-1,-1),key.DOWN:(-1,0), key.NUM_2:(-1,0), key.PAGEDOWN:(-1,1),
                   key.NUM_3:(-1,1) }








# INITIALIZE THE PROGRAM

dims = (70 * tiles.tilewidth, 35 * tiles.tileheight)
gdata = "placeholder"  # the GameData object will be attached here
gwindow = GameWindow( width=dims[0], height=dims[1], resizable=True )  # open the window
gwindow.change_bottom_mode( SplashScreen(gwindow,gdata) )  # launch the splash screen

pyglet.app.run()
