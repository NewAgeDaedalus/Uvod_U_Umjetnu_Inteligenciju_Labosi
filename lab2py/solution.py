from sys import argv
class Literal:
    def __init__(self, znak:str):
        #sljivis defenzivno programiranje!!!
        if znak[0] == '~':
            self.negacija = True
            self.znak = znak[1:].lower()
        else:
            self.negacija = False
            self.znak = znak.lower()
    def __eq__(self, other):
        if self.znak == other.znak and other.negacija == self.negacija:
            return True
        return False
    def __lt__(self, other):
        if self.znak < other.znak:
            return True
        return False
    def __str__(self):
        if self.negacija:
            return '~' + self.znak
        return self.znak
    def isKomplement(self, other):
        if self.znak == other.znak and self.negacija != other.negacija:
            return True 
        return False

#Ucitava iz teksturalne datoteke "path"
#i vraca listu klauzula
def ucitajKlazule(path:str):
    klauzule = []
    origin = ""
    with open(path, "r") as file:
        line = file.readline()[:-1].lower()
        while line != "":
            if line[0] == '#':
                continue
            klauzula = []
            origin = line 
            lit = line.split(' v ')
            for l in lit:
                klauzula.append(Literal(l))
            klauzule.append(klauzula.copy())
            line = file.readline()
            line = line[:-1].lower()  #makni \n
    return klauzule[:-1], klauzule[-1], origin # vrati F i G

def loadCommands(path:str):
    commands = []
    with open(path, 'r') as file:
        line = file.readline()[:-1].lower()
        while line != "":
            if line[0] == '#':
                continue
            klauzula = []
            lit = line.split(' v ')
            for l in lit:
                klauzula.append(Literal(l))
            command = klauzula[-1].znak[-1]
            klauzula[-1].znak = klauzula[-1].znak[:-2]
            commands.append((klauzula.copy(), command))
            line = file.readline()
            line = line[:-1].lower()  #makni \n
    return commands


#samo negira formule koje su u CNF obliku
#i zato je negacija rastav klauzulu na vise klauzula
#tocnije na n klauzala gdje je n broj literala formule
def negirajFormulu(formula):
    for lit in formula:
        lit.negacija = not lit.negacija
    tmp =   list(map(lambda i: [i], formula))
    return tmp, len(tmp) 

def factorize(mogucaResolucija):
    #mrzim python ne mogu i manipulirati D:
    tmp = mogucaResolucija.copy()
    for i in range(len(mogucaResolucija)):
        for j in range(i+1,len(mogucaResolucija)):
            if mogucaResolucija[i] == mogucaResolucija[j]:
                tmp.remove(mogucaResolucija[j])
    return tmp 

def jeTautologija(res):
    for i in range(len(res)):
        for j in range(i+1, len(res)):
            if res[i].isKomplement(res[j]):
                return True
    return False

#Vraca listu svih mogučih resolucija
def resolve(pair):
    moguceResolucije = []
    #OVO NIKAD NE PROLAZI
    if len(pair[0]) == len(pair[1]) == 1 and pair[0][0].isKomplement(pair[1][0]):
        return ["NIL"]
    #i i j su objekti klase Literal
    for i in pair[0]:
        for j in pair[1]:
            #print(i, j)
            if i.isKomplement(j):
                tmp0 =  pair[0].copy()
                tmp0.remove(i)
                tmp1 =  pair[1].copy()
                tmp1.remove(j)
                mogucaResolucija = tmp0 + tmp1 
                mogucaResolucija = factorize(mogucaResolucija)
                if jeTautologija(mogucaResolucija):
                    continue
                moguceResolucije.append(mogucaResolucija)
    return moguceResolucije

#Racuna sve moguce parove jedne liste. Vraca listu dvojki parova.
#neefikasno koristim memoriju ali to je python
def selectClauses(klauzule:list, depth:int):
    allPairs = []
    for i in range(len(klauzule)-1, depth-1,-1):
        for j in  range(i-1, -1,-1 ):
            allPairs.append((klauzule[i],klauzule[j],(i+1,j+1)))
    return allPairs

def printKlauz(klaus, numb):
    print(numb,". ", end ="", sep ="")
    klauz = []
    if isinstance(klaus, tuple):
        klauz = klaus[0]
    else:
        klauz = klaus
    for i in range(len(klauz)):
        print(klauz[i], end="", sep = "")
        if i != len(klauz) -1:
            print(" v ", end = "") 
    if isinstance(klaus, tuple):
        print(" (",klaus[1],", ",klaus[2], ")", end = "", sep = "")
    print()

