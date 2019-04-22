"""NeoTrellis M4 colors module."""

from time import sleep


WHITE      = 0xFFFFFF
LIGHT_GRAY = 0x666666
GRAY       = 0x444444
DARK_GRAY  = 0x222222
BLACK      = 0x000000
RED    = 0xFF0000
ORANGE = 0xFF7F00
YELLOW = 0xFFFF00
GREEN  = 0x00FF00
CYAN   = 0x00FFFF
BLUE   = 0x0000FF
VIOLET = 0x7F00FF
PINK   = 0xFF7F7F
COLORS = RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, VIOLET, PINK


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
        sleep(0.01)
