from ctypes import *
import model

DIRECTIONS = {
    1: (1, 0),
    2: (0, 1),
}

MAX_MOVES = 4096

dll = None

def init(dll_path, dawg_path):
    global dll
    dll = CDLL(dll_path)
    dll.init(dawg_path)

def uninit():
    dll.uninit()

class Board(Structure):
    _fields_ = [
        ('width', c_int),
        ('height', c_int),
        ('start', c_int),
        ('letterMultiplier', POINTER(c_int)),
        ('wordMultiplier', POINTER(c_int)),
        ('tileValue', POINTER(c_int)),
        ('tiles', POINTER(c_char)),
    ]

class Move(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int),
        ('direction', c_int),
        ('score', c_int),
        ('tiles', c_char * 16),
    ]

def convert_board(board):
    b = Board()
    b.width = board.width
    b.height = board.height
    b.start = board.start
    letterMultiplier = (c_int * (board.width * board.height))()
    for index, value in enumerate(board.letter_multiplier):
        letterMultiplier[index] = value
    b.letterMultiplier = letterMultiplier
    wordMultiplier = (c_int * (board.width * board.height))()
    for index, value in enumerate(board.word_multiplier):
        wordMultiplier[index] = value
    b.wordMultiplier = wordMultiplier
    tileValue = (c_int * len(board.tile_value))()
    for index, key in enumerate(sorted(board.tile_value.keys())):
        tileValue[index] = board.tile_value[key]
    b.tileValue = tileValue
    tiles = (c_char * (board.width * board.height))()
    for index, value in enumerate(board.tiles):
        tiles[index] = value
    b.tiles = tiles
    return b

def convert_move(move):
    return model.Move(move.x, move.y, DIRECTIONS[move.direction], 
        move.tiles, move.score, [])

def generate_moves(board, letters):
    board = convert_board(board)
    letters = ''.join(letters)
    moves = (Move * MAX_MOVES)()
    count = dll.generateMoves(byref(board), letters, len(letters), moves, MAX_MOVES)
    result = []
    for i in xrange(count):
        move = convert_move(moves[i])
        result.append(move)
    return result
