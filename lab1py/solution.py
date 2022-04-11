import argparse
from sys import *
from math import inf
from operator import itemgetter
from bisect import insort

#probably missusing global variables
#but it's not my fault it's python's problem
s_dst:str = ""
h_dst:str = ""
states = {}
prijelazi = {}
state_heuristic = {}
pocetnoStanje:str = ""
ciljnaStanja = set()
def ucitajPrijelaze():
    global prijelazi
    global pocetnoStanje
    global ciljnaStanja
    with open(ss_dst) as file:
        line = file.readline()
        glupiBrojac = 0
        while line != "":
            line = line[:-1] #Discard \n at the end
            if (line[0]== '#'):
                line = file.readline()
                continue
            if glupiBrojac == 0:
                pocetnoStanje = line
                glupiBrojac += 1
                line = file.readline()
                continue
            elif glupiBrojac == 1:
                for stanje in line.split():
                    ciljnaStanja.add(stanje)
                glupiBrojac+=1
                line = file.readline()
                continue
            line = line.split()
            followerStates = line[1:]
            for i in range(len(followerStates)):
                tmp = followerStates[i].split(',')
                followerStates[i] = (tmp[0],int(tmp[1]))
            if line[0][-1] == ':':
                line[0] = line[0][:-1]
            prijelazi[line[0]] = followerStates
            line = file.readline()

def ucitajHeuristiku():
    global prijelazi
    global state_heuristic
    with open(h_dst) as file:
        line = file.readline()
        #print(states)
        while line != "":
            line = line[:-1] #Discard \n at the end
            if (line[0] == '#'):
                line = file.readline()
                continue
            line = line.split()
            state_key = line[0][:-1]
            try:
                    prijelazi[state_key]
            except(KeyError):
                    print("State \"%s\" does not exist, skipping", state_key)
            state_heuristic[state_key] = int(line[1])
            line = file.readline()

#vraca cijenu za put
#put je oblika lista stanja
def izracunajCijenu(put):
    global prijelazi
    cijena = 0
    for i in range(len(put)-1):
        for prijelaz in prijelazi[put[i]]:
            if prijelaz[0] == put[i+1]:
                cijena += prijelaz[1]
    return cijena


def bfs():
    global prijelazi
    global pocetnoStanje
    global ciljnaStanja
    #print(ciljnaStanja)
    #print("##############")
   # for ciljnoStanje in ciljnaStanja:
    queue = [(pocetnoStanje, 0,"")]
    queueDict = {pocetnoStanje:(0,"")}
    posjeceno = {}
    cijena = 0
    nadjeno = ""
    predenoStanja = 1
    put = []
    while queue != []:
        trenutnoStanje = queue.pop(0)
        try:
            queueDict[trenutnoStanje[0]]
        except(ValueError):
            continue
        except(KeyError):
            continue
        #print(trenutnoStanje)
        d = trenutnoStanje[1]
        posjeceno[trenutnoStanje[0]] = trenutnoStanje[1:]
        if trenutnoStanje[0] in ciljnaStanja:
            nadjeno = trenutnoStanje[0]
            break 
        expand = prijelazi[trenutnoStanje[0]].copy()
        #expand.sort(key=itemgetter(1))
        #print(posjeceno)
        #print(expand)
        #posQue = {**queueDict, **posjeceno} #nadam se da ovo nema pre veliku slozenost
        for elm1 in expand:
            elm1 = (elm1[0],d+1,trenutnoStanje[0])
            #print(elm1)
            app = True
            #stvorim set i iz njega brzo ocitam bez iteriranja
            elm2 = ""
            try:
                elm2 = queueDict[elm1[0]]
                if elm1[1] < elm2[0]:
                    queueDict.pop(elm1[0])
                else:
                    app = False
            except(KeyError):
                try:
                    elm2 = posjeceno[elm1[0]] 
                    if elm1[1] < elm2[0]:
                        posjeceno.pop(elm1[0])
                    else:
                        app = False
                except(KeyError):
                    pass
           #if not (elm1[:-1] in posjeceno[:-1]):
            if (app):
                queue.append(elm1) 
                queueDict[elm1[0]] = elm1[1:]
        #print(queue)
        #print()
        #print()
        predenoStanja +=1
    #Ovo mora biti najgori način moguči za za rekonustrukciju puta
    #print(posjeceno)
    
    while nadjeno != "":
        put.append(nadjeno)
        nadjeno = posjeceno[nadjeno][1]
    
    put.reverse()
    #ispis rijesenjai
    print("# BFS")
    print("[FOUND_SOLUTION]: yes")
    print("[STATES_VISITED]:",predenoStanja)
    print("[PATH_LENGTH]:",len(put))
    print("[TOTAL_COST]:", float(izracunajCijenu(put)))
    print("[PATH]:", end=" ")
    for i in range(len(put)):
        print(put[i],end="")
        if i != len(put)-1:
            print(" => ",end="")
    print()
            
