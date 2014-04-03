"generate a new gamedata object"

import gamedata, geometry, random, tiles
import pyglet
pyglet.resource.path = ['program/resources/info','resources/info','program/resources/tiles','resources/tiles'] 
import sys


def gen_world():
    planttypes = generate_plantlife()
    gdata = gamedata.GameData( geometry.Rectangle8(100,100), gamedata.Grass() )         
    for i in range(1000):
        # generate a thousand shrubberies
        gdata.create_thing( random.choice(planttypes),tile=random.randint(0,gdata.level().geometry().tilecount()-1))
    return gdata
    
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