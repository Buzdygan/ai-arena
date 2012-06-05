#!/usr/bin/env python

import sys

def log(mes):
    sys.stderr.write(mes)
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

def main():
    
    global visited
    global unused_edges

    points_1 = 0;
    points_2 = 0;

    log('log1\n')

    for game_num in range(4):
        
        init()
        
        send("[0] INIT\n")
        ok = recv_mes()
        if (ok != "OK\n"):
            points_2 += 1
            continue
        ok = recv_mes()
        if (ok != "OK\n"):
            points_1 += 1
            continue
        send("[{0}] UP\n".format(1 + (game_num % 2)))
        ok = recv_mes()
        if (ok != "OK\n"):
            points_1 += (game_num % 2)
            points_2 += 1 - (game_num % 2)
            continue
        send("[{0}] DOWN\n".format(2 - (game_num % 2)))
        ok = recv_mes()
        if (ok != "OK\n"):
            points_1 += 1 - (game_num % 2)
            points_2 += (game_num % 2)
        moving = 1 + (game_num % 2)

        while(True):
            send("[{0}] MOVE []\n".format(moving))
            move = recv_mes()
            move_copy = move

            end_game = True
            bad_move = True

            who_won = 0
            while (move != []):
                n = move[0]
                del move[0]
                if ((current[0], current[1], n) in unused_edges):
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
                else:
                    break
                if (current == (4,0) or current == (4, 10)):
                    bad_move = False
                    break
                if (current in visited) and (move == []):
                    break
                elif (current not in visited) and (move != []):
                    break
                elif (current in visited) and (move != []):
                    continue
                elif (current not in visited) and (move == []):
                    end_game = False
                    bad_move = False
                    break

            if (end_game):    
                if (bad_move):
                    points_1 += (moving-1)
                    points_2 += (2-moving)
                else:
                    s = int((current == (4,0)) ^ ((game_num % 2) == 0))
                    points_1 += s
                    points_2 += (1 - s)
                break
            else:
                moving = 3 - moving
                send("[{0}] MOVE {1}\n".format(moving, move_copy))

    send("[0] END\n")
    send("[{0}, {1}]\n".format(points_1, points_2))

main()
