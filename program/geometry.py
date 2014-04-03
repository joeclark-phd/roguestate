"map geometries"
  



class AbstractGeometry:
    """
    Pattern for a rectangular geometry, hex geometry, etc.
    The first call should determine exactly how many tiles are in the map, so other objects can
    deal with a tile# instead of row/col coordinates. The AbstractGeometry object will handle
    pathfinding and provide relative x,y positions on screen.
    """
    
    #direction constants
    EAST = 0
    NE = 1
    NORTH = 2
    NW = 3
    WEST = 4
    SW = 5
    SOUTH = 6
    SE = 7
    
    def __init__(self,*dimensions):
        # determine the number of map tiles given the desired dimensions (in tiles)
        # set up internal coordinate system
        pass
    def tilecount(self):
        # return the number of tiles
        return self.num_tiles
    def viewport(self,*args):
        # return the set of tile numbers visible given the arguments
        pass
    def raw_xy(self,tile,tilewidth,tileheight):
        # return the x,y offset from the abstract map origin for a given tile for a given tile size
        # (not necessarily where it will appear on screen -- another object will adjust the "viewport")
        pass
    def dir_distance(self,direction):
        # return the distance of a "step" in this direction (e.g. using pythagorean theorem or other math)
        pass
    def adjacent(self,origin,direction):
        # returns the tile # adjacent to the current one in the specified direction, or None.
        # (None means either the direction is invalid in this geometry, or the adjacent tile is off the map)
        pass
    def nearest_tiles(self,origin,n):
        # return an ordered list of the n nearest tile #s from the origin
        pass
    def tiles_within(self,origin,n):
        # return an ordered list (from nearest to farthest) of all tiles up to n steps from the origin
        pass        
    def path_from_to(self,origin,destination):
        # return a list of tile #s on the shortest path from origin to destination
        pass





        
        
        
class Rectangle8(AbstractGeometry):
    """
    Implements the methods of AbstractGeometry for a rectangular map where eight directions of movement
    are allowed (i.e. including the diagonals).
    """
    def __init__(self,cols,rows):
        self._cols = cols
        self._rows = rows
        # determine the number of map tiles given the desired width/height (in tiles)
        self.num_tiles = (cols*rows)
        # set up internal tile-to-coordinate system
        self.tile_to_coords = []
        for r in range(rows):
            for c in range(cols):
                self.tile_to_coords.append((r,c))
        # set up coordinate-to-tile lookup dictionary (reverse of above)
        self.coords_to_tile = dict( zip(self.tile_to_coords,range(self.num_tiles)) )
        # define valid directions for this geometry
        self.valid_directions = { self.EAST:1, self.NE:1.4, self.NORTH:1, self.NW:1.4, self.WEST:1, self.SW:1.4, self.SOUTH:1, self.SE:1.4 }
        # coordinate adjustments for a "step" in each direction
        self.adj = { self.EAST: (0,1), self.NE: (1,1), self.NORTH: (1,0), self.NW: (1,-1), self.WEST: (0,-1), self.SW: (-1,-1), self.SOUTH: (-1,0), self.SE: (-1,1) } 
    def viewport(self,corner_row,corner_col,display_rows,display_cols):
        visible_tiles = set()
        if (display_rows == 0): display_rows = self._rows - corner_row # in this case we assume they want all of them to the top
        if (display_cols == 0): display_cols = self._cols - corner_col # in this case we assume they want all of them to the end
        try:
            for r in range(corner_row,corner_row+display_rows):
                for c in range(corner_col,corner_col+display_cols):
                    visible_tiles.add( self.coords_to_tile[(r,c)] )
            return visible_tiles
        except KeyError:
            # viewport is out of bounds
            return None
    def raw_xy(self,tile,tilewidth,tileheight):
        # return the x,y offset from the abstract map origin for a given tile for a given tile size
        # (not necessarily where it will appear on screen -- another object will adjust the "viewport")
        r,c = self.tile_to_coords[tile]
        return (c*tilewidth),(r*tileheight)   
    def dir_distance(self,direction):
        # return the distance of a "step" in this direction (e.g. using pythagorean theorem or other math)
        if not direction in self.valid_directions: return None
        else: return self.valid_directions[direction]
    def adjacent(self,origin,direction):
        # returns the tile # adjacent to the current one in the specified direction, or None.
        # (None means either the direction is invalid in this geometry, or the adjacent tile is off the map)
        if not direction in self.valid_directions: return None
        else:
            origin_coords = self.tile_to_coords[origin]
            # add the origin_coords and the adj. to get the move-to coordinates
            move_to_coords = tuple(sum(q) for q in zip(origin_coords,self.adj[direction]))
            if move_to_coords in self.coords_to_tile: return self.coords_to_tile[move_to_coords]
            else: return None # if the move is off the map
    def rows(self):
        return self._rows
    def cols(self):
        return self._cols
    def row(self,tile):
        # return the row of a given tile
        return self.tile_to_coords[tile][0]
    def col(self,tile):
        # return the column of a given tile
        return self.tile_to_coords[tile][1]
    def tile_at_coords(self, row, col):
        if (row,col) in self.coords_to_tile:
            return self.coords_to_tile[ (row,col) ]
        else:
            return False
        
        



        
