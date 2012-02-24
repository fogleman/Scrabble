from model import (
    EMPTY,
    SKIP,
    WILD,
)
import model
import struct

SENTINEL = '$'

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

class Generator(object):
    def __init__(self, dawg, board):
        self.dawg = dawg
        self.board = board
    def is_empty(self, x, y):
        return self.board.get_tile(x, y) == EMPTY
    def is_adjacent(self, x, y):
        board = self.board
        if board.index(x, y) == board.start:
            return True
        if x > 0 and not self.is_empty(x - 1, y):
            return True
        if y > 0 and not self.is_empty(x, y - 1):
            return True
        if x < board.width - 2 and not self.is_empty(x + 1, y):
            return True
        if y < board.height - 2 and not self.is_empty(x, y + 1):
            return True
        return False
    def get_horizontal_starts(self, tile_count):
        board = self.board
        result = [0] * (board.width * board.height)
        for y in xrange(board.height):
            for x in xrange(board.width):
                if x > 0 and not self.is_empty(x - 1, y):
                    continue
                if self.is_empty(x, y):
                    for i in xrange(tile_count):
                        if x + i < board.width and self.is_adjacent(x + i, y):
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
                if y > 0 and not self.is_empty(x, y - 1):
                    continue
                if self.is_empty(x, y):
                    for i in xrange(tile_count):
                        if y + i < board.height and self.is_adjacent(x, y + i):
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
                                self._generate(x + dx, y + dy, dx, dy, counts, node[tile], tiles, min_tiles, results)
                                tiles.pop()
                                counts[WILD] += 1
                    else:
                        if tile in node:
                            counts[tile] -= 1
                            tiles.append(tile)
                            self._generate(x + dx, y + dy, dx, dy, counts, node[tile], tiles, min_tiles, results)
                            tiles.pop()
                            counts[tile] += 1
        else:
            if tile in node:
                tiles.append(SKIP)
                self._generate(x + dx, y + dy, dx, dy, counts, node[tile], tiles, min_tiles, results)
                tiles.pop()
    def generate(self, tiles):
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
                    results = []
                    self._generate(x, y, 1, 0, counts, dawg, [], min_tiles, results)
                    for result in results:
                        print '%02d,%02d,%d %s' % (x, y, 1, result)
                min_tiles = vstarts[index]
                if min_tiles:
                    results = []
                    self._generate(x, y, 0, 1, counts, dawg, [], min_tiles, results)
                    for result in results:
                        print '%02d,%02d,%d %s' % (x, y, 2, result)

def print_data(data, width=model.WIDTH):
    data = ''.join(str(x) for x in data)
    rows = []
    for index in xrange(len(data) / width):
        rows.append(data[index * width:index * width + width])
    print '\n'.join(rows)

if __name__ == '__main__':
    dawg = load_dawg('files/twl.dawg')
    board = model.Board()
    x, y = 2, 7
    for i, c in enumerate('testing'):
        board.tiles[board.index(x + i, y)] = c
    generator = Generator(dawg, board)
    generator.generate('qzx?tar')
    print_data(board.tiles)
