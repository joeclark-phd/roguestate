"renders the GameData as Sprite objects"
import pyglet
import geometry, gamedata, tiles

# The best way to keep this decoupled from the GameData but still speedy was
# to have the Level (i.e. map) objects maintain sets of tile numbers that need 
# updating: terrain_changes, thing_changes, and critter_changes. The Viewport
# pop()s the tile numbers from those collections and updates only those tiles
# that need updating.  Call the Level's .refresh() method to flag all tiles as
# having changed, if you want to re-render all sprites from scratch: for example,
# if you have plugged in a new tileset.





class Viewport:
    """
    A "map" of game tile images in layers (terrain, thing, critter, effect, blueprint, cursor).
    Keeps track of which tiles should be visible (although it does not itself obscure the invisible tiles).
    Has routines to change the view within the visible viewport (i.e. by scrolling the entire map).
    Can display cursors on top of the game and tell you where they are located.
    """

    def __init__(self,level,x_margin=0,y_margin=0,corner_row=0,corner_col=0,visible_rows=0,visible_cols=0):

        self._level = level  # the "level" is a map in the GameData object containing geometry, terrain, items and creatures
        self._level.refresh()  # 

        # do some basic error checking on the parameters as we store them
        self._visible_rows = visible_rows or self._level.geometry().rows()  # if visible_rows is zero, assume the whole map is visible
        self._visible_cols = visible_cols or self._level.geometry().cols()
        self._visible_rows = min( visible_rows, self._level.geometry().rows() )  # more rows cannot be visible than exist
        self._visible_cols = min( visible_cols, self._level.geometry().cols() )
        self._corner_row = min( corner_row, self._level.geometry().rows() - self._visible_rows )  # the corner must be at least self._visible_rows below the top of the actual map
        self._corner_col = min( corner_col, self._level.geometry().cols() - self._visible_cols )  # and self._visible_cols to the left of the map's right edge
        
        # MARGINS: where the whole viewport is positioned
        self._x_margin = x_margin
        self._y_margin = y_margin
        # OFFSETS: how much the viewport is jiggered to put the corner tile in the corner
        self._x_offset = (-1)*(self._corner_col*tiles.tilewidth)
        self._y_offset = (-1)*(self._corner_row*tiles.tileheight)
        
        # DATA STRUCTURES
        # batch and orderedgroups to enable efficient drawing
        self._batch = pyglet.graphics.Batch()
        self._terrain_group = pyglet.graphics.OrderedGroup(0)
        self._thing_group = pyglet.graphics.OrderedGroup(1)
        self._critter_group = pyglet.graphics.OrderedGroup(2)
        self._cursor_group = pyglet.graphics.OrderedGroup(5)
        # arrays to hold the sprites -- there's a maximum of one sprite per tile per layer
        self._terraintiles = [None]*self._level.geometry().tilecount()
        self._thingtiles = [None]*self._level.geometry().tilecount()
        self._crittertiles = [None]*self._level.geometry().tilecount()

        #the tiles that SHOULD be visible are the only ones we care about
        self._visible_set = self._level.geometry().viewport( self._corner_row, self._corner_col, self._visible_rows, self._visible_cols )

        #initialize cursor
        self._cursor = None
        
    def draw(self):
        self._batch.draw()
     
    def render(self,tilerange=None):
        if tilerange==None: tilerange = self._visible_set # by default, render only the visible tiles
        "create or delete sprites in those tiles where there have been changes since the last render()"

        terrains_todo = tilerange & self._level.terrain_changes # the intersection of "visible in viewport" and "needs updating"
        while terrains_todo:
            t = terrains_todo.pop()
            self._level.terrain_changes.remove(t) # remove t from the queue of tiles flagged to be updated
            # create/update terrain sprites
            x,y = self._level.geometry().raw_xy(t,tiles.tilewidth,tiles.tileheight)
            x += self._x_margin + self._x_offset
            y += self._y_margin + self._y_offset
            terrain = self._level.terrain(t)
            self._terraintiles[t] = pyglet.sprite.Sprite( terrain.image(), x, y, batch=self._batch, group=self._terrain_group )
            
        things_todo = tilerange & self._level.thing_changes
        while things_todo:
            t = things_todo.pop()
            self._level.thing_changes.remove(t) # remove t from the queue of tiles flagged to be updated
            # create/update thing sprites
            thing = self._level.top_thing_at(t) # may return None
            if thing == None: self._thingtiles[t] = None # delete sprite if exists
            else: 
                x,y = self._level.geometry().raw_xy(t,tiles.tilewidth,tiles.tileheight)
                x += self._x_margin + self._x_offset
                y += self._y_margin + self._y_offset
                self._thingtiles[t] = pyglet.sprite.Sprite( thing.image(), x, y, batch=self._batch, group=self._thing_group )
                
        critters_todo = tilerange & self._level.critter_changes 
        while critters_todo:
            t = critters_todo.pop()
            self._level.critter_changes.remove(t) # remove t from the queue of tiles flagged to be updated
            # create/update critter sprites
            critter = self._level.top_critter_at(t) # may return None
            if critter == None: self._crittertiles[t] = None # delete sprite if exists
            else: 
                x,y = self._level.geometry().raw_xy(t,tiles.tilewidth,tiles.tileheight)
                x += self._x_margin + self._x_offset
                y += self._y_margin + self._y_offset
                self._crittertiles[t] = pyglet.sprite.Sprite( tiles.get_char_tile(ord(critter.icon()),alphabet=0), x, y, batch=self._batch, group=self._critter_group )

    def move_view(self,row_move,col_move):
        "move the viewport by an increment, if possible"

        # calculate the maximum moves right or up (max left and down moves are given by _corner_col and _corner_row)
        max_right = self._level.geometry().cols() - self._visible_cols - self._corner_col
        max_up = self._level.geometry().rows() - self._visible_rows - self._corner_row
        # reduce the move to its limits, if applicable
        row_move = min( max( row_move, -self._corner_row ), max_up )
        col_move = min( max( col_move, -self._corner_col ), max_right )
        # check if we are actually moving
        if (row_move==0) and (col_move==0): return False
        else:
            self.relocate_view( self._corner_row + row_move, self._corner_col + col_move )
            return True

    def relocate_view(self,corner_row,corner_col):
        "move the viewport to a specific corner cell"
        
        self._corner_row = corner_row
        self._corner_col = corner_col
        # OFFSETS: how much the viewport is jiggered to put the corner tile in the corner
        self._x_offset = (-1)*(self._corner_col*tiles.tilewidth)
        self._y_offset = (-1)*(self._corner_row*tiles.tileheight)
        # determine which sprites are now visible
        new_visible_set = self._level.geometry().viewport( self._corner_row, self._corner_col, self._visible_rows, self._visible_cols )
        
        # render and reveal the ones that are NEWLY visible
        to_reveal = new_visible_set - self._visible_set
        self.render(to_reveal) # render changes to the newly visible tiles; if never viewed before, this will create the sprites
        for t in to_reveal:
            self._terraintiles[t].visible = True
            if self._thingtiles[t]: self._thingtiles[t].visible = True
            if self._crittertiles[t]: self._crittertiles[t].visible = True
            
        # hide the ones that are NEWLY invisible
        to_hide = self._visible_set - new_visible_set
        for t in to_hide:
            self._terraintiles[t].visible = False
            if self._thingtiles[t]: self._thingtiles[t].visible = False
            if self._crittertiles[t]: self._crittertiles[t].visible = False                
        
        # move every now-visible sprite to its new x,y location
        for t in new_visible_set:
            x,y = self._level.geometry().raw_xy(t,tiles.tilewidth,tiles.tileheight)
            x += self._x_margin + self._x_offset
            y += self._y_margin + self._y_offset
            self._terraintiles[t].x = x
            self._terraintiles[t].y = y
            if self._thingtiles[t]:
                self._thingtiles[t].x = x
                self._thingtiles[t].y = y
            if self._crittertiles[t]:
                self._crittertiles[t].x = x
                self._crittertiles[t].y = y

        # finally
        self._visible_set = new_visible_set
        self.adjust_cursor() # if there's a cursor, change its x,y position accordingly

    def resize_view(self,new_rows,new_cols,x_margin=0,y_margin=0):
        # try to keep the same corner tile...
        #  - visible_rows can't be greater than the true map
        self._visible_rows = min( new_rows, self._level.geometry().rows() )  # more rows cannot be visible than exist
        self._visible_cols = min( new_cols, self._level.geometry().cols() )
        #  - move the corner tile down and left if the window is resized too big
        corner_row = min( self._corner_row, self._level.geometry().rows() - self._visible_rows )  # the corner must be at least self._visible_rows below the top of the actual map
        corner_col = min( self._corner_col, self._level.geometry().cols() - self._visible_cols )  # and self._visible_cols to the left of the map's right edge
        
        # now determine the new viewport
        new_visible_set = self._level.geometry().viewport( corner_row, corner_col, self._visible_rows, self._visible_cols )

        # render and reveal NEWLY visible tiles
        to_reveal = new_visible_set - self._visible_set
        self.render(to_reveal) # render changes to the newly visible tiles; if never viewed before, this will create the sprites
        for t in to_reveal:
            self._terraintiles[t].visible = True
            if self._thingtiles[t]: self._thingtiles[t].visible = True
            if self._crittertiles[t]: self._crittertiles[t].visible = True

        # hide the tiles that are newly INvisible
        to_hide = self._visible_set - new_visible_set
        for t in to_hide:
            self._terraintiles[t].visible = False
            if self._thingtiles[t]: self._thingtiles[t].visible = False
            if self._crittertiles[t]: self._crittertiles[t].visible = False                

        # in case the corner has moved, adjust the offsets
        if not ( (corner_col==self._corner_col) & (corner_row==self._corner_row) ):
            # permanently change the corner
            self._corner_col = corner_col
            self._corner_row = corner_row
            # adjust the offsets
            self._x_offset = (-1)*(self._corner_col*tiles.tilewidth)
            self._y_offset = (-1)*(self._corner_row*tiles.tileheight)

        # adjust the margins according to the function call
        self._x_margin = x_margin
        self._y_margin = y_margin
            
        # move every now-visible sprite to its new x,y location
        for t in new_visible_set:
            x,y = self._level.geometry().raw_xy(t,tiles.tilewidth,tiles.tileheight)
            x += self._x_margin + self._x_offset
            y += self._y_margin + self._y_offset
            self._terraintiles[t].x = x
            self._terraintiles[t].y = y
            if self._thingtiles[t]:
                self._thingtiles[t].x = x
                self._thingtiles[t].y = y
            if self._crittertiles[t]:
                self._crittertiles[t].x = x
                self._crittertiles[t].y = y

        # remember the new _visible_set
        self._visible_set = new_visible_set

        # TODO: finally,if there's a cursor active, and it's not in the new viewport, move the view.
        self.check_cursor_outofbounds()

    def init_cursor(self,image=tiles.tiles["cursor"]):
        "creates a cursor at the default location, i.e. not remembering where it was before"
        # default location is the center of the visible viewport:
        xcenter = self._corner_row + (self._visible_rows//2)
        ycenter = self._corner_col + (self._visible_cols//2)
        # draw cursor at the tile number of the center tile in the current view
        self._cursor_tilenum = self._level.geometry().tile_at_coords(xcenter,ycenter)
        # make the cursor
        self._cursor = pyglet.sprite.Sprite( image, x=0, y=0, batch=self._batch, group=self._cursor_group )
        self.adjust_cursor()
        
    def adjust_cursor(self):
        "put the cursor sprite in the right place and make it visible"
        if self._cursor:
            x,y = self._level.geometry().raw_xy( self._cursor_tilenum, tiles.tilewidth, tiles.tileheight )
            x += self._x_margin + self._x_offset
            y += self._y_margin + self._y_offset
            self._cursor.x, self._cursor.y = x, y
        
    def destroy_cursor(self):
        "destroy the cursor"
        if self._cursor:
            self._cursor = None
    
    def move_cursor(self,row_move,col_move):
        "move the cursor by an increment of rows or columns"
        if self._cursor:
            # calculate the maximum moves right or up (max left and down moves are given by _corner_col and _corner_row)
            max_left = self._level.geometry().col( self._cursor_tilenum )
            max_right = self._level.geometry()._cols - self._level.geometry().col( self._cursor_tilenum ) - 1
            max_down = self._level.geometry().row( self._cursor_tilenum )
            max_up = self._level.geometry()._rows - self._level.geometry().row( self._cursor_tilenum ) - 1
            # reduce the move to its limits, if applicable
            row_move = min( max( row_move, -max_down ), max_up )
            col_move = min( max( col_move, -max_left ), max_right )
            # check if we are actually moving
            if (row_move==0) and (col_move==0): 
                return False
            else:
                newrow = self._level.geometry().row( self._cursor_tilenum ) + row_move
                newcol = self._level.geometry().col( self._cursor_tilenum ) + col_move
                self._cursor_tilenum = self._level.geometry().tile_at_coords(newrow,newcol)
                self.adjust_cursor()
                self.check_cursor_outofbounds()

    def check_cursor_outofbounds(self,trigger=2,moveto=5):
        """
        if the cursor is offscreen, move the screen to include it. if the cursor is unacceptably close to an edge, move if possible
        triggerzone = 2: by default, the cursor is out of bounds if it is 1 or 2 tiles from the screen edge
        moveto = 5: by default, the view is moved so the cursor is 5 cells from the edge
        """
        
        # only if cursor exists
        if self._cursor:
            #adjustments to make the math work
            move = moveto-1
            # don't act unless the cursor is outside of the visible set
            acceptable_set = self._level.geometry().viewport(self._corner_row+trigger,self._corner_col+trigger,self._visible_rows-(2*trigger),self._visible_cols-(2*trigger))
            if self._cursor_tilenum in acceptable_set:
                return False # no move needed
            else:
                cursor_row = self._level.geometry().row(self._cursor_tilenum)
                cursor_col = self._level.geometry().col(self._cursor_tilenum)
                # if the cursor is to the left of acceptable boundaries, move left enough to bring it into the boundary, plus a couple
                row_move, col_move = 0, 0
                if cursor_row < (self._corner_row + trigger): 
                    row_move = (cursor_row - self._corner_row) - move
                if cursor_row > (self._corner_row + self._visible_rows - trigger - 1): 
                    row_move = (cursor_row - (self._corner_row + self._visible_rows - 1)) + move 
                if cursor_col < (self._corner_col + trigger): 
                    col_move = (cursor_col - self._corner_col) - move
                if cursor_col > (self._corner_col + self._visible_cols - trigger - 1): 
                    col_move = (cursor_col - (self._corner_col + self._visible_cols - 1)) + move
                # move view if possible
                self.move_view(row_move,col_move)

    def cursor_tilenum(self):
        return self._cursor_tilenum



        
if __name__ == "__main__":
    "UNIT TEST CODE"
    import time
    from random import randint
    from pyglet.window import key
    import worldgen

    gd = worldgen.gen_world()
    v = Viewport(gd._level,x_margin=5,y_margin=5,corner_row=80,corner_col=80,visible_rows=20,visible_cols=20)
    w = pyglet.window.Window()
    
    @w.event
    def on_draw():
        w.clear()
        start = time.clock()
        v.render()
        v.draw()
        print(time.clock()-start)

    @w.event
    def on_key_press(symbol,modifiers):
        if symbol == key.NUM_8: print(v.move_view(3,0))
        if symbol == key.NUM_2: print(v.move_view(-3,0))
        if symbol == key.NUM_4: print(v.move_view(0,-3))
        if symbol == key.NUM_6: print(v.move_view(0,3))
        if symbol == key.TAB: v.resize_view(25,25)
        if symbol == key.GRAVE: v.init_cursor()
        if symbol == key.UP: v.move_cursor(1,0)
        if symbol == key.DOWN: v.move_cursor(-1,0)
        if symbol == key.LEFT: v.move_cursor(0,-1)
        if symbol == key.RIGHT: v.move_cursor(0,1)
        
    pyglet.app.run()

