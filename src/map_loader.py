# ========== Cấu hình ==========
TILE_SIZE = 20  # Để sử dụng khi tạo tọa độ pixel nếu cần

# ========== Các ký hiệu ==========
# "M": Pac-Man
# "B": Blinky
# "P": Pinky
# "I": Inky
# "C": Clyde
# "G": ghost generic
# ".": pellet thường
# "o": power pellet
# "#": tường
# " ": trống


def load_map(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    return [list(row) for row in lines]


def find_pacman_start(map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == "M":
                return x, y
    return 1, 1


def find_home_start(map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == "H":
                return x, y
    return 1, 1


def find_ghost_start(map_data, type="G"):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == type:
                return x, y
    return 1, 1


def all_dot_pos(map_data):
    all_pos = []
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == ".":
                all_pos.append((x, y))
    return all_pos


def all_Power_pos(map_data):
    all_pos = []
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == ".":
                all_pos.append((x, y))
    return all_pos
