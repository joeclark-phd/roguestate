"""
Procedural generation of names based on dictionaries.
Uses the "high-order markov process and simplified katz back-off scheme" algorithm 
described by JLund3 (but not his code) found at: 
http://roguebasin.roguelikedevelopment.org/index.php?title=Names_from_a_high_order_Markov_Process_and_a_simplified_Katz_back-off_scheme
Also borrows the idea of sokol815 who uses include/exclude lists to generate words of certain types:
http://roguetemple.com/forums/index.php?topic=3083.msg25619#msg25619

USAGE:##
Put a textfile full of names (one on each line) in  your pyglet resource path.
Build a new name generator with its models like so:
    roman_names = NameGenerator( "roman.txt",order=3,prior=0.01 ) 
Generate a name like so:
    a = roman_names.generate(1) # generate 1 name
Optional parameters:
    b = roman_names.generate(1,minlen=3,maxlen=12) # filters for length
    c = roman_names.generate(1,includes=["ae","x"]) # return names that include one or more substrings
    d = roman_names.generate(1,includes=["#cae"])   # the "#" string signals the beginning/end of a name
    e = roman_names.generate(5,includes=["ia#"])    # this gives 5 names suitable for ladies
"""

import pyglet
pyglet.resource.path = ['program/resources/names','resources/names'] #this works whether the program is launched from this file or the top level
from collections import defaultdict # creates dictionaries where entries are lists by default, so you can .append() to a new key and it will not give an error
import random



def weighted_choice(weights):
    "cribbed from http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/"
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i





            
class Model:
    "stores the training data and retrieves characters given parameters"
    def __init__(self,data,order,prior,alphabet):
        #print("creating model with order",order)
        self._observations = defaultdict(list) # so you can .append() to a new key and it begins a list there automatically
        self._chains = defaultdict(list)
        self._alphabet = alphabet
        while data:
            d = data.pop()
            d = ("#"*order) + d + "#"
            for i in range(len(d)-order):
                self._observations[ d[i:i+order] ].append( d[i+order] )
        for context in self._observations:
            for prediction in self._alphabet:
                self._chains[context].append(prior + self._observations[context].count(prediction))
    def get_chain(self,context):
        return self._chains.get(context,None)
    def draw_letter(self,context):
        weights = self.get_chain(context)
        if weights == None: return None
        else: return self._alphabet[weighted_choice(weights)]
        

        
class NameGenerator:
    "reads the text file, builds a set of models, and uses them to generate a name"
    def __init__(self,filename,order,prior=0.01):
        self._order = order
        self._names = set()
        datafile = pyglet.resource.file(filename,"r")
        for line in datafile:
            self._names.add( line.strip().lower() )
        
        # identify alphabet
        letters = set()
        for name in self._names:
            for letr in name:
                letters.add(letr)
        self._alphabet = "#"+"".join(sorted(letters))
        
        self._models = []
        for i in range(order)[::-1]:
            # build a list of models of decreasing order: e.g. a 3rd-order, 2nd-order, and 1st-order
            self._models.append(Model(self._names.copy(),i+1,prior,self._alphabet))
            
        del(self._names) # to save memory

    def get_next_letter(self,context):
        weights = None
        for m in self._models:
            #print("trying",context)
            l = m.draw_letter(context)
            if l == None: context = context[1:]
            else: break
        return l
    def generate_one(self):
        name = "#"*len(self._models)
        nextletter = self.get_next_letter(name[-self._order:])
        while not nextletter == "#":
            #print(nextletter)
            name += nextletter
            nextletter = self.get_next_letter(name[-self._order:])
        name += "#"
        return name        
    def generate_filtered(self,minlen,maxlen,includes,excludes):
        name_ok = False
        while not name_ok:
            name = self.generate_one()
            name_ok = True
            if len(name) < (minlen + self._order + 1):
                #print("too short")
                name_ok = False
            if len(name) > (maxlen + self._order + 1):
                #print("too long")
                name_ok = False
            for i in includes:
                if name.find(i) == -1:
                    #print(i,"not found")
                    name_ok = False
            for i in excludes:
                if not (name.find(i) == -1):
                    #print(i,"found")
                    name_ok = False
            #loop should end here if name_ok was not set to false
        name = name[self._order:-1] # strip the "#" characters
        return name        
    def generate(self,count,minlen=4,maxlen=9,includes=[],excludes=[]):
        names = []
        for c in range(count):
            names.append( self.generate_filtered(minlen,maxlen,includes,excludes) )
        if count == 1: names = names[0] # don't return a list if they only need a string
        return names    
        


if __name__ == "__main__":
    "UNIT TEST CODE"
    roman_names = NameGenerator( "roman.txt",order=3,prior=0.005 ) 
    #viking_names = NameGenerator( "vikings_male.txt",order=3,prior=0.01 ) 
    #viking_girls = NameGenerator( "vikings_female.txt",order=3,prior=0.01 ) 
    for x in range(10):
        print(roman_names.generate(1))
    print("")
    for x in range(10):
        print(roman_names.generate(1,includes=["ia#"]))
    #for x in range(10):
    #    print(viking_names.generate(1))
    #print("")
    #for x in range(10):
    #    print(viking_girls.generate(1))
