import random

# Game Constants
HORIZONTAL = 1
VERTICAL = 2

# Board Constants
EMPTY = ' '
WILD = '?'
WIDTH = 15
HEIGHT = 15
START = 112

LETTER_MULTIPLIER = [
    1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,
    1,1,1,1,1,3,1,1,1,3,1,1,1,1,1,
    1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,
    2,1,1,1,1,1,1,2,1,1,1,1,1,1,2,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,3,1,1,1,3,1,1,1,3,1,1,1,3,1,
    1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,
    1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,
    1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,
    1,3,1,1,1,3,1,1,1,3,1,1,1,3,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    2,1,1,1,1,1,1,2,1,1,1,1,1,1,2,
    1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,
    1,1,1,1,1,3,1,1,1,3,1,1,1,1,1,
    1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,
]

WORD_MULTIPLIER = [
    3,1,1,1,1,1,1,3,1,1,1,1,1,1,3,
    1,2,1,1,1,1,1,1,1,1,1,1,1,2,1,
    1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,
    1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,
    1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    3,1,1,1,1,1,1,2,1,1,1,1,1,1,3,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,
    1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,
    1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,
    1,2,1,1,1,1,1,1,1,1,1,1,1,2,1,
    3,1,1,1,1,1,1,3,1,1,1,1,1,1,3,
]

# Tile Constants
RACK_SIZE = 7

TILE_FREQUENCY = {
    'a': 9,
    'b': 2,
    'c': 2,
    'd': 4,
    'e': 12,
    'f': 2,
    'g': 3,
    'h': 2,
    'i': 9,
    'j': 1,
    'k': 1,
    'l': 4,
    'm': 2,
    'n': 6,
    'o': 8,
    'p': 2,
    'q': 1,
    'r': 6,
    's': 4,
    't': 6,
    'u': 4,
    'v': 2,
    'w': 2,
    'x': 1,
    'y': 2,
    'z': 1,
    '?': 2,
}

TILE_VALUE = {
    'a': 1,
    'b': 3,
    'c': 3,
    'd': 2,
    'e': 1,
    'f': 4,
    'g': 2,
    'h': 4,
    'i': 1,
    'j': 8,
    'k': 5,
    'l': 1,
    'm': 3,
    'n': 1,
    'o': 1,
    'p': 3,
    'q': 10,
    'r': 1,
    's': 1,
    't': 1,
    'u': 1,
    'v': 4,
    'w': 4,
    'x': 8,
    'y': 4,
    'z': 10,
    '?': 0,
}

# Model Classes
class Board(object):
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.start = START
        self.letter_multiplier = LETTER_MULTIPLIER
        self.word_multiplier = WORD_MULTIPLIER
        self.tiles = [EMPTY] * (WIDTH * HEIGHT)

class Bag(object):
    def __init__(self):
        self.tiles = ''.join(k * v for k, v in TILE_FREQUENCY.items())
    def pop(self):
        index = random.randint(0, len(self.tiles) - 1)
        return self.tiles.pop(index)
    def empty(self):
        return not self.tiles

class Rack(object):
    def __init__(self):
        self.tiles = []
    def fill(self, bag):
        while len(self.tiles) < RACK_SIZE and not bag.empty():
            self.tiles.append(bag.pop())

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.rack = Rack()

class Game(object):
    def __init__(self):
        self.board = Board()
        self.bag = Bag()
        self.players = [Player('Player %d' % (i + 1)) for i in range(2)]
        for player in self.players:
            player.rack.fill(self.bag)
