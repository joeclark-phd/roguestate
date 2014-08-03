
"""
Pre-loads user preferences from plain-text info files.
"""

import pyglet
pyglet.resource.path = ['program/resources/info','resources/info','program/resources/tiles','resources/tiles']
from debug import error_log
import sys



# PARSE prefs.txt AND LOAD THE DICTIONARY OF PREFERENCES
print("Loading preferences.",end="")
prefs = {} # a dictionary of preferences
prefsfile = pyglet.resource.file('prefs.txt',"r")
for line in prefsfile:
    line = line.strip().lower()
    if line.find("#") > -1: line = line[:line.find("#")] # remove first "#" and everything after
    if len(line):
        # line has content, now test if it's valid
        data = line.split("=")
        if len(data) == 2:
            # two items means there was an "="
            prefs[ data[0].strip() ] = data[1].strip() # capture the preference (TO DO: better error checking)
            print(".",end="")
            sys.stdout.flush()
        else:
            error_log("invalid preferences entry: ",data)
print(" done.")




if __name__ == "__main__":
    # UNIT TEST CODE
    print(prefs)
