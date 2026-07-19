import random
import select
import shutil
import sys
import os
import time

from .color import Color
from mazegen import MazeGenerator
from solve import Solve_bfs


class AsciiRenderer:
    ANIM_DURATION: float = 2.5

    def __init__(
            self,
            maze: MazeGenerator,
            delay: float = 0.0,
            animate_reveal: bool = True
    ) -> None:
        self.maze: MazeGenerator = maze
        self.delay: float = delay

        t0: float = time.time()
        self.solve = Solve_bfs(maze)
        self._step_count = len(self.solve.get_solution())
        self._solve_time: float = time.time() - t0
        self._gen_time: float = 0.0
        self._bfs_visited = self.solve.get_visited_count()
        self._direction_counts = self.solve.get_direction_counts()
        self._direction_changes = self.solve.get_direction_changes()

        self._last_render_lines: int = 0
        self.count_invalid_inputs: int = 0
        self.show_path: bool = False
        self.animate_reveal: bool = animate_reveal

        self.c: Color = Color()

        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.wall = combinaison[idx][0] + "██" + self.c.end()
        self.way = self.c.rgb(255, 105, 180) + "██" + self.c.end()

        self.player: str = self.c.rgb(0, 255, 255) + "██" + self.c.end()
        self.blocked: str = self.c.rgb(255, 255, 0) + "██" + self.c.end()
        self.path: str = self.c.rgb(0, 255, 0) + "██" + self.c.end()
        self.start: str = self.c.rgb(00, 00, 255) + "██" + self.c.end()
        self.end: str = self.c.rgb(255, 00, 00) + "██" + self.c.end()

    def _build_pixels(self) -> list[list[str]]:
        cols: int = self.maze.width * 2 + 1
        rows: int = self.maze.height * 2 + 1
        pixels: list[list[str]] = [
            [self.wall for _ in range(cols)] for _ in range(rows)
        ]

        for y in range(self.maze.height):
            for x in range(self.maze.width):

                if (x, y) in self.maze._blocked:
                    pixels[2 * y + 1][2 * x + 1] = self.blocked
                else:
                    pixels[2 * y + 1][2 * x + 1] = self.way

                if not self.maze.has_wall(x, y, MazeGenerator.NORTH):
                    pixels[2 * y][2 * x + 1] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.SOUTH):
                    pixels[2 * y + 2][2 * x + 1] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.EAST):
                    pixels[2 * y + 1][2 * x + 2] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.WEST):
                    pixels[2 * y + 1][2 * x] = self.way

        return pixels

    def _maze_fits(self) -> bool:
        term_cols, term_lines = shutil.get_terminal_size(fallback=(80, 24))
        needed_cols = self.maze.width * 2 + 1
        needed_lines = self.maze.height * 2 + 1
        return term_cols >= needed_cols and term_lines >= needed_lines

    def _flush_render(self, pixels: list[list[str]]) -> None:
        output = "\n".join("".join(row) for row in pixels)
        preamble = "\033[H" if self._last_render_lines > 0 else ""
        sys.stdout.write(preamble + output + "\n\033[0J")
        sys.stdout.flush()
        self._last_render_lines = len(pixels)

    @staticmethod
    def _reveal_chunk_size(maze_width: int) -> int:
        thresholds = [(130, 16), (100, 8), (80, 4), (60, 2), (40, 2)]
        for limit, chunk in thresholds:
            if maze_width >= limit:
                return chunk
        return 1

    def _animate_reveal(self, pixels: list[list[str]]) -> None:
        total_rows = len(pixels)
        chunk = self._reveal_chunk_size(self.maze.width)
        center = total_rows // 2

        row_order = sorted(range(total_rows), key=lambda r: abs(r - center))
        steps = (total_rows + chunk - 1) // chunk
        step_delay = self.ANIM_DURATION / steps

        width = len(pixels[0])
        canvas = [
            [self.wall for _ in range(width)] for _ in range(total_rows)
        ]

        revealed: set[int] = set()
        for i in range(0, total_rows, chunk):
            batch = row_order[i:i + chunk]
            for r in batch:
                canvas[r] = pixels[r]
                revealed.add(r)
            self._flush_render(canvas)
            time.sleep(step_delay)

        self._flush_render(pixels)

    def display(
        self, show_path: bool = False, animate: bool | None = None
    ) -> None:
        self.show_path = show_path
        if animate is None:
            animate = self.animate_reveal

        if not self._maze_fits():
            needed_cols = self.maze.width * 2 + 1
            needed_lines = self.maze.height * 2 + 1
            term_cols, term_lines = shutil.get_terminal_size(fallback=(80, 24))
            print(
                Color.error(
                    f"Terminal too small"
                    f" ({term_cols}x{term_lines}) to display"
                    f" maze (needs {needed_cols}x{needed_lines})."
                    " Resize and try again."
                ),
                flush=True,
            )
            return

        entry_x, entry_y = self.maze.entry
        exit_x, exit_y = self.maze.exit
        pixels: list[list[str]] = self._build_pixels()
        pixels[2 * entry_y + 1][2 * entry_x + 1] = self.start
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end

        self._last_render_lines = 0

        if animate:
            self._animate_reveal(pixels)
        else:
            self._flush_render(pixels)

        if not show_path:
            return

        curr_x, curr_y = self.maze.entry
        for move in self.solve.get_solution():
            if move == "N":
                pixels[2 * curr_y][2 * curr_x + 1] = self.path
                curr_y -= 1
            elif move == "S":
                pixels[2 * curr_y + 2][2 * curr_x + 1] = self.path
                curr_y += 1
            elif move == "E":
                pixels[2 * curr_y + 1][2 * curr_x + 2] = self.path
                curr_x += 1
            elif move == "W":
                pixels[2 * curr_y + 1][2 * curr_x] = self.path
                curr_x -= 1
            pixels[2 * curr_y + 1][2 * curr_x + 1] = self.path
            self._flush_render(pixels)
            time.sleep(self.delay)

        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end
        self._flush_render(pixels)

    def _menu_prompt(self) -> str | None:
        """Return user input, or None on interrupt."""
        path_on = '[ON]' if self.show_path else '[OFF]'
        anim_on = '[ON]' if self.animate_reveal else '[OFF]'
        print("\n\033[1m=== A-Maze-ing ===\033[0m")
        print(
            f" [1].Re-generate maze\n"
            f" [2].Display maze\n"
            f" [3].Show path: {path_on}\n"
            f" [4].Reveal animation: {anim_on}\n"
            f" [5].Rotate maze colors\n"
            f" [6].Cycle '42' pattern colors")
        print(" [7].Quit")
        print(" [8].Play maze")

        print(self.c.info("\nType /help for more commands."))
        try:
            print("\033[1mMaze>> \033[0m", end="", flush=True)
            return input().strip(' ')
        except (KeyboardInterrupt, EOFError):
            print(Color.info("\nOperation cancelled.\n"))
            return None

    def _handle_regenerate(self) -> None:
        os.system('clear')
        self.maze.seed = random.randint(0, 2**32)
        self.maze._generated = False
        t0: float = time.time()
        self.maze.generate()
        self._gen_time = time.time() - t0
        t0 = time.time()
        self.solve = Solve_bfs(self.maze)
        self._solve_time = time.time() - t0
        self._step_count = len(self.solve.get_solution())
        self._bfs_visited = self.solve.get_visited_count()
        self._direction_counts = self.solve.get_direction_counts()
        self._direction_changes = self.solve.get_direction_changes()
        self.display(show_path=self.show_path)

    def _handle_display(self) -> None:
        os.system('clear')
        self.display(show_path=self.show_path)
        self.header()

    def _handle_toggle_path(self) -> None:
        os.system('clear')
        self.show_path = not self.show_path
        self.display(show_path=self.show_path, animate=False)
        self.header()

    def _handle_toggle_animation(self) -> None:
        os.system('clear')
        self.animate_reveal = not self.animate_reveal
        state = 'enabled' if self.animate_reveal else 'disabled'
        print(f"Reveal animation {state}.\n")

    def _handle_rotate_colors(self) -> None:
        os.system('clear')
        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.show_path = False
        self.wall = combinaison[idx][0] + "██" + self.c.end()
        self.way = combinaison[idx][1] + "██" + self.c.end()
        self.display(show_path=self.show_path, animate=False)

    def _handle_cycle_blocked(self) -> None:
        os.system('clear')
        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.show_path = False
        self.blocked = combinaison[idx][0] + "██" + self.c.end()
        self.display(show_path=self.show_path, animate=False)

    def _handle_delay(self, value: str) -> None:
        print(Color.info(
            f"Setting animation delay... {value}"
        ))
        try:
            tmp_delay = float(value)
            if tmp_delay < 0.0:
                raise ValueError("Delay cannot be negative.")
            self.delay = tmp_delay
            if self.delay > 0.1:
                print(Color.warning(
                    f"Delay {self.delay}s is quite long. Consider using a "
                    f"smaller value for a better experience."
                ))
            print(Color.success(
                f"Animation delay set to {self.delay}s.\n"
            ))
        except ValueError:
            print(Color.error("Invalid delay value. Enter a valid number.\n"))

    def _handle_clear(self) -> None:
        os.system('clear')

    def _handle_help(self) -> None:
        os.system('clear')
        show_help()

    def _handle_info(self) -> None:
        os.system('clear')
        temp_delay = self.delay
        if self.show_path:
            self.delay = 0.0
        self.display(show_path=self.show_path, animate=False)
        self.delay = temp_delay
        self.header()

    def _handle_quit(self) -> bool:
        print(Color.info(" ... Exiting Terminal Interface ...\n"))
        return True

    def _handle_set_colors(self) -> None:
        os.system('clear')
        c = self.c
        succ = Color.success

        print(f"┌─── {c.info('Set Custom Colors')} " + "─" * 44)
        print("│")
        print(f"│ {c.info('=== Current Colors ===')}")
        print(f"│   Wall:    {self.wall}")
        print(f"│   Blocked: {self.blocked}")
        print("│")
        print("│ Enter three integers 0-255, comma-separated:  R, G, B")
        print("│ Examples:  255, 0, 0  =  Red    0, 255, 0  =  Green")
        print("│")
        try:
            wall_str = input("│ Wall color (RGB): ")
            self.wall = (
                self.c.rgb(*map(int, wall_str.split(',')))
                + "██" + self.c.end()
            )
            print(f"│ {succ('Wall color set.')}  {self.wall}")
            print("│")
            blocked_str = input("│ Blocked color (RGB): ")
            self.blocked = (
                self.c.rgb(*map(int, blocked_str.split(',')))
                + "██" + self.c.end()
            )
            print(f"│ {succ('Blocked color set.')}  {self.blocked}")
            print("│")
            print(f"│ {succ('Colors updated successfully.')}")
        except (ValueError, IndexError) as e:
            print(f"│ {Color.error(f'Invalid RGB format: {e}')}")
        except Exception as e:
            print(f"│ {Color.error(f'Error: {e}')}")
        print("│")
        print("└" + "─" * 60)

    def _read_key(self) -> str:
        fd = sys.stdin.fileno()
        b = os.read(fd, 1)
        if not b:
            return '\x1b'
        if b == b'\x1b':
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                b2 = os.read(fd, 1)
                if b2 == b'[':
                    r, _, _ = select.select([fd], [], [], 0.1)
                    if r:
                        b3 = os.read(fd, 1)
                        if b3 == b'A':
                            return 'up'
                        if b3 == b'B':
                            return 'down'
                        if b3 == b'C':
                            return 'right'
                        if b3 == b'D':
                            return 'left'
        return b.decode('utf-8', errors='replace')

    def _handle_play(self) -> None:
        import tty
        import termios

        if not sys.stdin.isatty():
            print(Color.error("Play mode requires a terminal.\n"))
            return

        os.system('clear')
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        self._last_render_lines = 0

        try:
            tty.setcbreak(fd)

            player_x, player_y = self.maze.entry
            steps = 0
            start_time = time.time()
            show_solution = False

            while True:
                entry_x, entry_y = self.maze.entry
                exit_x, exit_y = self.maze.exit
                pixels = self._build_pixels()
                pixels[2 * entry_y + 1][2 * entry_x + 1] = self.start
                pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end

                if show_solution:
                    curr_x, curr_y = self.maze.entry
                    for move in self.solve.get_solution():
                        if move == "N":
                            pixels[2 * curr_y][2 * curr_x + 1] = self.path
                            curr_y -= 1
                        elif move == "S":
                            pixels[2 * curr_y + 2][2 * curr_x + 1] = self.path
                            curr_y += 1
                        elif move == "E":
                            pixels[2 * curr_y + 1][2 * curr_x + 2] = self.path
                            curr_x += 1
                        elif move == "W":
                            pixels[2 * curr_y + 1][2 * curr_x] = self.path
                            curr_x -= 1
                        pixels[2 * curr_y + 1][2 * curr_x + 1] = self.path

                pixels[2 * player_y + 1][2 * player_x + 1] = self.player

                sys.stdout.write("\033[H")
                for row in pixels:
                    sys.stdout.write("".join(row) + "\r\n")
                sys.stdout.write("\033[0J")

                elapsed = time.time() - start_time
                sys.stdout.write(
                    f" Steps: {steps}"
                    f"  |  Time: {elapsed:.1f}s"
                    f"  |  Optimal: {self._step_count}\r\n"
                )
                sys.stdout.write(
                    f" {self.c.info('[↑↓←→] Move')}"
                    f"  {self.c.info('[P] Path')}"
                    f"  {self.c.info('[H] Help')}"
                    f"  {self.c.info('[Q] Quit')}\r\n"
                )
                sys.stdout.flush()

                if (player_x, player_y) == self.maze.exit:
                    sys.stdout.write("\r\n")
                    sys.stdout.write(
                        f" {Color.success('Congratulations!')}"
                        f" You reached the exit!\r\n"
                    )
                    sys.stdout.write(
                        f" Steps: {steps}  |"
                        f" Optimal: {self._step_count}  |"
                        f" Time: {elapsed:.1f}s\r\n"
                    )
                    if steps <= self._step_count:
                        sys.stdout.write(
                            f" {Color.success('Perfect!')}"
                            f" You found the optimal path!\r\n"
                        )
                    sys.stdout.write(
                        "\r\n Press any key to return to menu..."
                    )
                    sys.stdout.flush()
                    self._read_key()
                    break

                key = self._read_key()

                if key in ('q', 'Q', '\x1b'):
                    break
                if key in ('p', 'P'):
                    show_solution = not show_solution
                if key in ('h', 'H'):
                    sys.stdout.write("\r\n")
                    sys.stdout.write(
                        " Controls: ↑ Up  |  ↓ Down"
                        "  |  ← Left  |  → Right\r\n"
                    )
                    sys.stdout.write(
                        " P: Toggle solution path"
                        "  |  Q: Quit to menu\r\n"
                    )
                    sys.stdout.write(" Press any key to continue...")
                    sys.stdout.flush()
                    self._read_key()

                dx, dy, direction = 0, 0, 0
                if key == 'up':
                    dy, direction = -1, MazeGenerator.NORTH
                elif key == 'down':
                    dy, direction = 1, MazeGenerator.SOUTH
                elif key == 'left':
                    dx, direction = -1, MazeGenerator.WEST
                elif key == 'right':
                    dx, direction = 1, MazeGenerator.EAST

                if direction != 0:
                    new_x, new_y = player_x + dx, player_y + dy
                    in_bounds = self.maze._in_bounds(new_x, new_y)
                    no_wall = not self.maze.has_wall(
                        player_x, player_y, direction
                    )
                    if in_bounds and no_wall:
                        player_x, player_y = new_x, new_y
                        steps += 1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            os.system('clear')

    @staticmethod
    def _build_bar(value: float, max_val: float, width: int = 24) -> str:
        filled = int(min(value / max_val * width if max_val > 0 else 0, width))
        return "█" * filled + "░" * (width - filled)

    def _handle_benchmark(self) -> None:
        os.system('clear')

        seed = self.maze.seed
        w, h = self.maze.width, self.maze.height
        total_cells = w * h - len(self.maze._blocked)

        deg1 = deg2 = deg34 = 0
        total_open = 0
        for y in range(h):
            for x in range(w):
                if (x, y) in self.maze._blocked:
                    continue
                walls = bin(self.maze.get_cell(x, y)).count('1')
                total_open += 4 - walls
                if walls == 3:
                    deg1 += 1
                elif walls == 2:
                    deg2 += 1
                else:
                    deg34 += 1

        entry_x, entry_y = self.maze.entry
        exit_x, exit_y = self.maze.exit
        pixels = self._build_pixels()
        pixels[2 * entry_y + 1][2 * entry_x + 1] = self.start
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end

        curr_x, curr_y = self.maze.entry
        for move in self.solve.get_solution():
            if move == "N":
                pixels[2 * curr_y][2 * curr_x + 1] = self.path
                curr_y -= 1
            elif move == "S":
                pixels[2 * curr_y + 2][2 * curr_x + 1] = self.path
                curr_y += 1
            elif move == "E":
                pixels[2 * curr_y + 1][2 * curr_x + 2] = self.path
                curr_x += 1
            elif move == "W":
                pixels[2 * curr_y + 1][2 * curr_x] = self.path
                curr_x -= 1
            pixels[2 * curr_y + 1][2 * curr_x + 1] = self.path
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end

        for row in pixels:
            sys.stdout.write("".join(row) + "\n")
        sys.stdout.flush()

        dir_max = max(self._direction_counts.values())
        topo_max = max(deg1, deg2, deg34)
        manhattan = (
            abs(self.maze.exit[0] - self.maze.entry[0])
            + abs(self.maze.exit[1] - self.maze.entry[1])
        )
        bar_w = 24
        c = self.c
        succ = Color.success

        print(f"┌─── {c.info(f'Benchmark [Seed: {seed}]')} " + "─" * 36)
        print("│")
        print(f"│ {c.info('=== Time ===')}")
        print(f"│   Generation:       {succ(f'{self._gen_time:.3f}s')}")
        print(f"│   Solve (BFS):      {succ(f'{self._solve_time:.3f}s')}")
        print("│")
        print(f"│ {c.info('=== Solution ===')}")
        print(f"│   Path length:      {self._step_count} steps")
        print(f"│   Manhattan dist.:  {manhattan} steps")
        path_ratio = (
            f"{self._step_count / manhattan:.2f}" if manhattan > 0 else "N/A"
        )
        print(f"│   Path ratio:       {path_ratio}")
        print(f"│   Direction changes:{self._direction_changes}")
        print("│")
        print(f"│ {c.info('=== Direction Breakdown ===')}")
        for d in ("N", "E", "S", "W"):
            count = self._direction_counts.get(d, 0)
            bar = self._build_bar(count, dir_max, bar_w)
            print(f"│   {d}: {bar}  {count}")
        print("│")
        print(f"│ {c.info(f'=== Topology ({total_cells} cells) ===')}")
        b1 = self._build_bar(deg1, topo_max, bar_w)
        b2 = self._build_bar(deg2, topo_max, bar_w)
        b3 = self._build_bar(deg34, topo_max, bar_w)
        d1_pct = f"{deg1 / total_cells * 100:.1f}%"
        d2_pct = f"{deg2 / total_cells * 100:.1f}%"
        d34_pct = f"{deg34 / total_cells * 100:.1f}%"
        print(f"│   Degree-1 (dead ends):       {deg1:<4} {b1}  {d1_pct}")
        d2_line = f"│   Degree-2 (corridors):       {deg2:<4} {b2}  {d2_pct}"
        print(d2_line)
        print(f"│   Degree-3/4 (intersections): {deg34:<4} {b3}  {d34_pct}")
        bf = total_open / total_cells
        print(f"│   Branching factor:           {bf:.2f}")
        print("│")
        print(f"│ {c.info('=== BFS Solver ===')}")
        print(f"│   Cells visited:  {self._bfs_visited} / {total_cells}")
        cov_bar = self._build_bar(self._bfs_visited, total_cells, bar_w)
        cov_pct = f"{self._bfs_visited / total_cells * 100:.1f}%"
        print(f"│   Coverage:       {cov_pct}  {cov_bar}")
        print("│")
        print("└" + "─" * 60)

        input(f"\n{c.info('Press Enter to return to menu...')}")

    def _handle_invalid(self) -> None:
        if self.count_invalid_inputs >= 4:
            os.system('clear')
            self.count_invalid_inputs = 0
        self.count_invalid_inputs += 1
        print(Color.error("Invalid choice.\n"))

    def run_iterative(self) -> None:
        self.wall = self.c.random_color() + "██" + self.c.end()

        while True:
            answer = self._menu_prompt()
            if answer is None:
                break
            if answer == "1":
                self._handle_regenerate()
            elif answer == "2":
                self._handle_display()
            elif answer == "3":
                self._handle_toggle_path()
            elif answer == "4":
                self._handle_toggle_animation()
            elif answer == "5":
                self._handle_rotate_colors()
            elif answer == "6":
                self._handle_cycle_blocked()
            elif answer.startswith("/delay ") or answer.startswith("/d "):
                delay_val = (
                    answer.removeprefix("/delay ")
                    .removeprefix("/d ").strip()
                )
                self._handle_delay(delay_val)
            elif answer in ("/clear", "/c"):
                self._handle_clear()
            elif answer in ("/help", "/h"):
                self._handle_help()
            elif answer in ("/info", "/i"):
                self._handle_info()
            elif answer in ("7", "quit", "exit"):
                if self._handle_quit():
                    break
            elif answer in ("/setcolors", "/sc"):
                self._handle_set_colors()
            elif answer in ("8", "/play", "/p"):
                self._handle_play()
            elif answer in ("/bench", "/b"):
                self._handle_benchmark()
            else:
                self._handle_invalid()

    def header(self) -> None:
        enter = self.start
        exit = self.end
        path = self.path
        print(
            "\033[1mInfo for maze:\033[0m\n"
            f"Entry : {enter} | Exit : {exit} | Path : {path}"
            f" | wall : {self.wall} | '42' pattern : {self.blocked}\n\n"
            f"Size : {self.maze.width} x {self.maze.height}\n"
            f"Steps to solve : {self._step_count}\n"

            f"Animation delay : {self.delay}s"
            f"\nReveal animation :"
            f" {'ON' if self.animate_reveal else 'OFF'}\n"
            f"Show path : {'ON' if self.show_path else 'OFF'}\n"
        )


