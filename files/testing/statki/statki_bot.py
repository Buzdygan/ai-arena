import sys
from itertools import product

received = []

def read_int():
    global received
    if received:
        return received.pop(0)
    m = sys.stdin.readline()
    received = map(lambda x: int(x), m.split(' '))
    print(received)
    return received.pop(0) 

def send_int(a):
    sys.stdout.write('%d ' % a)
    sys.stdout.flush()


def play_round():
    n = read_int()
    ships_number = read_int()
    ship_types = []
    for i in range(ships_number):
        stype = read_int()
        ship_types.append(stype)

    x = 4
    y = 2
    for stype in ship_types:
        send_int(stype)
        send_int(x)
        send_int(y)
        x += 4
        if x > n:
            x = 4
            y += 4

    all_fields = product(range(1, n+1), range(1, n+1))
    for x, y in all_fields:
        send_int(x)
        send_int(y)
        target = read_int()
        if target < 0:
            if target == -1:
                return 1
            if target == -2:
                return -1
            if target == -3:
                return 0
        dead = read_int()
    return 0


def play():
    score = 0
    while True:
        score += play_round()

play()
