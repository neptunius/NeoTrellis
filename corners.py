"""Corners: An adversarial game of squares."""

import time
import random
import adafruit_trellism4

COLORS = [0xFF0000, 0xFF5F00, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0xAA00FF]
RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, MAGENTA = COLORS
BLACK, WHITE, GRAY, DARK_GRAY = 0x000000, 0xFFFFFF, 0x444444, 0x222222


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return 0, 0, 0
    if pos < 85:
        return int(255 - pos*3), int(pos*3), 0
    if pos < 170:
        pos -= 85
        return 0, int(255 - pos*3), int(pos*3)
    pos -= 170
    return int(pos * 3), 0, int(255 - (pos*3))

def cycle_sequence(seq):
    while True:
        for elem in seq:
            yield elem

def rainbow_lamp(seq, key=None, trellis=None):
    g = cycle_sequence(seq)
    while True:
        color = wheel(next(g))
        if key:
            trellis.pixels[key] = color
        else:
            trellis.pixels.fill(color)
        yield

def splash(cycles=64, key=None, trellis=None):
    rainbow = rainbow_lamp(range(0, 256, 8), key, trellis)
    for _ in range(cycles):
        next(rainbow)
        time.sleep(0.005)


def add_coords(pointA, pointB):
    return (pointA[0] + pointB[0], pointA[1] + pointB[1])

def is_valid(coord):
    x, y = coord
    return 0 <= x < 8 and 0 <= y < 4

def index_of(coord):
    x, y = coord
    return y * 8 + x

def outward_from(coord):
    x, y = coord
    for d in range(1, 4):
        coords = (x + d, y), (x - d, y), (x, y + d), (x, y - d)
        coords = filter(is_valid, coords)
        yield coords


class Game:

    def __init__(self):
        self.trellis = adafruit_trellism4.TrellisM4Express(rotation=0)
        self.trellis.pixels.brightness = 0.1
        self.last_pressed_keys = set([])
        self.last_pressed_key = (0, 0)  # (8, 8)
        self.blank_color = DARK_GRAY
        self.rainbow_offset = 0
        self.rainbow_board()
        self.fill_board(RED)
        self.fill_board(BLUE)

    def rainbow_board(self):
        for _ in range(12):
            self.board = [COLORS[(i + self.rainbow_offset) % len(COLORS)] for i in range(8*4)]
            # self.board = [random.choice(COLORS) for _ in range(8*4)]
            self.rainbow_offset -= 1
            self.color_board()

    def create_board(self):
        # self.board = [[GRAY for col in range(8)] for row in range(4)]
        self.board = [self.blank_color for index in range(8*4)]
        self.color_board()

    def keys_pressed(self):
        now_pressed = set(self.trellis.pressed_keys)
        new_presses = list(now_pressed - self.last_pressed_keys)
        self.last_pressed_keys = now_pressed
        return new_presses

    def fill_board(self, color=WHITE):
        self.trellis.pixels.fill(color)

    def color_board(self):
        # colors = {}
        for row in (0, 3, 2, 1):
            for col in range(8):
                key = col, row
                color = self.board[index_of(key)]
                # if color != self.blank_color:
                # if True:
                #     colors[key] = color
                self.trellis.pixels[key] = color
        # self.fill_board(self.blank_color)
        # for key, color in sorted(colors.items()):
        #     self.trellis.pixels[key] = color

    def color_keys(self, keys, color=None):
        for key in keys:
            key_color = self.board[index_of(key)] if color is None else color
            self.trellis.pixels[key] = key_color

    def flash_keys(self, keys, color=None, times=3, delay=0.1):
        for _ in range(times-1):
            self.color_keys(keys, BLACK)
            time.sleep(delay)
            self.color_keys(keys, color)
            time.sleep(delay)
        self.color_keys(keys)
        time.sleep(delay)

    def wipe(self, color, delay=0.1, direction='inward'):
        for col in range(4):
            col = 3-col if direction == 'outward' else col
            row_coords1 = [(col, row) for row in range(4)]
            row_coords2 = [(7-col, row) for row in range(4)]
            self.color_keys(row_coords1 + row_coords2, color)
            time.sleep(delay)

    def find_winner(self, coord):
        player = self.board[index_of(coord)]
        x, y = coord
        for size in range(1, 4):
            offsets = (+size, 0), (0, +size), (-size, 0), (0, -size)  # E,N,W,S
            wraparound = tuple(offsets[1:] + offsets[:1])  # N,W,S,E
            for offset1, offset2 in zip(offsets, wraparound):
                coord1 = add_coords(coord, offset1)  # P+E, P+N, P+W, P+S
                coord2 = add_coords(coord, offset2)  # P+S, P+E, P+N, P+W
                diagonal = add_coords(offset1, offset2)  # NE, NW, SW, SE
                coord3 = add_coords(coord, diagonal)  # P+NE, P+NW, P+SW, P+SE
                if is_valid(coord1) and is_valid(coord2) and is_valid(coord3):
                    color1 = self.board[index_of(coord1)]
                    color2 = self.board[index_of(coord2)]
                    color3 = self.board[index_of(coord3)]
                    coords = [coord1, coord2, coord3]
                    colors = [color1, color2, color3]
                    self.flash_keys(coords, color=YELLOW, delay=0.01)
                    if all(color == player for color in colors):
                        witness = (coord, coord1, coord2, coord3)
                        self.flash_keys(witness, player, 5)
                        return witness

    def play(self):
        keys_pressed = []
        player = BLUE
        won = False
        while not won:
            self.color_board()
            keys_pressed = self.keys_pressed()
            if keys_pressed:
                key = keys_pressed[0]
                if key == self.last_pressed_key:
                    if key == (0, 0):  # upper left corner
                        rainbow = True
                        self.rainbow_board()
                        while rainbow:
                            splash(cycles=32, trellis=self.trellis)
                            keys_pressed = self.keys_pressed()
                            if keys_pressed:
                                key = keys_pressed[0]
                                if key != self.last_pressed_key:
                                    return
                    if key == (7, 0):  # upper right corner
                        self.rainbow_board()
                        return
                self.last_pressed_key = key
                self.board[index_of(key)] = player
                self.flash_keys([key], player)
                witness = self.find_winner(key)
                if witness:
                    won = True
                    self.fill_board(GREEN)
                    time.sleep(0.2)
                    for _ in range(5):
                        self.color_board()
                        time.sleep(0.2)
                        self.fill_board(player)
                        time.sleep(0.2)
                        self.color_board()
                        self.flash_keys(witness, player, 5)
                else:
                    self.wipe(player, delay=0.05, direction='outward')
                    player = BLUE if player is RED else RED
                    self.wipe(player, delay=0.1, direction='inward')
                    self.color_board()

def main_loop():
    game = Game()
    while True:
        game.create_board()
        game.play()


if __name__ == '__main__':
    main_loop()
