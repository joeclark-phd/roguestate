"structures for holding/accessing/saving/loading data in the current game"
import geometry
import tiles # only used in terrain type; not needed yet
from collections import defaultdict # used in creating dictionaries of lists/sets for quick-access indexes
from debug import error_log
import random




class GameData:
    """
    Holds all the data on maps, objects, entities for a single game.
    Should not hold any graphics or game-specific functions.
    Saving/loading this object alone to/from disk should be sufficient to save/load the game.
    """
    
    def __init__(self,geometry,terrain):
        #set up empty data structures
        self._level = Level(geometry,terrain) # the game's map (called "level" to avoid conflict with a python reserved word)
        self._things = [] # a list of inanimate objects in the game (including dead/gone)
        self._critters = [] # a list of creatures in the game (including dead/gone)

        #The things/critters lists could get long and slow down the game, so it is preferred to use
        # smaller indexes containing sets of things/critters with certain tags. For example, critters might
        # be tagged [alive] and those without that tag need not be processed for movement/action. Items may
        # have tags like [luminous] or [food] for quick access.
        #Each Level will have things_at/critters_at indexes.  A quick way to do a search for a nearby food
        # item, for example, would be to take the intersection of the [food] set with the 
        # [located at:level,tile] set(s) for the closest tiles until you find one.
        #These indexes can be generated at runtime as we read in the thing/critter types from text files.
        self.thing_indexes = {}
        self.critter_indexes = {}

    def level(self):
        return self._level
        
    def create_thing(self,thing,critter=None,tile=None):
        #add a new inanimate object to the game: specify either a critter's inventory or a map tile
        self._things.append(thing)
        if tile: self._level.place_thing(thing,tile) # place the thing on the map
        elif critter: pass # place the thing in critter's inventory
        else: pass # create the thing but do not place it in the world

    def create_critter(self,critter,tile=None):
        #add a new critter to the game at a specified location
        self._critters.append(critter)
        if tile: self._level.place_critter(critter,tile) # place the critter on the map
        else: pass # create the critter but don't place it in the world
        
    def look(self,tilenum):
        #return a list of objects at a tile in the order they are "seen" (i.e. top to bottom)
        #print("looking at",tilenum)
        seen = self._level._critters_at[tilenum][::-1] + self._level._things_at[tilenum][::-1] + [self._level._terrains[tilenum]]
        output = [s.name() for s in seen]
        print(output)
        
        





        
class Level:
    """
    Represents a single 2D map/level in the game.
    Holds an AbstractGeometry object and a list containing terrain data for every cell.
    Also some indexes to things and critters located in the level.
    """
    
    def __init__(self,geom,default_terrain):
        self._geom = geom
        self._terrains = [default_terrain for t in range(self._geom.tilecount())] # list containing one Terrain object for each tile
        self._things_at = defaultdict(list) # dictionary of lists(stacks) of inanimate objects indexed by tile#
        self._critters_at = defaultdict(list) # dictionary of lists(stacks) of critters indexed by tile#
        self.refresh()  # This function flags all terrains, etc as "changed" so the viewport will "clear its cache" and re-draw all tiles.

        
    def refresh(self):
        # These "change queues" inform any outside observer (i.e. the graphics Viewport)
        # which tiles have been updated since it last checked. The observer should pop() 
        # them as it processes them.
        self.terrain_changes = set(range(self._geom.tilecount()))
        self.thing_changes = set(self._things_at)
        self.critter_changes = set(self._critters_at)
    def geometry(self):
        return self._geom
    def terrain(self,tile):
        return self._terrains[tile]
    def top_thing_at(self,tile):
        if len(self._things_at[tile]): return self._things_at[tile][-1]
        else: return None # if item stack for tile is empty
    def top_critter_at(self,tile):
        if len(self._critters_at[tile]): return self._critters_at[tile][-1]
        else: return None # if item stack for tile is empty
    def place_thing(self,thing,tile): # put a thing into a place on the level (doesn't actually create it)
        self._things_at[tile].append(thing) # "stack" a thing
        self.thing_changes.add(tile) # signal a change
    def place_critter(self,critter,tile): # put a critter into a place on the level (doesn't actually create it)
        self._critters_at[tile].append(critter) # "stack" a critter
        self.critter_changes.add(tile) # signal a change

        
        
        
        
       

class Grass:
    # an example of a terraintype (in the real game the types should be loaded from a text file and made into objects at runtime)
    def image(self):
        return tiles.tiles["grassland"]
    def name(self):
        return "a patch of grass"

class Shrubbery:
    # an example of a thing (in the real game the types should be loaded from a text file and made into objects at runtime)
    def image(self):
        return tiles.tiles["shrubbery"]
    def name(self):
        return "a shrubbery"

class PlantType:
    # a type of plant: contains the tile/image as well as the plant type's properties
    def __init__(self,name,tile,tags):
        self._name = name
        self._tile = tile
        self._tags = tags
    def name(self):
        return self._name
    def image(self):
        return self._tile


        
        
if __name__ == "__main__":
    "UNIT TEST CODE"
    gd = GameData()
    print( gd._level._terrains )