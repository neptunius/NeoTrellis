"""Corners: An adversarial game of squares."""

from adafruit_trellism4 import TrellisM4Express
from colors import *
from time import sleep


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
        self.trellis = TrellisM4Express(rotation=0)
        self.trellis.pixels.brightness = 0.04  # 0.1  # 0.2  #
        self.last_pressed_keys = set([])
        self.last_pressed_key = (0, 0)  # (8, 8)
        self.blank_color = DARK_GRAY  # GRAY  # LIGHT_GRAY
        self.rainbow_offset = 0
        self.create_board()

    def rainbow_board(self):
        for _ in range(8):
            self.board = [COLORS[(i + self.rainbow_offset) % 7] for i in range(8*4)]
            self.rainbow_offset -= 1
            self.color_board()
        self.create_board()  # reset board

    def create_board(self):
        self.board = [self.blank_color for index in range(8*4)]

    def keys_pressed(self):
        now_pressed = set(self.trellis.pressed_keys)
        new_presses = list(now_pressed - self.last_pressed_keys)
        self.last_pressed_keys = now_pressed
        return new_presses

    def fill_board(self, color=WHITE):
        self.trellis.pixels.fill(color)

    def flash_board(self, color=GRAY, times=3, delay=0.1):
        for _ in range(times):
            self.fill_board(color)  # given color
            sleep(delay)
            self.fill_board(self.blank_color)  # blank color
            sleep(delay)
        self.color_board()  # redraw board with key colors

    def color_board(self):
        for row in (0, 1, 2, 3):
            for col in range(8):
                key = col, row
                color = self.board[index_of(key)]
                self.trellis.pixels[key] = color

    def color_keys(self, keys, color=None):
        for key in keys:
            key_color = self.board[index_of(key)] if color is None else color
            self.trellis.pixels[key] = key_color

    def flash_keys(self, keys, color=GRAY, times=3, delay=0.1):
        for _ in range(times):
            self.color_keys(keys, color)  # given color
            sleep(delay)
            self.color_keys(keys)  # original key color
            sleep(delay)

    def wipe(self, color, delay=0.1, direction='inward'):
        for col in range(4):
            col = 3-col if direction == 'outward' else col
            row_coords1 = [(col, row) for row in range(4)]
            row_coords2 = [(7-col, row) for row in range(4)]
            self.color_keys(row_coords1 + row_coords2, color)
            sleep(delay)

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
                    coords = [coord, coord1, coord2, coord3]
                    colors = [player, color1, color2, color3]
                    self.flash_keys(coords, color=LIGHT_GRAY, times=2, delay=0.05)
                    if all(color == player for color in colors):
                        witness = (coord, coord1, coord2, coord3)
                        # self.flash_keys(witness, color=player, times=5)
                        return witness

    def play(self):
        keys_pressed = []
        PLAYERS = [RED, GREEN, BLUE, VIOLET]
        NUM_PLAYERS = 4
        player = RED
        won = False
        while not won:
            self.color_board()
            keys_pressed = self.keys_pressed()
            if keys_pressed:
                key = keys_pressed[0]
                if key == self.last_pressed_key:
                    if key == (0, 0):  # upper left corner
                        self.rainbow_board()
                        while True:
                            # rainbow cycle through color spectrum
                            splash(cycles=32, trellis=self.trellis)
                            keys_pressed = self.keys_pressed()
                            if keys_pressed:
                                key = keys_pressed[0]
                                # different from last key (corner)
                                if key != self.last_pressed_key:
                                    return  # end game to start a new one
                    if key == (7, 0):  # upper right corner
                        return  # end game to start a new one
                # TODO: check if this breaks multiple inputs
                self.last_pressed_key = key
                self.board[index_of(key)] = player
                self.flash_keys([key], color=LIGHT_GRAY)
                witness = self.find_winner(key)
                won = witness is not None
                if not won:
                    self.wipe(player, delay=0.03, direction='outward')
                    player = PLAYERS[(PLAYERS.index(player) + 1) % NUM_PLAYERS]
                    self.wipe(player, delay=0.03, direction='inward')
                    self.color_board()
        if won:
            for _ in range(2):
                self.flash_board(color=player, times=3, delay=0.2)
                if witness:
                    self.flash_keys(witness, color=LIGHT_GRAY, times=5, delay=0.1)
            sleep(1.0)

def main_loop():
    game = Game()
    while True:
        game.rainbow_board()
        game.play()


if __name__ == '__main__':
    main_loop()
