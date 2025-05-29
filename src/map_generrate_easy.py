import random
from collections import deque

ROWS, COLS = 31, 28
WALL_RATIO = 0.3

WALL_PATTERNS = [
    # (2, 1),
    (1, 1),
    (2, 1),
    # (4, 1),
    # (5, 1),
    # (6, 1),
    # (1, 2),
    # (1, 6),
    # (1, 4),
    # (1, 5),
    # (1, 6),
]


def is_valid(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def neighbors(r, c):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if is_valid(nr, nc):
            yield nr, nc


def bfs_connected_area(grid, start):
    visited = set([start])
    q = deque([start])
    count = 1
    while q:
        r, c = q.popleft()
        for nr, nc in neighbors(r, c):
            if (nr, nc) not in visited and grid[nr][nc] != "#":
                visited.add((nr, nc))
                q.append((nr, nc))
                count += 1
    return count


def get_total_free(grid):
    return sum(cell != "#" for row in grid for cell in row)


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


def place_wall_pattern(grid, r, c, h, w):
    coords = [(r + dr, c + dc) for dr in range(h) for dc in range(w)]
    if all(
        1 <= rr < ROWS - 1 and 1 <= cc < COLS - 1 and grid[rr][cc] == "."
        for rr, cc in coords
    ):
        for rr, cc in coords:
            grid[rr][cc] = "#"
        return coords
    return []


def remove_wall(coords, grid):
    for r, c in coords:
        grid[r][c] = "."


def create_map_easy():
    grid = [["." for _ in range(COLS)] for _ in range(ROWS)]

    for r in range(ROWS):
        grid[r][0] = "#"
        grid[r][COLS - 1] = "#"
    for c in range(COLS):
        grid[0][c] = "#"
        grid[ROWS - 1][c] = "#"

    total_wall = int(ROWS * COLS * WALL_RATIO)
    attempts = 0
    placed = 0
    max_attempts = total_wall * 4

    while placed < total_wall and attempts < max_attempts:
        h, w = random.choice(WALL_PATTERNS)
        r = random.randint(1, ROWS - h - 1)
        c = random.randint(1, COLS - w - 1)
        coords = place_wall_pattern(grid, r, c, h, w)
        if coords:
            for sr in range(ROWS):
                for sc in range(COLS):
                    if grid[sr][sc] != "#":
                        total_free = get_total_free(grid)
                        reachable = bfs_connected_area(grid, (sr, sc))
                        if reachable != total_free or has_dead_end(grid):
                            remove_wall(coords, grid)
                        else:
                            placed += len(coords)
                        break
                else:
                    continue
                break
        attempts += 1

    for r, c in [(1, 1), (1, COLS - 2), (ROWS - 2, 1), (ROWS - 2, COLS - 2)]:
        grid[r][c] = "o"

    grid[ROWS // 2 + 2][COLS // 2] = "M"

    ghost_row = ROWS // 2
    ghost_col = COLS // 2
    for offset, g in zip([-2, -1, 0, 1], ["C", "I", "B", "P"]):
        grid[ghost_row][ghost_col + offset] = g

    return grid


def print_map(grid):
    for row in grid:
        print("".join(row))


if __name__ == "__main__":
    random.seed()
    game_map = create_map_easy()
    print_map(game_map)