def ucs(pocetnoStanje, verbose = True):
    global prijelazi
    global ciljnaStanja
    #print(ciljnaStanja)
    #print("##############")
    #for ciljnoStanje in ciljnaStanja:
    queue = [(pocetnoStanje, 0,"")]
    queueDict = {pocetnoStanje:(0,"")}
    posjeceno = {}
    predenoStanja = 1
    put = []
    nadjeno = ""
    while queue != []:
        trenutnoStanje = queue.pop(0)
        predenoStanja +=1
        try:
            queueDict[trenutnoStanje[0]]
            queueDict.pop(trenutnoStanje[0])
        except(ValueError):
            continue
        except(KeyError):
            continue
        posjeceno[trenutnoStanje[0]] = trenutnoStanje[1:]
        if trenutnoStanje[0] in ciljnaStanja:
            nadjeno = trenutnoStanje[0]    
            break
        expand = prijelazi[trenutnoStanje[0]].copy()
        for elm1 in expand:
            elm1 = (elm1[0],trenutnoStanje[1] + elm1[1],trenutnoStanje[0])
            app = True
            elm2 = ""
            try:
                elm2 = queueDict[elm1[0]]
                if elm1[1] < elm2[0]:
                    queueDict.pop(elm1[0])
                else:
                    app = False
            except(KeyError):
                try:
                    elm2 = posjeceno[elm1[0]] 
                    if elm1[1] < elm2[0]:
                        posjeceno.pop(elm1[0])
                    else:
                        app = False
                except(KeyError):
                    pass
            if (app):
                insort(queue,elm1,key=itemgetter(1))
                queueDict[elm1[0]] = elm1[1:]
    #Ovo mora biti najgori način moguči za za rekonustrukciju puta
    cijena = posjeceno[nadjeno][0]
    while nadjeno != "":
        put.append(nadjeno)
        nadjeno = posjeceno[nadjeno][1]
    put.reverse()
    #cijena = izracunajCijenu(posjeceno)
    if (verbose):
        print("# UCS")
        print("[FOUND_SOLUTION]: yes")
        print("[STATES_VISITED]:",predenoStanja)
        print("[PATH_LENGTH]:",len(posjeceno))
        print("[TOTAL_COST]:", float(cijena))
        print("[PATH]:", end=" ")
        for i in range(len(put)):
            print(put[i],end="")
            if i != len(put)-1:
                print(" => ",end="")
    return cijena 

