#!/usr/bin/env python

import sys

def log(log):
    sys.stderr.write(log)
    sys.stderr.flush()

def send(mes):
    sys.stdout.write(mes)
    sys.stdout.flush()

def recv_mes():
    try:
        m = sys.stdin.readline()
        mr = map(lambda x: int(x), m.split(','))
        return mr
    except:
        return []

LEN = 11
WID = 9

visited = set()
unused_edges = set()
direction = 0

def init():
    
    global visited
    global unused_edges

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
        elif (d in [1,2,3]):
            newx += 1
        elif (d in [3,4,5]):
            newy -= 1
        elif (d in [5,6,7]):
            newx -= 1
        
        current = (newx,newy)
        visited.add(current)

def move():
    
    ms = []

    while(True):
        d = -1
        while ((current[0], current[1], d) not in unused_edges):
            d = random.choice(range(8))
        ms.append(d)
        unused_edges.remove((current[0], current[1], d))
        newx = current[0]
        newy = current[1]
        if (d in [7,0,1]):
            newy += 1
        elif (d in [1,2,3]):
            newx += 1
        elif (d in [3,4,5]):
            newy -= 1
        elif (d in [5,6,7]):
            newx -= 1
        current = (newx,newy)
        if (current not in visited):
            break

    send("{0}".format(ms))

def main():
    
    global visited
    global unused_edges
    global direction

    while(True):

        mes = recv_mes()
        
        if (mes[0:4] == "INIT"):
            init()
            send("OK\n")
            mes_dir = recv_mes()
            if mes_dir == "UP\n":
                direction = 'UP'
            else:
                direction = 'DOWN'
        elif (mes[0:4] == "MOVE"):
           ms = mes.split()
           ml = map(int, (ms[1][1:-1]).split(','))
           simulate(ml)
           move()

main()
