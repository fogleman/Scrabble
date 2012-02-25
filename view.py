import colorsys
import model
import operator
import threading
import wx

COLORS = {
    (1, 1): (165, 155, 145),
    (1, 2): (125, 175, 205),
    (1, 3): (0, 70, 120),
    (2, 1): (210, 160, 180),
    (3, 1): (165, 45, 65),
}

def adjust(r, g, b, offset):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v += offset
    v = min(1, v)
    v = max(0, v)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def make_font(face, size, bold=False, italic=False, underline=False):
    family = wx.FONTFAMILY_DEFAULT
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    font = wx.Font(size, family, style, weight, underline, face)
    return font

class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        self.reset()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
    def reset(self):
        self.board = model.Board()
        start(self.board, self.Refresh)
    def on_left_down(self, event):
        self.reset()
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        self.draw(dc)
    def draw(self, dc):
        board = self.board
        pad = 20
        w, h = self.GetClientSize()
        size = min(w, h)
        size -= pad * 2
        size = (size / board.width) * board.width
        dc.SetDeviceOrigin((w - size) / 2, (h - size) / 2)
        self.draw_board(dc, size)
    def draw_board(self, dc, size):
        pad = 3
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRoundedRectangle(-pad, -pad, size + pad * 2, size + pad * 2, pad)
        board = self.board
        n = size / board.width
        m = n - 1
        dc.SetFont(make_font('Courier New', n * 3 / 5, True))
        for j in xrange(board.height):
            for i in xrange(board.width):
                tile = board.get_tile(i, j)
                if tile == model.EMPTY:
                    index = board.index(i, j)
                    key = (board.word_multiplier[index], board.letter_multiplier[index])
                    r, g, b = COLORS[key]
                else:
                    r, g, b = (48, 48, 48)
                x = i * n
                y = j * n
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetBrush(wx.Brush(wx.Colour(r, g, b)))
                dc.DrawRectangle(x, y, n, n)
                dc.SetPen(wx.Pen(wx.Colour(*adjust(r, g, b, 0.2))))
                dc.DrawLine(x, y, x + m, y)
                dc.DrawLine(x, y, x, y + m)
                dc.SetPen(wx.Pen(wx.Colour(*adjust(r, g, b, -0.2))))
                dc.DrawLine(x + m, y, x + m, y + m)
                dc.DrawLine(x, y + m, x + m, y + m)
                if tile != model.EMPTY:
                    letter = tile.upper()
                    tw, th = dc.GetTextExtent(letter)
                    tx, ty = x + n / 2 - tw / 2, y + n / 2 - th / 2
                    dc.SetTextForeground(wx.Colour(*adjust(r, g, b, 0.2)))
                    dc.DrawText(letter, tx - 1, ty - 1)
                    if tile.isupper():
                        dc.SetTextForeground(wx.YELLOW)
                    else:
                        dc.SetTextForeground(wx.WHITE)
                    dc.DrawText(letter, tx, ty)

def start(board, func):
    thread = threading.Thread(target=run, args=(board, func))
    thread.setDaemon(True)
    thread.start()

def run(board, func):
    import cEngine as engine
    bag = model.Bag()
    rack = model.Rack()
    rack.fill(bag)
    score = 0
    while not rack.empty():
        moves = engine.generate_moves(board, rack.tiles)
        moves.sort(key=operator.attrgetter('score'), reverse=True)
        if not moves:
            break
        move = moves[0]
        print move
        board.do_move(move)
        rack.do_move(move)
        rack.fill(bag)
        score += move.score
        wx.CallAfter(func)
    print 'Score = %d' % score

def main():
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    Panel(frame)
    frame.SetTitle('Scrabble')
    frame.SetClientSize((600, 600))
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
