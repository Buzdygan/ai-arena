import random
from itertools import product
from collections import defaultdict

CLASHES_NUMBER = 40
MAX_ROUNDS_NUMBER = 1000
MAX_SHIP_SIZE = 5
MIN_N = 12
MAX_N = 20
EMPTY = 0
OUT = -1
MISS = -1

DRAW = 2

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
            return number, int(not self.ships[number].alive)
        return MISS 

class Game:

    def __init__(self):
        self.n = random.choice(range(MIN_N, MAX_N+1))
        self.stypes = self.choose_ships()
        self.boards = [Board(self.n, len(self.stypes)), Board(self.n, len(self.stypes))]
        self.ships_nums = [0, 0]
        self.players_ships = [[], []]

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
            self.players_ships[player].append(ship)
            self.boards[player].add_ship(ship)

        except Exception as e:
            raise Exception(e.args[0], player)

    def shoot(self, player, x, y):
        try:
            number, dead = self.boards[player].shoot(x, y)
            if dead:
                self.ships_nums[player] -= 1
            if number == MISS:
                return MISS, dead
            else:
                return self.players_ships[player][number-1].stype, dead
        except Exception as e:
            raise Exception(e.args[0], player)

    def game_over(self):
        if self.ships_nums[0] <= 0:
            return 1
        if self.ships_nums[1] <= 0:
            return 0
        return -1



def opponent(x):
    return (x+1) % 2

################  TODO ###################
# Wypełnić poniższe funkcje

def send_int(player_number, a):
    pass

def send_int_list(player_number, intlist):
    """
        At beggining we should send number of ints to be sent
    """
    pass

def read_ship_position(player):
    """
        Returns ship_type, x, y
    """
    return 0,0,0

def read_shot(player):
    """
        Returns x, y of player's shot
    """
    return 0,0

def end_game(scores):
    """
        scores[i] - number of clashes won by i
        scores[2] - number of draws
    """
    pass

def end_error(error_player, error_message):
    """
        error_player did error with error_message
    """
    pass


################ Koniec TODO ###################


def send_ships_types(player, stypes):
    send_int_list(player, stypes)

def read_ships_positions(player, game):
    ships_number = len(game.stypes)
    for i in range(ships_number):
        stype, x, y = read_ship_position(player)
        game.place_ship(player, stype, x, y)


def play_one(start_player):
    game = Game()
    send_int(0, game.n)
    send_ships_types(0, game.stypes)
    send_int(1, game.n)
    send_ships_types(1, game.stypes)
    read_ships_positions(0, game)
    read_ships_positions(1, game)
    player = start_player 
    for i in range(MAX_ROUNDS_NUMBER):
        # player 0 shoots
        x, y = read_shot(player)
        stype, dead = game.shoot(opponent(player), x, y)
        send_int(player, stype)
        send_int(player, dead)
        game_res = game.game_over() 
        if game_res != -1:
            return game_res
        player = opponent(player)
    return DRAW


def play():
    try:
        scores = [0, 0, 0]
        start_player = 0
        for i in range(CLASHES_NUMBER):
            scores[play_one(start_player)] += 1
            start_player = opponent(start_player)
        end_game(scores)
    except Exception as e:
        error_message = e.args[0]
        error_player  = e.args[1]
        end_error(error_player, error_message)


