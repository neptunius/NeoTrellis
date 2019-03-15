class Cell:
    .coord = (col, row)
    .color = BLUE
    .state = {}

class Board:
    .trellis = TrellisM4Express
    .cells = [Cell objects]  # 1-D indexed

    .is_valid(coord) -> bool
    .index_of(coord) -> int in range(len(.cells))

    .cell(col, row) -> Cell object
    .row(row) -> [Cell objects]
    .col(col) -> [Cell objects]

    .paint_cell(col, row, color=None)
    .paint_row(row, color=None)
    .paint_col(col, color=None)
    .paint(color=None)
    .rainbow_cycle(cycles=32)
    .wipe(color, delay=0.1, direction='inward')

    .keys_pressed() -> [coordinate pairs]

class Game:
    .player = BLUE

    .setup()
    .play()
    .is_won() -> witness object or None
