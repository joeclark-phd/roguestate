"""
Generates frequently-used graphics concepts, such as boxes and menus.
"""

import pyglet
import tiles




class GraphicalMenu:
    """
    A graphical menu object including its graphics and logic.
    A number of options allow it to be drawn with or without a border,
    positioned by its center or its (bottom-left) origin, etc.
    """
    
    def __init__(self,*options,fixedwidth=None,fixedheight=None,hpadding=2,vpadding=0,spacing=1,xcenter=None,ycenter=None,xleft=None,ybottom=None,border=True,center_aligned=True):
        self.options = options # it helps if options all have an even-number of characters. all-odd is second best. mixed even/odd looks worst.
        self.selection = 0 # which option is selected

        # determine menu width in characters
        if fixedwidth: 
            self._width = fixedwidth
        else: 
            self._width = max( [len(o) for o in options] ) + (2*hpadding)
            if border: self._width += 2
        # determine height
        if fixedheight: 
            self._height = fixedheight
        else: 
            self._height = len(options) + ((len(options)+1)*spacing) + (2*vpadding) # spacing = the number of blank lines between options
            if border: self._height += 2
        # generate the character matrix in steps (as integer/ascii codes before converting to sprites)
        self._characters = [[255 for c in range(self._width)] for r in range(self._height)] # lists of columns in rows
        # add the border
        if border:
            self._characters[0][0] = 201 # top left corner
            self._characters[0][-1] = 187 # top right
            self._characters[-1][0] = 200 # bottom left
            self._characters[-1][-1] = 188 # bottom right
            for r in (0,-1):
                for c in range(1,(self._width-1)):
                    self._characters[r][c] = 205 # horizontal top/bottom border
            for r in range(1,(self._height-1)):
                for c in (0,-1):
                    self._characters[r][c] = 186 # vertical side borders
        # add the options and keep track of their positions (row,column from top-left)
        self._optionpositions = []
        for o in range(len(options)):
            row = border + vpadding + o + (o+1)*spacing
            col = self._width//2 - len(options[o])//2
            self._optionpositions.append( (row,col) )
            for c in range(len(options[o])):
                self._characters[row][col+c] = ord(options[o][c])
        # figure out on-screen positioning in x,y terms
        if not xleft == None: self._x_offset = xleft
        else:
            if xcenter == None: 
                print("neither xleft nor xcenter specified. default to zero")
                self._x_offset = 0
            else:
                self._x_offset = xcenter - (self._width*tiles.tilewidth)//2
        if not ybottom == None: self._y_offset = ybottom
        else:
            if ycenter == None: 
                print("neither ybottom nor ycenter specified. default to zero")
                self._y_offset = 0
            else:
                self._y_offset = ycenter - (self._height*tiles.tileheight)//2
        # transform _characters to _sprites
        self._batch = pyglet.graphics.Batch()
        self._sprites = [[ pyglet.sprite.Sprite( tiles.get_char_tile(self._characters[r][c],alphabet=0),
                             x=(c*tiles.tilewidth)+self._x_offset, y=((self._height-r-1)*tiles.tileheight)+self._y_offset,
                             batch=self._batch) 
                           for c in range(len(self._characters[r]))] for r in range(len(self._characters))]
        # generate the cursor images
        self.generate_cursors() # this is outsourced to another function so that I can alter it by extending the class instead of deleting
        
    def generate_cursors(self):
        "generate sprites for 'cursors' or highlighted options; one for each option"
        self._cursorbatches = []
        self._cursorsprites = []
        for o in range(len(self.options)):
            b = pyglet.graphics.Batch()
            # this code implements cursors as highlighted [ ] brackets around the option
            self._cursorsprites.append( pyglet.sprite.Sprite( tiles.get_char_tile(ord("["),alphabet=1),
                                                              x = ( (self._optionpositions[o][1]-1) * tiles.tilewidth ) + self._x_offset,
                                                              y = ( (self._height - self._optionpositions[o][0] - 1) * tiles.tileheight ) + self._y_offset,
                                                              batch = b ) )
            self._cursorsprites.append( pyglet.sprite.Sprite( tiles.get_char_tile(ord("]"),alphabet=1),
                                                              x = ( (self._optionpositions[o][1]+len(self.options[o])) * tiles.tilewidth ) + self._x_offset,
                                                              y = ( (self._height - self._optionpositions[o][0] - 1) * tiles.tileheight ) + self._y_offset,
                                                              batch = b ) )
            self._cursorbatches.append(b)
            
    def option_up(self):
        if self.selection == 0: 
            self.selection = len(self.options)-1
        else: 
            self.selection -= 1
			
    def option_down(self):
        if self.selection == (len(self.options)-1): 
            self.selection = 0
        else: 
            self.selection += 1
			
    def draw(self):
        self._batch.draw()
        self._cursorbatches[self.selection].draw()
            
            
            
            

if __name__ == "__main__":
    "UNIT TEST CODE"
    gm = GraphicalMenu("foo","bar","xyz")
    print( gm._width )
    print( gm._height )
    print(gm._characters)
    print(gm._optionpositions)
    print( [[(c*tiles.tilewidth) for c in range(len(gm._characters[r]))] for r in range(len(gm._characters))] )