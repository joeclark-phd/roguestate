
# The pyglet library calls itself a lot with "import pyglet".
# Since I want to package the library with the game (rather
# than assume players have it installed on their PYTHONPATH)
# here I simply add the containing folder to the PYTHONPATH
# for the duration of execution. This does not need to be
# repeated in every script.

import sys
from os import path

cwd = sys.path[0]  # current working directory

# i can have as many of these as necessary...
sys.path.insert(0,path.join(cwd,"program"))


# this launches the game window
import program.window