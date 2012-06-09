#!/usr/bin/env python

import sys
import random

def log(log):
    sys.stderr.write(log)
    sys.stderr.flush()

def send(mes):
    sys.stdout.write(mes)
    sys.stdout.flush()

def recv_mes():
    try:
        m = sys.stdin.readline()
        return m
    except:
        return []

LEN = 11
WID = 9

visited = set()
unused_edges = set()
direction = 0
current = (0,0)

def init():
    
    global visited
    global unused_edges
    global current

    visited = set((4,5))
    visited.update([(a,b) for a in [0,8] for b in range(0,11)])
    visited.update([(a,b) for a in range(1,8) for b in [0,10]])
    visited.remove((4,0))
    visited.remove((4,10))

    current = (4,5)

    unused_edges = set([(a,b,c) for a in range(1,8) for b in range(1,10) for c in range(0,8)])
    unused_edges.update(set([(0,b,c) for b in range(1,10) for c in [1,2,3]]))
    unused_edges.update(set([(8,b,c) for b in range(1,10) for c in [5,6,7]]))
    unused_edges.update(set([(a,0,c) for a in range(1,8) for c in [7,0,1]]))
    unused_edges.update(set([(a,10,c) for a in range(1,8) for c in [3,4,5]]))
    unused_edges.add((0,0,1))
    unused_edges.add((8,0,7))
    unused_edges.add((0,10,3))
    unused_edges.add((8,10,5))
    unused_edges.add((3,0,3))
    unused_edges.update([(4,0,c) for c in [3,4,5]])
    unused_edges.add((5,0,5))
    unused_edges.add((3,10,1))
    unused_edges.update([(4,10,c) for c in [7,0,1]])
    unused_edges.add((5,10,7))
    unused_edges.update([(4,11,a) for a in [3,4,5]])
    unused_edges.add((3,11,3))
    unused_edges.add((5,11,5))
    unused_edges.update([(4,-1,a) for a in [7,0,1]])
    unused_edges.add((3,-1,1))
    unused_edges.add((5,-1,7))

def simulate(ml):

    global current
    global unused_edges
    global visited

    while(ml != []):
        d = ml[0]
        del ml[0]
        
        unused_edges.remove((current[0], current[1], d))
        
        newx = current[0]
        newy = current[1]
        
        if (d in [7,0,1]):
            newy += 1
        if (d in [1,2,3]):
            newx += 1
        if (d in [3,4,5]):
            newy -= 1
        if (d in [5,6,7]):
            newx -= 1
        
        current = (newx,newy)
        unused_edges.remove((current[0], current[1], ((d+4)%8)))
        visited.add(current)
        #log("Simulated {0}".format(current))

def move():
     
    ms = []

    global current
    global unused_edges
    global visited

    while(True):
        d = -1
        untried = set(range(-1,8,1))
        while ((current[0], current[1], d) not in unused_edges):
            untried.remove(d)
            if (list(untried) == []):
                d = -1
                break
            else:
                d = random.choice(list(untried))
        ms.append(d)
        if (d == -1):
            log("Blocked :( \n")
            break
        unused_edges.remove((current[0], current[1], d))
        newx = current[0]
        newy = current[1]
        if (d in [7,0,1]):
            newy += 1
        if (d in [1,2,3]):
            newx += 1
        if (d in [3,4,5]):
            newy -= 1
        if (d in [5,6,7]):
            newx -= 1
        current = (newx,newy)
        unused_edges.remove((current[0], current[1], ((d+4)%8)))
        if (current not in visited):
            visited.add(current)
            break

    send("{0}\n".format(ms))

def main():
    
    global visited
    global unused_edges
    global direction

    while(True):

        mes = recv_mes()
        
        if (mes[0:4] == "INIT"):
            #log("Got init!\n")
            init()
            send("OK\n")
            #log("Sent OK\n")
            mes_dir = recv_mes()
            if mes_dir == "UP\n":
                direction = 'UP'
            else:
                direction = 'DOWN'
            send("OK\n")
        elif (mes == "\n"):
            pass
        elif (mes[0:4] == "MOVE"):
            ms = mes.split()
            if (ms[1] == "[]"):
                move()
            else:
                ml = map(int, (ms[1][1:-1]).split(','))
                simulate(ml)
                move()
main()