def show_help() -> None:
    os.system('clear')
    info = Color.info
    print(f"┌─── {info('A-Maze-ing Help')} " + "─" * 48)
    print("│")
    print(f"│ {info('=== Menu Options ===')}")
    print("│   [1] Re-generate maze   Creates a new maze with random seed.")
    print("│   [2] Display maze       Shows the current maze in terminal.")
    print("│   [3] Show/Hide path     Toggles the solution path.")
    print("│   [4] Toggle reveal animation  Enables or disables animation.")
    print("│   [5] Rotate maze colors       Changes the wall color scheme.")
    print("│   [6] Cycle '42' pattern       Changes blocked cell colors.")
    print("│   [7] Quit               Exits the program.")
    print("│   [8] Play maze          Navigate with arrow keys.")
    print("│")
    print(f"│ {info('=== Play Mode Controls ===')}")
    print("│   ↑ ↓ ← →      Move the player through the maze.")
    print("│   P             Show/Hide the optimal solution path.")
    print("│   H             Show play mode controls.")
    print("│   Q / ESC       Quit play mode and return to menu.")
    print("│")
    print(f"│ {info('=== Commands ===')}")
    print("│   /clear  /c       Clears the screen.")
    print("│   /help   /h       Shows this help screen.")
    print("│   /delay <s>/d <s> Sets animation delay speed.")
    print("│   /info   /i       Shows maze information and legend.")
    print("│   /setcolors /sc   Sets custom colors for maze elements.")
    print("│   /play   /p       Play the maze manually.")
    print("│   /bench  /b       Maze statistics and benchmark.")
    print("│")
    print(f"│ {info('=== Color Reference (Color.rgb) ===')}")
    print("│   Color.rgb(R, G, B) sets a 24-bit terminal color.")
    print("│   Each value is an integer 0-255.")
    print("│   Examples:  255,   0,   0  =  Red")
    print("│               0, 255,   0  =  Green")
    print("│               0,   0, 255  =  Blue")
    print("│             255, 255,   0  =  Yellow")
    print("│   Enter values as comma-separated:  R, G, B")
    print("│")
    print("└" + "─" * 72)