class HexVertical(AbstractGeometry):
    """
    Implements the methods of AbstractGeometry for a hexagon grid map with vertical edges
    (i.e., travel left-right is possible, but up-down is not).
    The first (bottom) row will be a short one. An odd number of rows is recommended for symmetry.
    """
    def __init__(self,cols,rows):
        # determine the number of map tiles given the desired width/height (in tiles)
        self.num_tiles = (cols*rows) - (rows//2) - (rows%2)
        # set up internal tile-to-coordinate system
        self.tile_to_coords = []
        for r in range(rows):
            adjcols = cols if (r%2) else (cols - 1) # odd numbered rows have 1 fewer column
            for c in range(adjcols):
                self.tile_to_coords.append((r,c))
        # set up coordinate-to-tile lookup dictionary (reverse of above)
        self.coords_to_tile = dict( zip(self.tile_to_coords,range(self.num_tiles)) )
        # define valid directions for this geometry, and their distance multipliers
        self.valid_directions = { self.EAST:1, self.NE:1, self.NW:1, self.WEST:1, self.SW:1, self.SE:1 }
        # moves in this geometry are implemented differently in odd and even rows, so we'll create two dictionaries for directional adjustments
        self.adj = [ { self.EAST: (0,1), self.NE: (1,1), self.NW: (1,0), self.WEST: (0,-1), self.SW: (-1,0), self.SE: (-1,1) } ,  # for even rows
                     { self.EAST: (0,1), self.NE: (1,0), self.NW: (1,-1), self.WEST: (0,-1), self.SW: (-1,-1), self.SE: (-1,0) }]  # for odd rows
    def raw_xy(self,tile,tilewidth,tileheight):
        # return the x,y offset from the abstract map origin for a given tile for a given tile size
        # (not necessarily where it will appear on screen -- another object will adjust the "viewport")
        r,c = self.tile_to_coords[tile]
        if r%2: return (c*tilewidth),(r*tileheight) #formula for even (short) rows
        else: return ((c*tilewidth)+tilewidth//2),(r*tileheight) #formula for odd (long) rows   
    def dir_distance(self,direction):
        # return the distance of a "step" in this direction (e.g. using pythagorean theorem or other math)
        if not direction in self.valid_directions: return None
        else: return self.valid_directions[direction]
    def adjacent(self,origin,direction):
        # returns the tile # adjacent to the current one in the specified direction, or None.
        # (None means either the direction is invalid in this geometry, or the adjacent tile is off the map)
        if not direction in self.valid_directions: return None
        else:
            origin_coords = self.tile_to_coords[origin]
            # the adjustments that correspond to each direction are different in even/odd rows
            adjustment = self.adj[ origin_coords[0]%2 ]  # get the geometry's dictionary of move-to adjustments
            # add the origin_coords and the adj. to get the move-to coordinates
            move_to_coords = tuple(sum(q) for q in zip(origin_coords,adjustment[direction]))
            if move_to_coords in self.coords_to_tile: return self.coords_to_tile[move_to_coords]
            else: return None # if the move is off the map

        

        










        
        
if __name__ == "__main__":
    "UNIT TEST CODE"
    rect = Rectangle8(10,10)
    print( rect.viewport(2,2,5,5) )