def astar():
    global s_dst
    global prijelazi
    global state_heuristic
    global pocetnoStanje
    global ciljnaStanja
    queue = [(pocetnoStanje,state_heuristic[pocetnoStanje],0,"")]
    queueDict = {pocetnoStanje:(state_heuristic[pocetnoStanje],0,"")}
    posjeceno = {}
    cijena = 0
    predenoStanja = 1
    put = []
    nadjeno = ""
    while queue != []:
        trenutnoStanje = queue.pop(0)
        try:
            queueDict[trenutnoStanje[0]]
            queueDict.pop(trenutnoStanje[0])
        except(ValueError):
            continue
        except(KeyError):
            continue
        posjeceno[trenutnoStanje[0]] = trenutnoStanje[1:]
        
        predenoStanja+=1
        if trenutnoStanje[0] in ciljnaStanja:
            nadjeno = trenutnoStanje[0]
            break
        expand = prijelazi[trenutnoStanje[0]].copy()
        for elm in expand:
            #print(elm)
            elm1 = (elm[0],state_heuristic[elm[0]],trenutnoStanje[2]+elm[1],trenutnoStanje[0])
            app = True
            elm2 = ""
            try:
                elm2 = queueDict[elm1[0]]
                if elm1[2] < elm2[1]:
                    queueDict.pop(elm1[0])
                else:
                    app = False
            except(KeyError):
                try:
                    elm2 = posjeceno[elm1[0]] 
                    if elm1[2] < elm2[1]:
                        posjeceno.pop(elm1[0])
                    else:
                        app = False
                except(KeyError):
                    pass
            if (app):
                insort(queue,elm1,key= lambda stat: stat[1]+stat[2])
                queueDict[elm1[0]] = elm1[1:]
    cijena = posjeceno[nadjeno][1]
    while nadjeno != "":
        put.append(nadjeno)
        nadjeno = posjeceno[nadjeno][2]
 
    put.reverse() 
    print("# A-STAR ", s_dst)
    print("[FOUND_SOLUTION]: yes")
    print("[STATES_VISITED]:",predenoStanja)
    print("[PATH_LENGTH]:",len(put))
    print("[TOTAL_COST]:", float(cijena))
    print("[PATH]:", end=" ")
    for i in range(len(put)):
        print(put[i],end="")
        if i != len(put)-1:
            print(" => ",end="")

def checkOptimistic():
    global h_dst
    print("# HEURISTIC-OPTIMISTIC ",h_dst)
    global state_heuristic
    optimistic = True
    for state in state_heuristic:
        cijena = ucs(state, verbose = False)
        print("[CONDITION]: ",end="")
        if state_heuristic[state] <= cijena:
            print("[OK] h("+str(state)+") <= h*: "+str(float(state_heuristic[state]))+" <= "+ str(float(cijena)))
        else:
            optimistic = False
            print("[ERR] h("+str(state)+") <= h*: "+str(float(state_heuristic[state]))+" <= "+ str(float(cijena)))
    if optimistic:
        print("[CONCLUSION]: Heuristic is optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is not optimistic.")

def checkConsistent():
    global state_heuristic
    global prijelazi
    global h_dst
    print("# HEURISTIC-CONSISTENT", h_dst)
    consistent = True
    for prijelaz in prijelazi:
        for succ in prijelazi[prijelaz]:
            if state_heuristic[succ[0]] +succ[1] >= state_heuristic[prijelaz]:
                print("[CONDITION]: [OK] h("+str(prijelaz)+") <= h("+str(succ[0])+") + c: "+str(float(state_heuristic[prijelaz]))+" <= "+str(float(state_heuristic[succ[0]]))+ " + "+str(float(succ[1])))
            else:
                print("[CONDITION]: [ERR] h("+str(prijelaz)+") <= h("+str(succ[0])+") + c: "+str(float(state_heuristic[prijelaz]))+" <= "+str(float(state_heuristic[succ[0]]))+ " + "+str(float(succ[1])))
                consistent = False
    if (consistent):
        print("[CONCLUSION]: Heuristic is consistent.")
    else:
        print("[CONCLUSION]: Heuristic is not consistent.")
def main():
    global ss_dst
    global h_dst
    global pocetnoStanje
    parser = argparse.ArgumentParser(description="Parse different argument types")
    parser.add_argument('--alg') #algoritam
    parser.add_argument('--ss')  #stanja za stanja
    parser.add_argument('--h')   #stanja za heuristiku
    parser.add_argument('--check-optimistic',  action='store_true') 
    parser.add_argument('--check-consistent',  action='store_true')
    opcije = parser.parse_args()

    #Ucitaj datoteke
    ss_dst = opcije.ss
    h_dst = opcije.h
    if (ss_dst == None):
        print("Requiere path for state file")
        return
    ucitajPrijelaze()
    if (h_dst != None):
        ucitajHeuristiku()
    if (opcije.alg == None):
        opcije.alg = ""
    
    if(opcije.alg.lower() == 'astar'):
        astar()
    elif(opcije.alg.lower() == 'ucs'):
        ucs(pocetnoStanje)
    elif (opcije.alg.lower() == 'bfs'):
        bfs()
    if (opcije.check_optimistic):
        checkOptimistic()
    if (opcije.check_consistent):
        checkConsistent()
if __name__ == '__main__':
    main()
