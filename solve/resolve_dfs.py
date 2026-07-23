from collections import deque
from mazegen import MazeGenerator


class Solve_bfs:
    """BFS solver that computes the shortest path and traversal statistics."""

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

    def __init__(self, maze: MazeGenerator) -> None:
        """Solve the maze and pre-compute direction/visit statistics."""
        self.maze = maze
        self._solution = maze.solve()
        self._visited_count = 0
        self._direction_counts: dict[str, int] = {}
        self._direction_changes = 0
        self._compute_stats()

    def _compute_stats(self) -> None:
        """Count BFS-visited cells, direction breakdown, and changes."""
        queue: deque[tuple[int, int]] = deque([self.maze.entry])
        visited: set[tuple[int, int]] = {self.maze.entry}
        while queue:
            x, y = queue.popleft()
            if (x, y) == self.maze.exit:
                self._visited_count = len(visited)
                break
            for direction, (dx, dy) in self.DELTA.items():
                nx, ny = x + dx, y + dy
                if self.maze._in_bounds(nx, ny) \
                   and not self.maze._has_wall_internal(x, y, direction) \
                   and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        else:
            self._visited_count = len(visited)

        self._direction_counts = {"N": 0, "E": 0, "S": 0, "W": 0}
        for move in self._solution:
            if move in self._direction_counts:
                self._direction_counts[move] += 1

        self._direction_changes = 0
        for i in range(1, len(self._solution)):
            if self._solution[i] != self._solution[i - 1]:
                self._direction_changes += 1

    def get_solution(self) -> list[str]:
        """Return the list of N/E/S/W moves from entry to exit."""
        return self._solution

    def get_step_count(self) -> int:
        """Return the number of steps in the solution."""
        return len(self._solution)

    def get_visited_count(self) -> int:
        """Return how many cells BFS explored before finding the exit."""
        return self._visited_count

    def get_direction_counts(self) -> dict[str, int]:
        """Return a dict mapping N/E/S/W to their frequency in the solution."""
        return self._direction_counts

    def get_direction_changes(self) -> int:
        """Return how many times the direction changes along the solution."""
        return self._direction_changes
