"Rogue State University"
-free and open source-


CONTRIBUTORS:
Joseph Clark -- joseph.w.clark@asu.edu


PREMISE:
This is going to be a relatively simple roguelike game written in Python with Pyglet. It will incorporate some code that I wrote for earlier, unfinished games, so I can delete those old repositories.  Consider it a vanilla game that you can build on top of.


STATUS:
The game is running but not playable, yet.  My code sets up the window, main menu, initializes a game (currently a grassy field with a few plants), and allows you to move the view around.  Hold SHIFT to move quickly, CTRL to move precisely.  Press TAB to get a "look/examine" cursor and see what's on each tile.  Press "I" to toggle the information panel at the right (which currently has no information in it).  You can resize the window.  Press ESC for an escape menu.

Originally this was going to be a fortress simulation, so I never wrote code for first person control of an "@" character.  That'll be next.  Also, world generation will need to be tweaked to create items and terrain better suited to a dungeon.


DEVELOPED USING:
Python 3.4
pyglet 1.2alpha1 (included in /program/dependencies/ directory)


TO PLAY:
Run "roguestate.py".
