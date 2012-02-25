from model import (
    WILD,
    EMPTY,
    DIRECTION,
    SKIP,
    RACK_SIZE,
    BINGO,
    SENTINEL,
    HORIZONTAL,
    VERTICAL,
    Move,
)

import struct

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

def key_letter(tile):
    if tile.isupper():
        key = WILD
        letter = tile.lower()
    else:
        key = tile
        letter = tile
    return (key, letter)

def compute_move(board, dawg, x, y, direction, tiles):
    mx, my = x, y
    dx, dy = DIRECTION[direction]
    px, py = int(not dx), int(not dy)
    main_word = []
    main_score = 0
    sub_scores = 0
    multiplier = 1
    words = []
    placed = 0
    adjacent = False
    
    # check for dangling tiles before word
    ax, ay = x - dx, y - dy
    if ax >= 0 and ay >= 0 and board.get_tile(ax, ay) != EMPTY:
        return None
    
    for tile in tiles:
        # check for board run off
        if x < 0 or y < 0 or x >= board.width or y >= board.height:
            return None
        adjacent = adjacent or board.is_adjacent(x, y)
        index = board.index(x, y)
        if tile == SKIP:
            tile = board.get_tile(x, y)
            if tile == EMPTY:
                return None
            key, letter = key_letter(tile)
            main_word.append(letter)
            main_score += board.tile_value[key]
        else:
            placed += 1
            key, letter = key_letter(tile)
            main_word.append(letter)
            main_score += board.tile_value[key] * board.letter_multiplier[index]
            multiplier *= board.word_multiplier[index]
            # check for perpendicular word
            sub_word = [letter]
            sub_score = board.tile_value[key] * board.letter_multiplier[index]
            n = 1
            while True: # prefix
                sx = x - px * n
                sy = y - py * n
                if sx < 0 or sy < 0:
                    break
                tile = board.get_tile(sx, sy)
                if tile == EMPTY:
                    break
                key, letter = key_letter(tile)
                sub_word.insert(0, letter)
                sub_score += board.tile_value[key]
                n += 1
            n = 1
            while True: # suffix
                sx = x + px * n
                sy = y + py * n
                if sx >= board.width or sy >= board.height:
                    break
                tile = board.get_tile(sx, sy)
                if tile == EMPTY:
                    break
                key, letter = key_letter(tile)
                sub_word.append(letter)
                sub_score += board.tile_value[key]
                n += 1
            if len(sub_word) > 1:
                sub_score *= board.word_multiplier[index]
                sub_scores += sub_score
                sub_word = ''.join(sub_word)
                words.append(sub_word)
        x += dx
        y += dy
    
    # check for dangling tiles after word
    if x < board.width and y < board.height and board.get_tile(x, y) != EMPTY:
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

def get_horizontal_starts(board, tile_count):
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

def get_vertical_starts(board, tile_count):
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

def _generate(board, x, y, dx, dy, counts, node, tiles, min_tiles, results):
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
                            _generate(board, x + dx, y + dy, dx, dy, counts, 
                                node[tile], tiles, min_tiles, results)
                            tiles.pop()
                            counts[WILD] += 1
                else:
                    if tile in node:
                        counts[tile] -= 1
                        tiles.append(tile)
                        _generate(board, x + dx, y + dy, dx, dy, counts, 
                            node[tile], tiles, min_tiles, results)
                        tiles.pop()
                        counts[tile] += 1
    else:
        if tile in node:
            tiles.append(SKIP)
            _generate(board, x + dx, y + dy, dx, dy, counts, node[tile], 
                tiles, min_tiles, results)
            tiles.pop()

def generate(board, dawg, tiles):
    moves = []
    counts = dict((letter, tiles.count(letter)) for letter in set(tiles))
    hstarts = get_horizontal_starts(board, len(tiles))
    vstarts = get_vertical_starts(board, len(tiles))
    for y in xrange(board.height):
        for x in xrange(board.width):
            index = board.index(x, y)
            min_tiles = hstarts[index]
            if min_tiles:
                direction = HORIZONTAL
                dx, dy = DIRECTION[direction]
                results = []
                _generate(board, x, y, dx, dy, counts, dawg, [], 
                    min_tiles, results)
                for result in results:
                    move = compute_move(board, dawg, x, y, direction, result)
                    if move:
                        moves.append(move)
            min_tiles = vstarts[index]
            if min_tiles:
                direction = VERTICAL
                dx, dy = DIRECTION[direction]
                results = []
                _generate(board, x, y, dx, dy, counts, dawg, [], 
                    min_tiles, results)
                for result in results:
                    move = compute_move(board, dawg, x, y, direction, result)
                    if move:
                        moves.append(move)
    return moves

def generate_moves(board, letters):
    return generate(board, DAWG, letters)

DAWG = load_dawg('files/twl.dawg')