def inKlauzule(klauzule:list, new:list):
    res = True 
    newNew = []
    for klaus  in new:
        if klaus not in klauzule:
            newNew.append(klaus)
            res = False
    return res, newNew

def clausToString(klauzla:list):
    res = ""
    for i in range(len(klauzla)):
        res += klauzla[i].znak
        if i != len(klauzla)-1:
            res += " v "
    return res

def printKlauzPath(kIndex1, kIndex2, sastav:dict, klauzule:list):
    path = [kIndex1-1, kIndex2-1]
    kIndex = path[0]
    i = 0
    while True:
        tmp = []
        if sastav[str(klauzule[kIndex])] == -1:
            i+=1
            if i >= len(path):
                break
            kIndex=path[i]
            continue
        tmp += list(map(lambda i: i-1,sastav[str(klauzule[kIndex])]))
        path += tmp
        i+=1
        if i >= len(path):
            break
        kIndex=path[i]
    #print(path)
    path = set(path)
    path = list(path)
    path.sort()
    #print(path)
    for index in path:
        if sastav[str(klauzule[index])] == -1:
            continue
        printKlauz((klauzule[index], sastav[str(klauzule[index])][0], sastav[str(klauzule[index])][1]), index+1)

#Koristim bolju strategiju ali jos ne optimalnu
#Pamtim klauzule koje sam vec ranije nasao
#Ne kombiniram klauzule koje sam jednom vec kombinirao
def resolute(klauzule, ciljnaKlaula, cilj): 
    knownClauses = {}
    print("Time to resolute!") 
    new = [] 
    new, negLen = negirajFormulu(ciljnaKlaula) 
    klauzule += new
    for i in range(1, len(klauzule)+1):
        klauzule[i-1].sort()
        knownClauses[str(klauzule[i-1])] = -1
    new = []
    depth = len(klauzule) - negLen 
    end = False 
    for i in range(len(klauzule)): 
        printKlauz(klauzule[i],i+1) 
    print("=================") 
    while not end: 
        br = 1 
        sasTmp = []
        for par in selectClauses(klauzule, depth):
            resolvents = resolve(par[:2])
            for res in resolvents:
                # jako intuitivno i totalno necu zaboraviti sta sam tu radio.
                # par je tuple oblika (klauz1,klauz2, (pos1, pos2)), glupo
                # ali neda mi se sada refaktorirati kod
                if res == "NIL":
                    printKlauzPath(par[2][0],par[2][1], knownClauses, klauzule)
                    print("NIL (",par[2][0],", ",par[2][1],")", sep= "")
                    end = True
                    break
                else:
                    #printKlauz((res,par[2][0],par[2][1]),len(klauzule)+br)
                    sasTmp.append(par[2])
                    br+=1
            if not end:
                new += resolvents 
            else:
                break
        #if len(klauzule) >=  15:
        #    break
        podskup = True
        depth = len(klauzule) 
        br = 0
        for klauz in new:
            try:
                klauz.sort()
                knownClauses[str((klauz))]
            except(KeyError):
                podskup = False
                klauzule.append(klauz)
                knownClauses[str(klauz)]= sasTmp[br] 
            br+=1
        new = []
        if podskup and not end:
            print("[CONCLUSION]:",cilj,end = " ")
            print("is unknown")       
            exit()
    print("[CONCLUSION]:",cilj, end = " ")
    print("is true")

def cook(knowledge:list, commands:list):
    print("MMmmmmm so good cooking!!")
    for command in commands:
        if command[1] == '+':
            command[0].sort()
            contains = False
            for claus in knowledge:
                claus.sort()
                if command[0] == claus:
                    contains = True
            if not contains:
                knowledge.append(command[0])
        elif command[1] == '-':
            command[0].sort()
            for claus in knowledge:
                claus.sort()
                if command[0] == claus:
                    knowledge.remove(claus)
        elif command[1] == '?':
            resolute(knowledge.copy(), command[0].copy(), clausToString(command[0]))
            

def main():
    command = argv[1]
    klauzule = [] #lista klauzula npr [["a","~b","c"], ["a", "~c"]]
    if (command == "resolution"):
        klauzule, ciljnaKlauzula, cilj = ucitajKlazule(argv[2])
        resolute(klauzule, ciljnaKlauzula, cilj)
    elif (command == "cooking"):
        #Funky stuff 
        knowledge, smece1, smece2= ucitajKlazule(argv[2])
        knowledge.append(smece1)
        commands = []
        try:
            commands = loadCommands(argv[3])
        except(IndexError):
            exit("No command file given")
        cook(knowledge,commands)
    else:
        print("Command: \"",argv[2],"\" does not exist.\nValid commands are \"resolution\" or \"cook\"")

if __name__ == '__main__':
    main()
