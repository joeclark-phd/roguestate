
"""
Pre-loads and provides the graphics, generating ImageData objects with the
specified characters and fg/bg colors.  Reads data from plain-text info files.
"""

import preferences
import pyglet
pyglet.resource.path = ['program/resources/info','resources/info','program/resources/tiles','resources/tiles']
import re # for regular expressions
RGBcolor = re.compile("[0-9a-f]{6}")  # regular expression for a 6 digit hexadecimal number
AAlpha = re.compile("[0-9a-f]{2}")  # for a 2 digit alpha value
from debug import error_log
import sys # to flush the console

#############################################
# FUNCTIONS TO BE USED IN GENERATING IMAGES #
#############################################

def generate_colorized_tile(tilenum,fg_color=b'\xff\xff\xff\xff',bg_color=b'\x00\x00\x00\xff'):
    "returns a new image by transforming the foreground and background colors of one of the raw (white on black) tiles"
    rawpic = tileset[tilenum]
    return colorize(rawpic,fg_color,bg_color)

def colorize(image,fg_color,bg_color):
    """
    returns an image transformed to a new set of colors; note that this
    works on the individual tiles which are TextureRegions, but doesn't
    work on the imported image (tilegrid) itself. The discrepancy is due
    to the line image.image_data.get_data returning a different form of
    data for these two types of objects.
    """
    picdata = image.image_data.get_data("RGBA",image.width*4) # as a byte string of RGBA bytes
    pixels = [picdata[x:x+4] for x in range(0,len(picdata),4)] # split that string into 4-byte strings representing pixels
    blackcolor = b'\x00\x00\x00\xff'
    whitecolor = b'\xff\xff\xff\xff'
    bgs = [y for y in range(len(pixels)) if pixels[y]==blackcolor] # indexes of background pixels
    fgs = [y for y in range(len(pixels)) if pixels[y]==whitecolor] # indexes of foreground pixels
    for i in bgs: pixels[i] = bg_color # transform background to specified RGBA values
    for i in fgs: pixels[i] = fg_color # transform foreground to specified RGBA values
    pixel_out = b''
    for j in pixels:
        pixel_out += j # merge back into a single byte string
    return pyglet.image.ImageData(image.width,image.height,"RGBA",pixel_out) # generate a new image with the new data

def get_char_tile(tilenum,alphabet):
    "returns the (character) imagedata for a given ascii code (0 to 255) and alphabet (0=plaintext,1=highlighted)"
    return alphabets[alphabet][tilenum]

def get_tile_string(text):
    "returns a list of tiles for a given string; does not keep track of text wrapping or anything like that"
    return [get_char_tile(ord(x)) for x in text]

def generate_sprite_string(text,x,y,batch,alphabet=0):
    "returns a set of sprites (with position and batch assigned) for a text string; lower-left corner at x,y"
    return [pyglet.sprite.Sprite( get_char_tile(ord(text[i]),alphabet), x=x+(i*tilewidth), y=y, batch=batch) for i in range(len(text))]


###########################################################################
# LOADING OF COLORS AND IMAGES: TO RUN WHEN THIS MODULE IS FIRST IMPORTED #
###########################################################################

# IMPORT RAW (UNCOLORED) TILE GRAPHICS
tilegrid = pyglet.resource.image( preferences.prefs["tileset"] )
tilerows = int( preferences.prefs["tileset_rows"] )
tilecols = int( preferences.prefs["tileset_columns"] )
tilewidth,tileheight = tilegrid.width//tilecols, tilegrid.height//tilerows # tile width/height, assuming a 16x16 grid

print("Loading tileset.",end="")
tileset = pyglet.image.ImageGrid(tilegrid,tilerows,tilecols)  # split into equal sized tiles, assuming they are in a 16x16 grid
print(".",end="")
sys.stdout.flush()
# pyglet starts from the bottom left, not top left, so we need to re-order the list just a bit
tileset = tuple(zip(*[iter(tileset)]*16))[::-1] # this one-liner should split the sequence into (rows) groups of 16 and then reverse their order
print(".",end="")
sys.stdout.flush()
#tileset = [tileset[x:x+16] for x in range(0,len(tileset),16)][::-1] # alternate way to do the same thing
tileset = [tile for row in tileset for tile in row] # merge back into a one-dimensional list
print(" done.")

