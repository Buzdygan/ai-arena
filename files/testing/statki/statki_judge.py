import random
from itertools import product
from collections import defaultdict
from sys import stdin, stdout, stderr

CLASHES_NUMBER = 50 
MAX_ROUNDS_NUMBER = 1000 
MAX_SHIP_SIZE = 2
MIN_N = 12
MAX_N = 20
EMPTY = 0
OUT = -1
MISS = 0 
WINNER_RESULT = -1
LOSER_RESULT = -2
DRAW_RESULT = -3

DRAW = 3
AVAILABLE_TYPES = range(1, 12)

neighbours = [(-1,0), (1,0), (0,-1), (0,1)]

ships_types = dict()

ship_types_by_size = defaultdict(list)

def prepare_ships():

    # horizontal lines 
    ships_types[1] = [(-1,0), (0,0)]
    ships_types[2] = [(-2, 0), (-1,0), (0,0)]
    ships_types[3] = [(-3, 0), (-2, 0), (-1,0), (0,0)]
    ships_types[4] = [(-4, 0), (-3, 0), (-2, 0), (-1,0), (0,0)]

    # vertical lines 
    for i in range(1, 5):
        ships_types[i + 4] = [(y, x) for x,y in ships_types[i]]

    # cross 
    ships_types[9] = [(0,0), (-1, 0), (-2, 0), (-1, -1), (-1, 1)] 

    # boat
    ships_types[10] = [(0,0), (0, -1), (-1, -1), (-2, -1), (-2, 0)]

    # reversed boat
    ships_types[11] = [(0,0), (0, -1), (-1, 0), (-2, -1), (-2, 0)]

    for stype, ship_fields in ships_types.items():
        ship_types_by_size[len(ship_fields)].append(stype)

class GameException(Exception):
    pass

class Ship:

    def __init__(self, number, stype, x, y):
        self.number = number
        self.stype = stype
        self.alive = True
        self.hp = len(ships_types[stype])
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
            raise GameException("Field (%d,%d) is not empty!" % (x,y))
        for xn, yn in neighbours:
            if self.brd[(x+xn,y+yn)] > 0 and self.brd[(x+xn, y+yn)] != v:
                raise GameException("Neighbour of field (%d,%d) is ocuppied!" % (x,y))
        self.brd[(x,y)] = v

    def add_ship(self, ship):
        if ship.number > self.ships_number:
            raise GameException("Too many ships")
        self.ships[ship.number] = ship
        x = ship.x
        y = ship.y
        for dx, dy in ships_types[ship.stype]:
            self.put(x+dx, y+dy, ship.number)

    def shoot(self, x, y):
        if (x < 1) or (x > self.n) or (y < 1) or (y > self.n):
            raise GameException("Shot out of bounds!")
        if self.brd[(x,y)] > 0:
            number = self.brd[(x,y)]
            self.brd[(x,y)] = 0
            self.ships[number].hp -= 1
            if self.ships[number].hp == 0:
                self.ships[number].alive = False
                self.alive_number -= 1
            return number, int(not self.ships[number].alive)
        return MISS, 0 

class Game:

    def __init__(self):
        self.n = random.choice(range(MIN_N, MAX_N+1))
        self.stypes = self.choose_ships()
        self.boards = [None, Board(self.n, len(self.stypes)), Board(self.n, len(self.stypes))]
        self.ships_nums = [0, 0, 0]
        self.players_ships = [[], [], []]

    def choose_ships(self):
        stypes = list() 
        for i in range(2, MAX_SHIP_SIZE+1):
            for j in range(MAX_SHIP_SIZE - i + 1):
                stypes.append(random.choice(ship_types_by_size[i]))
        return stypes

    def place_ship(self, player, stype, x, y):
        try:
            if stype not in AVAILABLE_TYPES:
                raise GameException("Wrong ship type")
            self.ships_nums[player] += 1
            ship = Ship(self.ships_nums[player], stype, x, y)
            self.players_ships[player].append(ship)
            self.boards[player].add_ship(ship)
            if len(self.players_ships[player]) == len(self.stypes):
                player_ships_types = set([ship.stype for ship in self.players_ships[player]])
                if set(self.stypes) != player_ships_types:
                    raise GameException("Wrong set of ships given")

        except GameException as e:
            raise GameException(e.args[0], player)

    def shoot(self, player, x, y):
        try:
            number, dead = self.boards[player].shoot(x, y)
            if dead:
                self.ships_nums[player] -= 1
            if number == MISS:
                return MISS, dead
            else:
                return self.players_ships[player][number-1].stype, dead
        except GameException as e:
            raise GameException(e.args[0], player)

    def game_over(self):
        if self.ships_nums[1] <= 0:
            return 2
        if self.ships_nums[2] <= 0:
            return 1
        return -1



