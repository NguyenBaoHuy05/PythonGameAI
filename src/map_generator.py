import random
from collections import deque

ROWS, COLS = 31, 28
WALL_RATIO = 0.3


def is_valid(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def neighbors(r, c):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if is_valid(nr, nc):
            yield nr, nc


def bfs_check_connectivity(grid):
    visited = [[False] * COLS for _ in range(ROWS)]
    start = None

    # Tìm ô đầu tiên không phải tường
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] != "#":
                start = (r, c)
                break
        if start:
            break
    if not start:
        return False

    q = deque([start])
    visited[start[0]][start[1]] = True
    count = 1
    total_free = sum(
        row.count(".")
        + row.count("o")
        + row.count("M")
        + row.count("C")
        + row.count("I")
        + row.count("B")
        + row.count("P")
        for row in grid
    )

    while q:
        r, c = q.popleft()
        for nr, nc in neighbors(r, c):
            if not visited[nr][nc] and grid[nr][nc] != "#":
                visited[nr][nc] = True
                q.append((nr, nc))
                count += 1

    return count == total_free


def has_dead_end(grid):
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            if grid[r][c] != "#":
                open_neighbors = sum(
                    1 for nr, nc in neighbors(r, c) if grid[nr][nc] != "#"
                )
                if open_neighbors <= 1:
                    return True
    return False


def create_map():
    grid = [["." for _ in range(COLS)] for _ in range(ROWS)]

    for r in range(ROWS):
        grid[r][0] = "#"
        grid[r][COLS - 1] = "#"
    for c in range(COLS):
        grid[0][c] = "#"
        grid[ROWS - 1][c] = "#"

    wall_cells = int(ROWS * COLS * WALL_RATIO)
    placed_walls = 0
    attempts = 0
    max_attempts = wall_cells * 5

    while placed_walls < wall_cells and attempts < max_attempts:
        r = random.randint(1, ROWS - 2)
        c = random.randint(1, COLS - 2)
        if grid[r][c] == ".":
            grid[r][c] = "#"
            if bfs_check_connectivity(grid) and not has_dead_end(grid):
                placed_walls += 1
            else:
                grid[r][c] = "."
        attempts += 1

    pellet_positions = [
        (1, 1),
        (1, COLS - 2),
        (ROWS - 2, 1),
        (ROWS - 2, COLS - 2),
    ]
    for r, c in pellet_positions:
        grid[r][c] = "o"

    mid_r, mid_c = ROWS // 2 + 2, COLS // 2
    grid[mid_r][mid_c] = "M"

    ghost_row = ROWS // 2
    ghost_positions = [
        (ghost_row, COLS // 2 - 2),
        (ghost_row, COLS // 2 - 1),
        (ghost_row, COLS // 2),
        (ghost_row, COLS // 2 + 1),
    ]
    ghosts = ["C", "I", "B", "P"]
    for (r, c), g in zip(ghost_positions, ghosts):
        grid[r][c] = g

    return grid


def print_map(grid):
    for row in grid:
        print("".join(row))


if __name__ == "__main__":
    random.seed(42)
    game_map = create_map()
    print_map(game_map)
