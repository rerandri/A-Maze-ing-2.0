from collections import deque
from mazegen import MazeGenerator


class Solve_bfs:
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    DELTA: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        EAST: (1, 0),
        SOUTH: (0, 1),
        WEST: (-1, 0),
    }

    def __init__(self, Maze: MazeGenerator) -> None:
        self.maze = Maze
        self._solution: list[str] = []
        self._visited_count: int = 0

    def _solve_bfs(self) -> list[str]:
        queue: deque[tuple[int, int]] = deque([self.maze.entry])
        parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {
            self.maze.entry: ((-1, -1), 0)
        }

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.maze.exit:
                self._visited_count = len(parent)
                path: list[str] = []
                curr = self.maze.exit
                while curr != self.maze.entry:
                    prev, direction = parent[curr]
                    direction_names = {
                        self.NORTH: "N",
                        self.SOUTH: "S",
                        self.EAST: "E",
                        self.WEST: "W"
                    }
                    path.append(direction_names.get(direction, "_"))
                    curr = prev
                path.reverse()
                self._solution = path
                return self._solution

            for direction, (dx, dy) in self.DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.maze._in_bounds(nx, ny)
                    and not self.maze._has_wall_internal(x, y, direction)
                    and (nx, ny) not in parent
                ):
                    parent[(nx, ny)] = ((x, y), direction)
                    queue.append((nx, ny))
        self._visited_count = len(parent)
        return self._solution

    def get_solution(self) -> list[str]:
        solution_path: list[str] = self._solve_bfs()
        return solution_path

    def get_step_count(self) -> int:
        if not self._solution:
            self._solve_bfs()
        return len(self._solution)

    def get_visited_count(self) -> int:
        if not self._solution:
            self._solve_bfs()
        return self._visited_count

    def get_direction_counts(self) -> dict[str, int]:
        if not self._solution:
            self._solve_bfs()
        counts: dict[str, int] = {"N": 0, "E": 0, "S": 0, "W": 0}
        for move in self._solution:
            if move in counts:
                counts[move] += 1
        return counts

    def get_direction_changes(self) -> int:
        if not self._solution:
            self._solve_bfs()
        changes: int = 0
        for i in range(1, len(self._solution)):
            if self._solution[i] != self._solution[i - 1]:
                changes += 1
        return changes