def opponent(x):
    return 3 - x 

################ Communication ###################

received_ints = [[], [], []]
ints_to_send = [[], [], []]

def to_send(player_number, i):
    global ints_to_send
    ints_to_send[player_number].append(i)

def send(player_number):
    global received_ints
    global ints_to_send
    mes = ""
    for index, i in enumerate(ints_to_send[player_number]):
        mes += str(i)
        if index + 1 < len(ints_to_send[player_number]):
            mes += " "
    ints_to_send[player_number] = []
    stdout.write("[" + str(player_number) + "]" + mes + "\n")
    stdout.flush()
    response = map(int, raw_input().split())
    received_ints[player_number].extend(response)

def read(player_number):
    global received_ints
    return received_ints[player_number].pop(0)

################ Communication END ###################


def send_int(player_number, a, flush=True):
    to_send(player_number, a)
    if flush:
        send(player_number)

def send_int_list(player_number, intlist):
    """
        At beggining we should send number of ints to be sent
    """
    to_send(player_number, len(intlist))
    for i in intlist:
        to_send(player_number, i)
    send(player_number)

def read_ship_position(player):
    """
        Returns ship_type, x, y
    """
    ship_type = read(player)
    x = read(player)
    y = read(player)
    return ship_type, x, y
    #return 0,0,0

def read_shot(player):
    """
        Returns x, y of player's shot
    """
    x = read(player)
    y = read(player)
    return x, y
    #return 0,0

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
    stderr.write('player %d looses' % error_player)
    stderr.write(error_message)


def send_ships_types(player, stypes):
    send_int_list(player, stypes)

def read_ships_positions(player, game):
    ships_number = len(game.stypes)
    for i in range(ships_number):
        stype, x, y = read_ship_position(player)
        print(stype, x, y)
        game.place_ship(player, stype, x, y)


def play_one(start_player):
    global ints_to_send
    game = Game()
    for player in [1,2]:
        send_int(player, game.n, flush=False)
        send_ships_types(player, game.stypes)
        read_ships_positions(player, game)
        n = game.n


    player = start_player 
    for i in range(MAX_ROUNDS_NUMBER):
        # player 0 shoots
        x, y = read_shot(player)
        stype, dead = game.shoot(opponent(player), x, y)
        game_res = game.game_over() 
        if game_res != -1:
            # returns winner
            return game_res
        send_int(player, stype, flush=False)
        send_int(player, dead)
        player = opponent(player)
    return DRAW


def play():
    global received_ints
    global ints_to_send
    prepare_ships()
    try:
        scores = [0, 0, 0, 0]
        start_player = 1
        for i in range(CLASHES_NUMBER):
            winner = play_one(start_player)
            scores[winner] += 1

            received_ints = [[], [], []]
            ints_to_send = [[], [], []]

            if winner == DRAW:
                send_int(0, DRAW_RESULT, flush=False)
                send_int(1, DRAW_RESULT, flush=False)
            else:
                send_int(winner, WINNER_RESULT, flush=False)
                send_int(opponent(winner), LOSER_RESULT, flush=False)
            start_player = opponent(start_player)
        end_game(scores)
    except GameException as e:
        error_message = e.args[0]
        error_player  = e.args[1]
        end_error(error_player, error_message)

play()