# PARSE palette.txt AND LOAD THE DICTIONARY OF NAMED COLORS (COLOR SCHEME)
print("Loading palette.",end="")
palette = {} # a dictionary of named colors
palettefile = pyglet.resource.file('palette.txt',"r")
for line in palettefile:
    line = line.strip().lower()
    if line.find("#") > -1: line = line[:line.find("#")] # remove first "#" and everything after
    if len(line):
        # line has content, now test if it's valid
        data = line.split("=")
        if len(data) == 2:
            # two items means there was an "=", now make sure the bit on the right is a valid color
            colorcode = data[1].strip()
            if RGBcolor.match( colorcode ) : # only checks first 6 digits; junk afterwards can be ignored
                # we now have a valid color (we haven't checked for valid alpha yet)
                color = r"\x" + colorcode[0:2] + r"\x" + colorcode[2:4] + r"\x" + colorcode[4:6]
                if (len(colorcode) > 7) and (AAlpha.match(colorcode[6:8])): color += r"\x" + colorcode[6:8] # add alpha data
                else: color += r"\xff" # if no alpha data, default to ff (no transparency)
                # add the new named color to the palette
                palette[data[0].strip()] = eval("b'"+color+"'") #turn this text string into a byte string when adding to palette dictionary
                print(".",end="")
                sys.stdout.flush()
            else:
                error_log("invalid color: ",colorcode)
        else:
            error_log("invalid palette entry: ",data)
print(" done.")

# COLORIZE THE ASCII ALPHABETS (THE FIRST 256 CHARACTERS) IN THE DEFAULT TEXT COLORS
print("Colorizing fonts.",end="")
alphabets = [ [], [], [] ] # plain, highlighted, and inverted text
for i in range(256):
    alphabets[0].append( generate_colorized_tile( i , palette["plaintext"] , palette["bg"] ) )
    alphabets[1].append( generate_colorized_tile( i , palette["highlight"] , palette["bg"] ) )
    alphabets[2].append( generate_colorized_tile( i , palette["bg"] , palette["plaintext"] ) )
    print(".",end="")
    sys.stdout.flush()
print(" done.")

# NOW PARSE tiles.txt AND GENERATE ALL SPRITES FOR PROMPT LOADING WHEN NEEDED
print("Generating graphics.",end="")
tiles = {} # a dictionary of images
tilefile = pyglet.resource.file('tiles.txt',"r")
for line in tilefile:
    line = line.strip().lower()
    if line.find("#") > -1: line = line[:line.find("#")] # remove first "#" and everything after
    if len(line):
        # line has content, now test if it's valid
        data = line.split("=")
        if len(data) == 2:
            # two items means there was an "=", now make sure the bit on the right is valid
            image_id = data[0].strip() # the image_id
            details = data[1].split(":") # the tile number and colors defining the image
            if len(details) == 3:
                # the right number of details, so far so good
                # from here on out, if details are empty or invalid, replace them with defaults
                tile_id = details[0].strip()
                if tile_id.isnumeric() and ( 0 <= int(tile_id) < len(tileset) ): tile_id = int(tile_id)
                else: tile_id = 255 # the "empty" character (all background)
                # foreground color may be a hexadecimal code (with or without alpha) or a named color
                fgcode = details[1].strip()
                if RGBcolor.match( fgcode ):
                    fgcolor = r"\x" + fgcode[0:2] + r"\x" + fgcode[2:4] + r"\x" + fgcode[4:6]
                    if (len(fgcode) > 7) and (AAlpha.match(fgcode[6:8])): fgcolor += r"\x" + fgcode[6:8] # add alpha data
                    else: fgcolor += r"\xff" # if no alpha data, default to ff (no transparency)
                    fgcolor = eval("b'"+fgcolor+"'") # turn text string into a byte string
                else:
                    #user gave a named color, check if it's in the palette
                    if fgcode in palette:
                        fgcolor = palette[fgcode]
                    elif len(fgcode) == 0:
                        fgcolor = palette["fg"]
                    else:
                        fgcolor = palette["fg"]
                        error_log("no color called: ",fgcode," (going with default)")
                # background color may be a hexadecimal code (with or without alpha) or a named color
                bgcode = details[2].strip()
                if RGBcolor.match( bgcode ):
                    bgcolor = r"\x" + bgcode[0:2] + r"\x" + bgcode[2:4] + r"\x" + bgcode[4:6]
                    if (len(bgcode) > 7) and (AAlpha.match(bgcode[6:8])): bgcolor += r"\x" + bgcode[6:8] # add alpha data
                    else: bgcolor += r"\xff" # if no alpha data, default to ff (no transparency)
                    bgcolor = eval("b'"+bgcolor+"'") # turn text string into a byte string
                else:
                    #user gave a named color, check if it's in the palette
                    if bgcode in palette:
                        bgcolor = palette[bgcode]
                    elif len(bgcode) == 0:
                        bgcolor = palette["no_bg"]
                    else:
                        bgcolor = palette["no_bg"]
                        error_log("no color called: ",bgcode," (going with default)")
                #print("name","tile_id:",tile_id,"fgcolor",fgcolor,"bgcolor",bgcolor)
                tiles[image_id] = generate_colorized_tile( tile_id, fgcolor, bgcolor ) # generate the new image
                print(".",end="")
                sys.stdout.flush()
            else:
                error_log("improper tiles.txt entry for: ",image_id)
        else:
            error_log("improper tiles.txt entry: ",data)


print(" done.")





if __name__ == "__main__":
    "UNIT TEST CODE"
    print(tiles)
