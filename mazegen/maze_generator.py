import random
import sys


BITMAP_FONT: dict[str, list[str]] = {
    "A": ["01110", "10001", "11111", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000"],
    "G": ["01111", "10000", "10011", "10001", "01111"],
    "H": ["10001", "10001", "11111", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "11111"],
    "J": ["11111", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "11100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001"],
    "O": ["01110", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "11110", "10000", "10000"],
    "Q": ["01110", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "11110", "10010", "10001"],
    "S": ["01111", "10000", "01110", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100"],
    "Z": ["11111", "00010", "00100", "01000", "11111"],
    "0": ["01110", "10011", "10101", "11001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "01110"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["11110", "00001", "01110", "00001", "11110"],
    "4": ["100", "100", "111", "001", "001"],
    "5": ["11111", "10000", "11110", "00001", "11110"],
    "6": ["01110", "10000", "11110", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000"],
    "8": ["01110", "10001", "01110", "10001", "01110"],
    "9": ["01110", "10001", "01111", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00100"],
    ",": ["00000", "00000", "00000", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00110", "00000", "00100"],
    "-": ["00000", "00000", "11111", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "11111"],
    "#": ["01010", "11111", "01010", "11111", "01010"],
}


def text_to_pattern(text: str) -> list[str]:
    upper = text.upper()
    chars: list[list[str]] = []
    for char in upper:
        if char in BITMAP_FONT:
            chars.append(BITMAP_FONT[char])
        else:
            chars.append(BITMAP_FONT[" "])
    pattern_rows: list[str] = []
    for row_idx in range(5):
        row = ""
        for i, char_grid in enumerate(chars):
            if i > 0:
                row += "0"
            row += char_grid[row_idx]
        pattern_rows.append(row)
    return pattern_rows


class MazeGenerator:
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    PATTERN_42: list[str] = [
        "F000FFF",
        "F00000F",
        "FFF0FFF",
        "00F0F00",
        "00F0FFF",
    ]

    OPPOSITE: dict[int, int] = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST,
    }

    DELTA: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        EAST: (1, 0),
        SOUTH: (0, 1),
        WEST: (-1, 0),
    }

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None,
        perfect: bool = True,
        show_pattern: bool = True,
        pattern_text: str = "42"
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self._blocked: set[tuple[int, int]] = set()
        self.seed: int = seed if seed is not None else random.randint(0, 2**31)
        self.perfect: bool = perfect
        self.grid: list[list[int]] = []
        self._generated: bool = False
        self._show_pattern: bool = show_pattern
        self._pattern: list[str] = text_to_pattern(pattern_text)

    def _init_grid(self) -> None:
        closed: int = self.NORTH | self.SOUTH | self.EAST | self.WEST
        self.grid = [[closed for _ in range(self.width)]
                     for _ in range(self.height)]

    def _remove_wall(
        self,
        x1: int, y1: int, wto_open1: int,
        x2: int, y2: int, wto_open2: int
    ) -> None:
        self.grid[y1][x1] &= ~wto_open1
        self.grid[y2][x2] &= ~wto_open2

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _require_generated(self) -> None:
        if not self._generated:
            raise RuntimeError(
                "Maze has not been generated yet."
                " Call generate() before accessing maze data."
            )

    def get_cell(self, x: int, y: int) -> int:
        self._require_generated()
        if not self._in_bounds(x, y):
            raise IndexError(
                f"Cell coordinates ({x}, {y}) are out of bounds"
                f" for a {self.width}x{self.height} maze."
            )
        return self.grid[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        if direction not in self.DELTA:
            valid = ", ".join(str(d) for d in self.DELTA)
            raise ValueError(
                f"Invalid direction constant {direction}."
                f" Valid values are: {valid}."
            )
        cell: int = self.get_cell(x, y)
        return (cell & direction) != 0

    def _has_wall_internal(self, x: int, y: int, direction: int) -> bool:
        if not self._in_bounds(x, y):
            return True
        return (self.grid[y][x] & direction) != 0

    def to_hex_lines(self) -> list[str]:
        self._require_generated()
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]

    def generate(self) -> None:
        self._init_grid()
        random.seed(self.seed)
        if self._show_pattern:
            self._carve_pattern42()
        if self.entry in self._blocked:
            raise ValueError(
                f"Entry point {self.entry} overlaps with the '42' pattern. "
                f"Choose a different entry position."
            )
        if self.exit in self._blocked:
            raise ValueError(
                f"Exit point {self.exit} overlaps with the '42' pattern. "
                f"Choose a different exit position."
            )
        self._generate_dfs()
        if not self.perfect:
            self._add_extra_passages()
        self._generated = True

    def _carve_pattern42(self) -> None:
        pattern_height = len(self._pattern)
        if pattern_height == 0:
            return
        pattern_width = len(self._pattern[0])

        if self.width < pattern_width or self.height < pattern_height:
            from display.color import Color
            print(
                Color.warning(
                    f"Maze too small ({self.width}x{self.height})"
                    f" to embed '42' pattern"
                    f" (needs {pattern_width}x{pattern_height})."
                ),
                file=sys.stderr,
            )
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        for r, row_str in enumerate(self._pattern):
            for c, hex_char in enumerate(row_str):
                if hex_char == "1":
                    y = start_y + r
                    x = start_x + c
                    if self._in_bounds(x, y):
                        self._blocked.add((x, y))

    def _generate_dfs(self) -> None:
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}

        while stack:
            current_x, current_y = stack[-1]
            neighbors = []
            for direction, (dx, dy) in self.DELTA.items():
                nx = current_x + dx
                ny = current_y + dy
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in visited
                    and (nx, ny) not in self._blocked
                ):
                    neighbors.append((nx, ny, direction))

            if neighbors:
                next_x, next_y, direction = random.choice(neighbors)
                self._remove_wall(
                    current_x,
                    current_y,
                    direction,
                    next_x,
                    next_y,
                    self.OPPOSITE[direction]
                )
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def _add_extra_passages(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                directions = list(self.DELTA.items())
                random.shuffle(directions)
                for direction, (dx, dy) in directions:
                    nx, ny = x + dx, y + dy
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self._blocked
                        and self._has_wall_internal(x, y, direction)
                        and random.random() < 0.5
                    ):
                        self._remove_wall(
                            x, y, direction,
                            nx, ny, self.OPPOSITE[direction],
                        )
                    break
