#!/usr/bin/env python

import sys
import copy

def log(mes):
    sys.stderr.write(mes)
    sys.stderr.flush()

def send(mes):
    sys.stdout.write(mes)
    sys.stdout.flush()

def recv_mes():
    try:
        m = sys.stdin.readline()
        if (m == "OK\n"):
            return m
        mr = map(lambda x: int(x), m[1:-2].split(','))
        return mr
    except:
        return []

LEN = 11
WID = 9

visited = set()
unused_edges = set()
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

def main():
    
    global visited
    global unused_edges
    global current

    points_1 = 0;
    points_2 = 0;

    for game_num in range(4):
        
        log("INIT")
        init()

        bad_1 = False
        bad_2 = False

        send("[1,2]INIT\n")
        ok = recv_mes()
        if (ok != "OK\n"):
            bad_1 = True
            #log("Not OK 1\n")
        else:
            pass
            #log("OK 1\n")
        ok = recv_mes()
        if (ok != "OK\n"):
            bad_2 = True
            #log("Not OK 2\n")
        else:
            pass
            #log("OK 2\n")

        if (bad_1 and bad_2):
            continue
        elif (bad_1):
            points_2 += 1
            continue
        elif (bad_2):
            points_1 += 1
            continue

        send("[{0}]UP\n".format(1 + (game_num % 2)))
        ok = recv_mes()
        if (ok != "OK\n"):
            points_1 += (game_num % 2)
            points_2 += 1 - (game_num % 2)
            continue
        send("[{0}]DOWN\n".format(2 - (game_num % 2)))
        ok = recv_mes()
        if (ok != "OK\n"):
            points_1 += 1 - (game_num % 2)
            points_2 += (game_num % 2)
        moving = 1 + (game_num % 2)

        send("[{0}]MOVE []\n".format(moving))
        
        while(True):
            move = recv_mes()
            move_copy = copy.deepcopy(move)
            
            log("{0}\n".format(len(move)))

            end_game = True
            bad_move = True

            who_won = 0
            while (move != []):
                n = move[0]
                del move[0]
                if ((current[0], current[1], n) in unused_edges):
                    unused_edges.remove((current[0], current[1], n))
                    newx = current[0]
                    newy = current[1]
                    if (n in [7,0,1]):
                        newy += 1
                    if (n in [1,2,3]):
                        newx += 1
                    if (n in [3,4,5]):
                        newy -= 1
                    if (n in [5,6,7]):
                        newx -= 1
                    current = (newx, newy)
                    unused_edges.remove((current[0], current[1], ((n+4)%8)))
                else:
                    log("Tried to use used edge {0} , {1}\n".format(current, n))
                    log
                    break
                if (current in set([(a,b) for a in [3,4,5] for b in [-1,11]])):
                    log("Goal!\n")
                    bad_move = False
                    break
                if (current in visited) and (move == []):
                    log("Shouldn't stop\n")
                    break
                elif (current not in visited) and (move != []):
                    log("Should have stopped\n")
                    break
                elif (current in visited) and (move != []):
                    continue
                elif (current not in visited) and (move == []):
                    visited.add(current)
                    end_game = False
                    bad_move = False
                    break

            if (end_game):    
                log("End game\n")
                if (bad_move):
                    log("Bad move\n")
                    points_1 += (moving-1)
                    points_2 += (2-moving)
                else:
                    log("Goal!\n")
                    s = int((current == (4,0)) ^ ((game_num % 2) == 0))
                    points_1 += s
                    points_2 += (1 - s)
                break
            else:
                moving = 3 - moving
                send("[{0}]MOVE {1}\n".format(moving, move_copy))
                #log("Sent [{0}]MOVE {1}\n".format(moving, move_copy))
                #log("{0}".format(current))

    send("[0]END\n")
    send("[{0}, {1}]\n".format(points_1, points_2))

main()
