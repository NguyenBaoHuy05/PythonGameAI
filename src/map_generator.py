import random


def count_adjacent_paths(grid, x, y, height, width):
    # Count adjacent cells that are not walls
    paths = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < height and 0 <= ny < width and grid[nx][ny] != "#":
            paths += 1
    return paths


def ensure_two_paths(grid, height, width):
    # Ensure each non-wall cell has at least 2 adjacent paths
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if grid[i][j] != "#":
                paths = count_adjacent_paths(grid, i, j, height, width)
                if paths < 2:
                    # Randomly open a wall to create at least 2 paths
                    random.shuffle(directions)
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if (
                            0 <= ni < height
                            and 0 <= nj < width
                            and grid[ni][nj] == "#"
                        ):
                            grid[ni][nj] = "."
                            paths += 1
                            if paths >= 2:
                                break


def generate_pacman_map(
    height=31, width=28, wall_density=0.3, power_pellet_count=4
):
    # Initialize grid with walls
    grid = [["#" for _ in range(width)] for _ in range(height)]

    # Create initial paths
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if random.random() > wall_density:
                grid[i][j] = "."

    # Ensure border is all walls
    for i in range(height):
        grid[i][0] = grid[i][width - 1] = "#"
    for j in range(width):
        grid[0][j] = grid[height - 1][j] = "#"

    # Ensure each non-wall cell has at least 2 paths
    ensure_two_paths(grid, height, width)

    # Place power pellets (o)
    placed_power_pellets = 0
    while placed_power_pellets < power_pellet_count:
        x, y = random.randint(1, height - 2), random.randint(1, width - 2)
        if (
            grid[x][y] == "."
            and count_adjacent_paths(grid, x, y, height, width) >= 2
        ):
            grid[x][y] = "o"
            placed_power_pellets += 1

    # Place Pac-Man (M)
    while True:
        x, y = random.randint(1, height - 2), random.randint(1, width - 2)
        if (
            grid[x][y] == "."
            and count_adjacent_paths(grid, x, y, height, width) >= 2
        ):
            grid[x][y] = "M"
            break

    # Place ghosts (C, I, B, P)
    ghosts = ["C", "I", "B", "P"]
    for ghost in ghosts:
        while True:
            x, y = random.randint(1, height - 2), random.randint(1, width - 2)
            if (
                grid[x][y] == "."
                and count_adjacent_paths(grid, x, y, height, width) >= 2
            ):
                grid[x][y] = ghost
                break

    return grid


# Generate and print the map for visualization
random.seed()  # For reproducibility, remove for true randomness
map_array = generate_pacman_map()
for row in map_array:
    print("".join(row))
