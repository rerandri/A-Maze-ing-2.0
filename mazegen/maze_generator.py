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
    "": ["00000", "00000", "00000", "00000", "00000"],
}


def text_to_pattern(text: str) -> list[str]:
    """Convert a text string into a 5-row bitmap pattern (list of str)."""
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
    """Generates and solves mazes using DFS-based recursive backtracking.

    Supports perfect (tree) and imperfect (loops) mazes, optional bitmap
    pattern embedding, hex export, and BFS solution.
    """
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

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
        """Initialise maze dimensions, entry/exit, seed and pattern options."""
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
        self._pattern_text: str = pattern_text
        self._solution: list[str] = []

    def _init_grid(self) -> None:
        """Initialise the grid with all walls closed (bitmask 15)."""
        closed: int = self.NORTH | self.SOUTH | self.EAST | self.WEST
        self.grid = [[closed for _ in range(self.width)]
                     for _ in range(self.height)]

    def _remove_wall(
        self,
        x1: int, y1: int, wto_open1: int,
        x2: int, y2: int, wto_open2: int
    ) -> None:
        """Remove walls between two adjacent cells by clearing direction bits."""
        self.grid[y1][x1] &= ~wto_open1
        self.grid[y2][x2] &= ~wto_open2

    def _in_bounds(self, x: int, y: int) -> bool:
        """Check if (x, y) is within the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _require_generated(self) -> None:
        if not self._generated:
            raise RuntimeError(
                "Maze has not been generated yet."
                " Call generate() before accessing maze data."
            )

    def get_cell(self, x: int, y: int) -> int:
        """Return the wall bitmask for cell (x, y)."""
        self._require_generated()
        if not self._in_bounds(x, y):
            raise IndexError(
                f"Cell coordinates ({x}, {y}) are out of bounds"
                f" for a {self.width}x{self.height} maze."
            )
        return self.grid[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """Return True if the wall in *direction* is still present at (x, y)."""
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
        """Export the grid as hex-encoded strings (one per row)."""
        self._require_generated()
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]

    def generate(self) -> None:
        """Generate the maze: carve pattern, run DFS, optionally add loops."""
        self._init_grid()
        random.seed(self.seed)
        if self._show_pattern:
            self._carve_pattern42()
        if self.entry in self._blocked:
            raise ValueError(
                f"Entry point {self.entry} overlaps with the "
                f"'{self._pattern_text}' pattern. "
                f"Choose a different entry position."
            )
        if self.exit in self._blocked:
            raise ValueError(
                f"Exit point {self.exit} overlaps with the "
                f"'{self._pattern_text}' pattern. "
                f"Choose a different exit position."
            )
        self._generate_dfs()
        if not self.perfect:
            self._add_extra_passages()
        self._generated = True

    def solve(self) -> list[str]:
        """BFS from entry to exit; returns a list of N/E/S/W directions."""
        from collections import deque
        queue: deque[tuple[int, int]] = deque([self.entry])
        parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {
            self.entry: ((-1, -1), 0)
        }
        rev = {
            self.NORTH: "N", self.EAST: "E",
            self.SOUTH: "S", self.WEST: "W",
        }

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                path: list[str] = []
                curr = self.exit
                while curr != self.entry:
                    prev, direc = parent[curr]
                    path.append(rev[direc])
                    curr = prev
                path.reverse()
                self._solution = path
                return path
            for direc, (dx, dy) in self.DELTA.items():
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny) \
                   and not self._has_wall_internal(x, y, direc) \
                   and (nx, ny) not in parent:
                    parent[(nx, ny)] = ((x, y), direc)
                    queue.append((nx, ny))
        return []

    def _carve_pattern42(self) -> None:
        """Mark cells blocked by the bitmap pattern (centred on the grid)."""
        pattern_height = len(self._pattern)
        if pattern_height == 0:
            return
        pattern_width = len(self._pattern[0])

        if self.width < pattern_width or self.height < pattern_height:
            sys.stderr.write(
                f"Error: Maze too small ({self.width}x{self.height})"
                f" to embed '{self._pattern_text}' pattern"
                f" (needs {pattern_width}x{pattern_height}).\n"
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
        """Recursive backtracking (DFS) that carves the maze passage."""
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
        """Add loops and reduce dead-ends to create an imperfect maze."""
        self._open_special_cells()
        loop_target = max(5, self.width * self.height // 50)
        self._carve_loops(min_loops=loop_target)
        self._reduce_dead_ends(max_dead_ends=2)

    def _find_dead_ends(self) -> list[tuple[int, int]]:
        """Return all degree-1 cells (three walls)."""
        dead_ends: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                if bin(self.grid[y][x]).count('1') == 3:
                    dead_ends.append((x, y))
        return dead_ends

    def _reduce_dead_ends(self, max_dead_ends: int = 2) -> None:
        """Open walls to reduce dead-ends to at most *max_dead_ends*."""
        dead_ends = self._find_dead_ends()
        random.shuffle(dead_ends)
        for cx, cy in dead_ends:
            if len(self._find_dead_ends()) <= max_dead_ends:
                break
            for direction, (dx, dy) in self.DELTA.items():
                nx, ny = cx + dx, cy + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in self._blocked:
                    if self._has_wall_internal(cx, cy, direction):
                        self._remove_wall(
                            cx, cy, direction,
                            nx, ny, self.OPPOSITE[direction],
                        )
                        break

    def _open_special_cells(self) -> None:
        """Open at least two walls from each corner cell."""
        cells = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
        for cx, cy in cells:
            if (cx, cy) in self._blocked:
                self._blocked.remove((cx, cy))
            walls = [
                (d, dx, dy) for d, (dx, dy) in self.DELTA.items()
                if self._in_bounds(cx + dx, cy + dy)
                and (cx + dx, cy + dy) not in self._blocked
            ]
            random.shuffle(walls)
            opened = 0
            for direction, dx, dy in walls:
                if opened >= 2:
                    break
                nx, ny = cx + dx, cy + dy
                if self._has_wall_internal(cx, cy, direction):
                    self._remove_wall(
                        cx, cy, direction,
                        nx, ny, self.OPPOSITE[direction],
                    )
                    opened += 1
                else:
                    opened += 1

    def _carve_loops(self, min_loops: int) -> None:
        """Carve at least *min_loops* additional passages to form loops."""
        candidates: list[tuple[int, int, int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                for direction, (dx, dy) in self.DELTA.items():
                    nx, ny = x + dx, y + dy
                    if self._in_bounds(nx, ny) \
                       and (nx, ny) not in self._blocked \
                       and self._has_wall_internal(x, y, direction):
                        candidates.append((x, y, direction, nx, ny))
        random.shuffle(candidates)
        loops = 0
        seen: set[frozenset[tuple[int, int]]] = set()
        for x, y, direction, nx, ny in candidates:
            pair = frozenset([(x, y), (nx, ny)])
            if pair in seen:
                continue
            self._remove_wall(
                x, y, direction,
                nx, ny, self.OPPOSITE[direction],
            )
            seen.add(pair)
            loops += 1
            if loops >= min_loops:
                break
