import operator
import random
import struct

# Constants
HORIZONTAL = (1, 0)
VERTICAL = (0, 1)

PERPENDICULAR = {
    HORIZONTAL: VERTICAL,
    VERTICAL: HORIZONTAL,
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

# Functions
def key_letter(tile):
    if tile.isupper():
        key = WILD
        letter = tile.lower()
    else:
        key = tile
        letter = tile
    return (key, letter)

def load_dawg(path):
    with open(path, 'rb') as fp:
        data = fp.read()
    groups = {}
    start = 0
    lookup = {}
    for index in xrange(len(data) / 4):
        block = data[index * 4:index * 4 + 4]
        x = struct.unpack('<I', block)[0]
        link = x & 0xffffff
        letter = chr((x >> 24) & 0x7f)
        more = bool((x >> 31) & 1)
        lookup[letter] = link
        if not more:
            groups[start] = lookup
            start = index + 1
            lookup = {}
    for lookup in groups.itervalues():
        for letter, link in lookup.iteritems():
            lookup[letter] = groups[link] if link else None
    return groups[0]

def check_dawg(dawg, word):
    word = '%s$' % word.lower()
    node = dawg
    for letter in word:
        if letter in node:
            node = node[letter]
        else:
            return False
    return True

# Model Classes
class Move(object):
    def __init__(self, x, y, direction, tiles, score, words):
        self.x = x
        self.y = y
        self.direction = direction
        self.tiles = tiles
        self.score = score
        self.words = words

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
    def xy(self, index):
        return (index % self.width, index / self.width)
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
        dx, dy = move.direction
        for tile in move.tiles:
            if tile != SKIP:
                index = self.index(x, y)
                self.tiles[index] = tile
            x += dx
            y += dy
    def undo_move(self, move):
        x, y = move.x, move.y
        dx, dy = move.direction
        for tile in move.tiles:
            if tile != SKIP:
                index = self.index(x, y)
                self.tiles[index] = EMPTY
            x += dx
            y += dy
    def compute_move(self, dawg, x, y, direction, tiles):
        mx, my = x, y
        dx, dy = direction
        px, py = PERPENDICULAR[direction]
        main_word = []
        main_score = 0
        sub_scores = 0
        multiplier = 1
        words = []
        placed = 0
        adjacent = False
        
        # check for dangling tiles before word
        ax, ay = x - dx, y - dy
        if ax >= 0 and ay >= 0 and self.get_tile(ax, ay) != EMPTY:
            return None
        
        for tile in tiles:
            # check for board run off
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return None
            adjacent = adjacent or self.is_adjacent(x, y)
            index = self.index(x, y)
            if tile == SKIP:
                tile = self.get_tile(x, y)
                if tile == EMPTY:
                    return None
                key, letter = key_letter(tile)
                main_word.append(letter)
                main_score += self.tile_value[key]
            else:
                placed += 1
                key, letter = key_letter(tile)
                main_word.append(letter)
                main_score += self.tile_value[key] * self.letter_multiplier[index]
                multiplier *= self.word_multiplier[index]
                # check for perpendicular word
                sub_word = [letter]
                sub_score = 0
                n = 1
                while True: # prefix
                    sx = x - px * n
                    sy = y - py * n
                    if sx < 0 or sy < 0:
                        break
                    tile = self.get_tile(sx, sy)
                    if tile == EMPTY:
                        break
                    key, letter = key_letter(tile)
                    sub_word.insert(0, letter)
                    sub_score += self.tile_value[key]
                    n += 1
                n = 1
                while True: # suffix
                    sx = x + px * n
                    sy = y + py * n
                    if sx >= self.width or sy >= self.height:
                        break
                    tile = self.get_tile(sx, sy)
                    if tile == EMPTY:
                        break
                    key, letter = key_letter(tile)
                    sub_word.append(letter)
                    sub_score += self.tile_value[key]
                    n += 1
                if len(sub_word) > 1:
                    sub_score *= self.word_multiplier[index]
                    sub_scores += sub_score
                    sub_word = ''.join(sub_word)
                    words.append(sub_word)
            x += dx
            y += dy
        
        # check for dangling tiles after word
        if x < self.width and y < self.height and self.get_tile(x, y) != EMPTY:
            return None
        
        # check for placed tiles
        if placed < 1 or placed > RACK_SIZE or not adjacent:
            return None
        
        # compute score
        main_score *= multiplier
        score = main_score + sub_scores
        if placed == RACK_SIZE:
            score += BINGO
        main_word = ''.join(main_word)
        words.insert(0, main_word)
        
        # check words
        for word in words:
            if not check_dawg(dawg, word):
                return None
        
        # build result
        return Move(mx, my, direction, tiles, score, words)

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

class Generator(object):
    def __init__(self, dawg, board):
        self.dawg = dawg
        self.board = board
    def get_horizontal_starts(self, tile_count):
        board = self.board
        result = [0] * (board.width * board.height)
        for y in xrange(board.height):
            for x in xrange(board.width):
                if x > 0 and not board.is_empty(x - 1, y):
                    continue
                if board.is_empty(x, y):
                    for i in xrange(tile_count):
                        if x + i < board.width and board.is_adjacent(x + i, y):
                            result[board.index(x, y)] = i + 1
                            break
                else:
                    result[board.index(x, y)] = 1
        return result
    def get_vertical_starts(self, tile_count):
        board = self.board
        result = [0] * (board.width * board.height)
        for y in xrange(board.height):
            for x in xrange(board.width):
                if y > 0 and not board.is_empty(x, y - 1):
                    continue
                if board.is_empty(x, y):
                    for i in xrange(tile_count):
                        if y + i < board.height and board.is_adjacent(x, y + i):
                            result[board.index(x, y)] = i + 1
                            break
                else:
                    result[board.index(x, y)] = 1
        return result
    def _generate(self, x, y, dx, dy, counts, node, tiles, min_tiles, results):
        board = self.board
        if len(tiles) >= min_tiles and SENTINEL in node:
            results.append(''.join(tiles))
        if x >= board.width or y >= board.height:
            return
        tile = board.get_tile(x, y).lower()
        if tile == EMPTY:
            for tile in counts:
                if counts[tile]:
                    if tile == WILD:
                        for letter in xrange(26):
                            tile = chr(ord('a') + letter)
                            if tile in node:
                                counts[WILD] -= 1
                                tiles.append(tile.upper())
                                self._generate(x + dx, y + dy, dx, dy, counts, 
                                    node[tile], tiles, min_tiles, results)
                                tiles.pop()
                                counts[WILD] += 1
                    else:
                        if tile in node:
                            counts[tile] -= 1
                            tiles.append(tile)
                            self._generate(x + dx, y + dy, dx, dy, counts, 
                                node[tile], tiles, min_tiles, results)
                            tiles.pop()
                            counts[tile] += 1
        else:
            if tile in node:
                tiles.append(SKIP)
                self._generate(x + dx, y + dy, dx, dy, counts, node[tile], 
                    tiles, min_tiles, results)
                tiles.pop()
    def generate(self, tiles):
        moves = []
        dawg = self.dawg
        board = self.board
        counts = dict((letter, tiles.count(letter)) for letter in set(tiles))
        hstarts = self.get_horizontal_starts(len(tiles))
        vstarts = self.get_vertical_starts(len(tiles))
        for y in xrange(board.height):
            for x in xrange(board.width):
                index = board.index(x, y)
                min_tiles = hstarts[index]
                if min_tiles:
                    dx, dy = direction = HORIZONTAL
                    results = []
                    self._generate(x, y, dx, dy, counts, dawg, [], 
                        min_tiles, results)
                    for result in results:
                        move = board.compute_move(dawg, x, y, direction, result)
                        if move:
                            moves.append(move)
                min_tiles = vstarts[index]
                if min_tiles:
                    dx, dy = direction = VERTICAL
                    results = []
                    self._generate(x, y, dx, dy, counts, dawg, [], 
                        min_tiles, results)
                    for result in results:
                        move = board.compute_move(dawg, x, y, direction, result)
                        if move:
                            moves.append(move)
        return moves

if __name__ == '__main__':
    dawg = load_dawg('files/twl.dawg')
    board = Board()
    bag = Bag()
    rack = Rack()
    rack.fill(bag)
    score = 0
    while not bag.empty():
        print ''.join(rack.tiles)
        generator = Generator(dawg, board)
        moves = generator.generate(rack.tiles)
        moves.sort(key=operator.attrgetter('score'), reverse=True)
        if not moves:
            break
        move = moves[0]
        print move.x, move.y, move.score, move.tiles, move.words
        board.do_move(move)
        score += move.score
        for tile in move.tiles:
            if tile != SKIP:
                key, letter = key_letter(tile)
                rack.tiles.remove(key)
        print board
        print score
        print
        rack.fill(bag)
