"""Corners: An adversarial game of squares."""

import time
import random
import adafruit_trellism4

COLORS = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0xFF00FF]
RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA = COLORS
BLACK, WHITE, GRAY, DARK_GRAY = 0x000000, 0xFFFFFF, 0x444444, 0x222222

def is_valid(coord):
    x, y = coord
    return 0 <= x < 8 and 0 <= y < 4

def index_of(coord):
    x, y = coord
    return y * 8 + x

def outward_from(coord):
    x, y = coord
    # coords = (x + d, y), (x - d, y), (x, y + d), (x, y - d)
    for d in range(1, 4):
        coords = (x + d, y), (x - d, y), (x, y + d), (x, y - d)
        coords = filter(is_valid, coords)
        yield coords  # if len(coords) > 1 else []
    # return y * 8 + x


class Game:

    def __init__(self):
        self.trellis = adafruit_trellism4.TrellisM4Express(rotation=0)
        self.trellis.pixels.brightness = 0.05
        self.trellis.pixels.fill(RED)

        self.last_pressed_keys = set([])
        self.create_board()

    def create_board(self):
        # self.board = [[GRAY for col in range(8)] for row in range(4)]
        # self.board = [[random.choice(COLORS) for col in range(8)] for row in range(4)]
        # self.board = [random.choice(COLORS) for index in range(8*4)]
        # self.board = [COLORS[index % len(COLORS)] for index in range(8*4)]
        self.board = [DARK_GRAY for index in range(8*4)]
        self.color_board()

    def keys_pressed(self):
        now_pressed = set(self.trellis.pressed_keys)
        new_presses = now_pressed - self.last_pressed_keys
        self.last_pressed_keys = now_pressed
        return list(new_presses)

    def color_board(self):
        for row in range(4):
            for col in range(8):
                key = col, row
                color = self.board[index_of(key)]
                # color = self.board[row][col]
                self.trellis.pixels[key] = color

    def color_keys(self, keys, color):
        for key in keys:
            self.trellis.pixels[key] = color

    def flash_keys(self, keys, color=WHITE, times=3, delay=0.1):
        self.color_keys(keys, color)
        time.sleep(delay)
        for _ in range(times-1):
            self.color_keys(keys, BLACK)
            time.sleep(delay)
            self.color_keys(keys, color)
            time.sleep(delay)
        # self.color_keys(keys, color)  # GRAY
        # time.sleep(delay)
        # self.color_keys(keys, color)

    def find_winner(self, coord):
        # return self.board[0] == BLUE
        player = self.board[index_of(coord)]
        x, y = coord
        # coords = (x + d, y), (x - d, y), (x, y + d), (x, y - d)
        for size in range(1, 2):
            coords = (x+size, y), (x, y+size), (x-size, y), (x, y-size)  # E,N,W,S
            for coord in coords:
                if is_valid(coord):
                    color = self.board[index_of(coord)]
                    # if color == player:
                    if True:
                        self.flash_keys([coord], GRAY)
                        # self.flash_keys([coord], color)
                        # self.color_keys([coord], WHITE)
                        # time.sleep(0.1)
                        # self.color_keys([coord], color)
                        # time.sleep(0.1)
            # coords = filter(is_valid, coords)
            # self.trellis.pixels.fill(YELLOW)
            def add_coords(pointA, pointB):
                return (pointA[0] + pointB[0], pointA[1] + pointB[1])
            offsets = (+size, 0), (0, +size), (-size, 0), (0, -size)  # E,N,W,S
            for offset1, offset2 in zip(offsets, offsets[1:]+offsets[:1]):
                coord1 = add_coords(coord, offset1)
                coord2 = add_coords(coord, offset2)
                if is_valid(coord1) and is_valid(coord2):
                    color1 = self.board[index_of(coord1)]
                    color2 = self.board[index_of(coord2)]
                    # self.trellis.pixels.fill(CYAN)
                    self.flash_keys([coord1, coord2], GRAY, 2)
                    if color1 == player and color2 == player:
                        self.flash_keys([coord1, coord2], player)
                        coord3 = add_coords(coord, add_coords(offset1, offset2))
                        if is_valid(coord3):
                            color3 = self.board[index_of(coord3)]
                            self.flash_keys([coord3], GRAY, 2)
                            if color3 == player:
                                self.flash_keys([coord3], player)
                                coords = (coord, coord1, coord2, coord3)
                                self.color_keys(coords, player)
                                time.sleep(0.1)
                                return coords

    def play(self):
        # self.trellis.pixels.fill(BLUE)
        # assign_colors()
        keys_pressed = []
        # first_pixel = None
        # found_pairs = 0
        # remaining = [(x, y) for x in range(8) for y in range(4)]
        # self.board = self.random_colors()

        player = BLUE
        won = False
        while not won:
            self.color_board()
            # time.sleep(0.5)
            # Handle key input
            keys_pressed = self.keys_pressed()
            if keys_pressed:
                # self.trellis.pixels.fill(YELLOW)
                key = keys_pressed[0]
                # row, col = key
                # self.board[row][col] = player
                self.board[index_of(key)] = player
                self.flash_keys([key], player)
                # for times, keys in enumerate(outward_from(key)):
                    # keys = (right, left, up, down)
                    # self.flash_keys(keys, player, times=3)
                # self.trellis.pixels.fill(GREEN)
                # self.trellis.pixels.fill(YELLOW)
                # Find where a square created
                witness = self.find_winner(key)
                if witness:
                    won = True
                    for _ in range(5):
                        self.trellis.pixels.fill(GREEN)
                        time.sleep(0.5)
                        self.trellis.pixels.fill(player)
                        time.sleep(1)
                        self.color_board()
                        self.flash_keys(witness, player, 5)
                else:
                    player = BLUE if player is RED else RED
                    # self.trellis.pixels.fill(player)
                    # time.sleep(1)
                    corners = [(0, 0), (7, 0), (0, 3), (7, 3)]
                    self.flash_keys(corners, player, delay=0.2)
                    self.color_board()

def main_loop():
    game = Game()
    while True:
        game.create_board()
        game.play()
        # memory.splash()


if __name__ == '__main__':
    main_loop()
