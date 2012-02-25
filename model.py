import random

# Constants
HORIZONTAL = 1
VERTICAL = 2

DIRECTION = {
    HORIZONTAL: (1, 0),
    VERTICAL: (0, 1),
}

EMPTY = '.'
WILD = '?'
SKIP = '-'
SENTINEL = '$'

WIDTH = 15
HEIGHT = 15
START = 112

RACK_SIZE = 7
BINGO = 50

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

TILE_FREQUENCY = {
    'a': 9, 'b': 2, 'c': 2, 'd': 4, 'e':12, 'f': 2, 'g': 3, 'h': 2,
    'i': 9, 'j': 1, 'k': 1, 'l': 4, 'm': 2, 'n': 6, 'o': 8, 'p': 2,
    'q': 1, 'r': 6, 's': 4, 't': 6, 'u': 4, 'v': 2, 'w': 2, 'x': 1,
    'y': 2, 'z': 1, WILD: 2,
}

TILE_VALUE = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4,
    'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3,
    'q':10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
    'y': 4, 'z':10, WILD: 0,
}

# Model Classes
class Move(object):
    def __init__(self, x, y, direction, tiles, score, words):
        self.x = x
        self.y = y
        self.direction = direction
        self.tiles = tiles
        self.score = score
        self.words = words
    def __str__(self):
        words = ', '.join(self.words)
        return '%d %s "%s" [%s]' % (self.score, self.vector, self.tiles, words)
    @property
    def key(self):
        return (-self.score, self.tiles)
    @property
    def vector(self):
        row = '%02d' % (self.y + 1)
        col = chr(ord('A') + self.x)
        if self.direction == HORIZONTAL:
            return row + col
        else:
            return col + row

class Board(object):
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.start = START
        self.letter_multiplier = LETTER_MULTIPLIER
        self.word_multiplier = WORD_MULTIPLIER
        self.tile_value = TILE_VALUE
        self.tiles = [EMPTY] * (WIDTH * HEIGHT)
    def __str__(self):
        width = self.width
        data = ''.join(self.tiles)
        rows = []
        for index in xrange(len(data) / width):
            rows.append(data[index * width:index * width + width])
        return '\n'.join(rows)
    def index(self, x, y):
        return y * self.width + x
    def get_tile(self, x, y):
        return self.tiles[self.index(x, y)]
    def is_empty(self, x, y):
        return self.get_tile(x, y) == EMPTY
    def is_adjacent(self, x, y):
        if self.index(x, y) == self.start:
            return True
        if x > 0 and not self.is_empty(x - 1, y):
            return True
        if y > 0 and not self.is_empty(x, y - 1):
            return True
        if x < self.width - 2 and not self.is_empty(x + 1, y):
            return True
        if y < self.height - 2 and not self.is_empty(x, y + 1):
            return True
        return False
    def do_move(self, move):
        x, y = move.x, move.y
        dx, dy = DIRECTION[move.direction]
        for tile in move.tiles:
            if tile != SKIP:
                index = self.index(x, y)
                self.tiles[index] = tile
            x += dx
            y += dy
    def undo_move(self, move):
        x, y = move.x, move.y
        dx, dy = DIRECTION[move.direction]
        for tile in move.tiles:
            if tile != SKIP:
                index = self.index(x, y)
                self.tiles[index] = EMPTY
            x += dx
            y += dy

class Bag(object):
    def __init__(self):
        self.tiles = list(''.join(k * v for k, v in TILE_FREQUENCY.items()))
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
    def empty(self):
        return not self.tiles
    def do_move(self, move):
        for tile in move.tiles:
            if tile != SKIP:
                key = WILD if tile.isupper() else tile
                self.tiles.remove(key)

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.rack = Rack()

class Game(object):
    def __init__(self):
        self.board = Board()
        self.bag = Bag()
        self.players = [Player('Player %d' % (i + 1)) for i in xrange(2)]
        for player in self.players:
            player.rack.fill(self.bag)

if __name__ == '__main__':
    import cEngine as engine
    board = Board()
    bag = Bag()
    rack = Rack()
    rack.fill(bag)
    score = 0
    while not rack.empty():
        moves = engine.generate_moves(board, rack.tiles)
        moves.sort(key=lambda x:x.key)
        if not moves:
            break
        move = moves[0]
        print move
        board.do_move(move)
        rack.do_move(move)
        rack.fill(bag)
        score += move.score
    print
    print board
    print score
