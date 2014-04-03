import preferences # this first import will load the user's preferences from prefs.txt
import tiles # this is the first import of tiles.py so it will take some time initializing graphics
import widgets, viewport, worldgen
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
                newgamedata = worldgen.gen_world()
                self._window.change_bottom_mode(MapInterface(self._window,newgamedata))
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
        self._sidebar_width = 20 # how wide is the sidebar of messages/options on the right
        self._sidebar_on = True # display the sidebar or hide it?
        self._bottombar_on = False
        self._lay_out(gwindow.width,gwindow.height)
        self._view = viewport.Viewport(self._game.level(),x_margin=self._renderbox_corner[0],y_margin=self._renderbox_corner[1],visible_rows=self._renderbox_dims[1],visible_cols=self._renderbox_dims[0],corner_col=20,corner_row=20)
        self._title = tiles.generate_sprite_string("this is the normal game map",self._messagebar_corner[0],self._messagebar_corner[1],self._batch,alphabet=1)
        #self._adventurer = pyglet.sprite.Sprite( tiles.tiles["adventurer"],x=gwindow.width//2,y=gwindow.height//2 )
    def _lay_out(self,width,height):
        #figure out where everything goes
        maxcols = width//tiles.tilewidth
        maxrows = height//tiles.tileheight
        xmargin = (width-(maxcols*tiles.tilewidth)) // 2  # half of the fractional tilewidth remainder is the margin on the left
        ymargin = (height-(maxrows*tiles.tileheight)) // 2  # the margin on the bottom
        # PARTS OF THE SCREEN:
        #   leftborder: a 1 tile wide strip of border tiles on the left
        #   rightborder: a 1 tile wide strip of border tiles on the left
        #   topborder: a 1 tile high strip of border tiles on top
        #   bottomborder: a 1 tile high strip of border tiles on bottom
        #   messagebar: a 1 tile high bar above the bottomborder that will display messages
        #   bottom2border: a 1 tile high strip of border tiles above the messagebar and below the following:
        #       renderbox: the viewport within which the map will be rendered; abuts the leftborder, bottomborder, and topborder.
        #       right2border: an optional vertical strip of border tiles between the renderbox and the sidebar
        #       sidebar: an optional [20] tile wide box for options/information/etc to the right of right2border and left of rightborder
        self._leftborder_corner = (xmargin,ymargin)
        self._leftborder_dims = (1,maxrows)
        self._rightborder_corner = ( xmargin+((maxcols-1)*tiles.tilewidth) , ymargin )
        self._rightborder_dims = (1,maxrows)
        self._bottomborder_corner = (xmargin,ymargin)
        self._bottomborder_dims = (maxcols,1)
        self._topborder_corner = ( xmargin , ymargin+((maxrows-1)*tiles.tileheight) )
        self._topborder_dims = (maxcols,1)
        self._messagebar_corner = ( (xmargin+tiles.tilewidth) , (ymargin+tiles.tileheight) )
        self._messagebar_dims = (maxcols-2,1)
        self._bottom2border_corner = ( xmargin , ymargin+(2*tiles.tileheight) )
        self._bottom2border_dims = (maxcols,1)
        self._renderbox_corner = ( (xmargin+tiles.tilewidth) , (ymargin+(3*tiles.tileheight)) )
        if self._sidebar_on:
            self._renderbox_dims = ( maxcols-3-self._sidebar_width, maxrows-4 )
            self._right2border_corner = ( (xmargin+((maxcols-2-self._sidebar_width)*tiles.tilewidth)), (ymargin+(3*tiles.tileheight)) )
            self._right2border_dims = ( 1, maxrows-4 )
            self._sidebar_corner = ( (xmargin+((maxcols-1-self._sidebar_width)*tiles.tilewidth)), (ymargin+(3*tiles.tileheight)) )
            self._sidebar_dims = ( self._sidebar_width, maxrows-4 )
        else:
            self._renderbox_dims = ( maxcols-2, maxrows-4 )
            #no right2border
            #no sidebar
    def on_key_press(self,symbol,modifiers):
        if symbol == key.ESCAPE:
            print("showing ESC menu.")
            self._window.push_mode(ESCMenu(self._window,self._game))
        if symbol == key.TAB:
            print("showing look cursor.")
            self._window.push_mode(LookCursor(self._view,self._window,self._game))
        if symbol == key.I:  # (i)nfo-panel
            print("showing/hiding sidebar.")
            self._sidebar_on = 1 - self._sidebar_on  # toggle True/False value
            self._lay_out(self._window.width,self._window.height)
            self._view.resize_view(new_rows=self._renderbox_dims[1],new_cols=self._renderbox_dims[0],x_margin=self._renderbox_corner[0],y_margin=self._renderbox_corner[1])
        if symbol in direction_keys:
            v,h = direction_keys[symbol] # the sign (or zero) of vertical/horizontal movement
            multiplier = 3 # the default scroll speed
            if modifiers & key.MOD_SHIFT: multiplier = 10
            if modifiers & key.MOD_CTRL: multiplier = 1
            self._view.move_view(v*multiplier,h*multiplier)
        return True
    def on_resize(self,width,height):
        self._lay_out(self._window.width,self._window.height)
        self._view.resize_view(new_rows=self._renderbox_dims[1],new_cols=self._renderbox_dims[0],x_margin=self._renderbox_corner[0],y_margin=self._renderbox_corner[1])
        # TODO move sidebar
        # TODO move messagebar
    def on_draw(self):
        self._view.render()
        self._view.draw()
        #self._adventurer.draw()

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

class LookCursor(GameMode):
    # take over the directional controls to move a cursor around the screen
    # display what is "seen" in the bottom bar
    def __init__(self, view, *args):
        GameMode.__init__(self, *args)
        self._view = view
        self._view.init_cursor()  # make a cursor visible at the default position
        self._game.look(self._view.cursor_tilenum())
    def on_key_press(self, symbol, modifiers):
        if symbol == key.TAB:
            print("closing look mode.")
            self._view.destroy_cursor()
            self._window.pop_mode()
            return True
        if symbol in direction_keys:
            v,h = direction_keys[symbol] # the sign (or zero) of vertical/horizontal movement
            multiplier = 1 # the default scroll speed
            if modifiers & key.MOD_SHIFT: multiplier = 10
            self._view.move_cursor(v*multiplier,h*multiplier)
            self._game.look(self._view.cursor_tilenum())
            return True # do not let direction keys cascade to the underlying mode
        # no general "return True" so this mode only intercepts the specified key presses. other key presses will go to the underlying mode.





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
