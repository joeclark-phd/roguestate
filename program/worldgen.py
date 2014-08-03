"generate a new gamedata object"

import gamedata, geometry, random, tiles
import pyglet
pyglet.resource.path = ['program/resources/info','resources/info','program/resources/tiles','resources/tiles'] 
import sys


def gen_world():
    planttypes = generate_plantlife()
    terraintypes = generate_terrain()
    gdata = gamedata.GameData( geometry.Rectangle8(100,100), terraintypes[1] )  #terraintypes[1] is green grass;
    
    
    btiles = [] #an array of all "building tiles" so far
    i = 0;
    while i < 30 :
        # generate rectangles of walls with tile floors inside
        nextrect = gdata.level().geometry().rectangle( gdata.level().geometry().randomtile(), 9, 9 )
        if len([val for val in nextrect if val in btiles]) == 0:
            # only build a room if this doesn't intersect an existing room
            for t in nextrect:
                btiles.append(t)
            inside_corner = gdata.level().geometry().adjacent(nextrect[0],geometry.AbstractGeometry.NE)
            if inside_corner:
                #this will fail if the building starts at the top or right edge of the map, so there is no "inside"
                interior = gdata.level().geometry().rectangle( inside_corner, 7, 7 )
                for t in interior:
                    gdata.create_terrain( terraintypes[2], tile=t ) #terraintypes[2] is a tile floor
                # now remove the interior tiles from 'nextrect' so we just have a list of wall tiles
                nextrect = [val for val in nextrect if not val in interior]
            for t in nextrect:
                gdata.create_terrain( terraintypes[0], tile=t ) #terraintypes[0] is the brick wall
            # now create a doorway
            gdata.create_terrain( terraintypes[2], tile=random.choice(nextrect) )
            i = i + 1
        
        #gdata.create_terrain( gamedata.Wall(), tile=gdata.level().geometry().randomtile() )

    
    for i in range(1000):
        # generate a thousand shrubberies
        t = gdata.level().geometry().randomtile()
        if not "built" in gdata.level().terrain(t)._tags:
            gdata.create_thing( random.choice(planttypes),tile=t )
	
	#pick a random tile for the player and tell the GameData to initialize him there
    ptile = gdata.level().geometry().randomtile()
    while "built" in gdata.level().terrain(ptile)._tags: # don't let the player start indoors
        ptile = gdata.level().geometry().randomtile()
    gdata.init_player_at(ptile)
    
    return gdata

    
def generate_terrain():
    # read the terrain.txt file, generate terrain as gamedata.TerrainTypes
    print("Generating terrain.",end="")
    terraintypes = []
    terrainsfile = pyglet.resource.file('terrains.txt',"r")
    for line in terrainsfile:
        line = line.strip().lower()
        if line.find("#") > -1: line = line[:line.find("#")] # ignore comments beginning with "#"
        if len(line):
            # line has content, now test if it's valid
            data = line.split(":")
            if len(data) == 3:
                # 3 items expected
                terraintypes.append( gamedata.TerrainType( data[0].strip(), tiles.tiles[data[1].strip()], data[2].strip() ) ) # create the TerrainType
                print(".",end="")
                sys.stdout.flush()
            else:
                error_log("invalid preferences entry: ",data)
    print(" done.")
    return terraintypes
    
    
def generate_plantlife():
    # read the plants.txt file, generate plants as gamedata.PlantTypes
    print("Generating plants.",end="")
    planttypes = [] # a list of plant types
    plantsfile = pyglet.resource.file('plants.txt',"r")
    for line in plantsfile:
        line = line.strip().lower()
        if line.find("#") > -1: line = line[:line.find("#")] # remove first "#" and everything after
        if len(line):
            # line has content, now test if it's valid
            data = line.split(":")
            if len(data) == 3:
                # 3 items expected
                planttypes.append( gamedata.PlantType( data[0].strip(), tiles.tiles[data[1].strip()], data[2].strip() ) ) #create the PlantType
                print(".",end="")
                sys.stdout.flush()
            else:
                error_log("invalid preferences entry: ",data)
    print(" done.")            
    return planttypes
    
    