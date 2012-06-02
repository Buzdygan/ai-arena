import random
from itertools import product
from collections import defaultdict

MAX_SHIP_SIZE = 5
MIN_N = 12
MAX_N = 20
EMPTY = 0
OUT = -1

neighbours = [(-1,0), (1,0), (0,-1), (0,1)]

ships_types = dict()
ships_hps = dict()

ship_types_by_size = defaultdict(list)

class Ship:

    def __init__(self, number, stype, x, y):
        self.number = number
        self.stype = stype
        self.alive = True
        self.hp = ships_hps[stype]
        self.x = x
        self.y = y

class Board:

    def __init__(self, n, ships_number):
        r = range(-MAX_SHIP_SIZE, n + MAX_SHIP_SIZE)
        self.brd = dict([(pair, OUT) for pair in product(r,r)])
        for pair in product(range(1,n+1), range(1,n+1)):
            self.brd[pair] = EMPTY 

        self.n = n
        self.ships_number = ships_number
        self.alive_number = ships_number
        self.ships = dict()

    def put(self, x, y, v):
        if self.brd[(x,y)] != EMPTY:
            raise Exception("Field (%d,%d) is not empty!" % (x,y))
        for xn, yn in neighbours:
            if self.brd[(x+xn,y+yn)] > 0:
                raise Exception("Neighbour of field (%d,%d) is ocuppied!" % (x,y))

    def add_ship(self, ship):
        if ship.number > self.ships_number:
            raise Exception("Too many ships")
        self.ships[ship.number] = ship
        x = ship.x
        y = ship.y
        for dx, dy in ships_types[ship.stype]:
            self.put(x+dx, y+dy, ship.number)

    def shoot(self, x, y):
        if (x < 1) or (x > self.n) or (y < 1) or (y > self.n):
            raise Exception("Shot out of bounds!")
        if self.brd[(x,y)] > 0:
            number = self.brd[(x,y)]
            self.brd[(x,y)] = 0
            self.ships[number].hp -= 1
            if self.ships[number].hp == 0:
                self.ships[number].alive = False
                self.alive_number -= 1
            return number
        return -1

class Game:

    def __init__(self):
        self.n = random.choice(range(MIN_N, MAX_N+1))
        self.stypes = self.choose_ships()
        self.boards = [Board(self.n, len(self.stypes)), Board(self.n, len(self.stypes))]
        self.ships_nums = [0, 0]

    def choose_ships(self):
        stypes = list() 
        for i in range(1, MAX_SHIP_SIZE+1):
            for j in range(MAX_SHIP_SIZE - i + 1):
                stypes.append(random.choice(ship_types_by_size[i]))
        return stypes

    def place_ship(self, player, stype, x, y):
        self.ships_nums[player] += 1
        ship = Ship(self.ships_nums[player], stype, x, y)
        try:
            self.boards[player].add_ship(ship)
        except Exception as e:
            raise Exception(e.args[0], player)

    def shoot(self, player, x, y):
        try:
            return self.boards[player].shoot(x, y)
        except Exception as e:
            raise Exception(e.args[0], player)

try:
    game = Game()
    send_int(0, game.n)
    send_ships_types(0, game.stypes)
    send_int(1, game.n)
    send_ships_types(1, game.stypes)
    read_ships_positions(0, game)
    read_ships_positions(1, game)
except Exception as e:
    error_message = e.args[0]
    error_player  = e.args[1]
