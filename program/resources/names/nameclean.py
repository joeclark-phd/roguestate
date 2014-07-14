

F = open("romanraw.txt","r")
O = open("roman.txt","w")

for line in F:
    name = line.strip()
    if len(name)==0 or name[0]=="-": pass
    else: O.write(name+"\n")