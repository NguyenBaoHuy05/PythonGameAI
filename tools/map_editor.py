import pygame
import sys

# ========== Cấu hình ==========
TILE_SIZE = 20
MAP_WIDTH = 28
MAP_HEIGHT = 31
WINDOW_WIDTH = TILE_SIZE * MAP_WIDTH
WINDOW_HEIGHT = TILE_SIZE * MAP_HEIGHT
MAP_FILE = "../assets/maps/level1.txt"

# Màu sắc
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 150, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Ký hiệu và màu tương ứng
tile_types = {
    "#": BLUE,  # tường
    ".": YELLOW,  # chấm ăn nhỏ
    "o": ORANGE,  # power pellet
    "P": GREEN,  # pacman
    "G": RED,  # ghost
}

# Khởi tạo
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pac-Man Map Editor")

# Bản đồ: khởi tạo toàn bộ là khoảng trắng
grid = [[" " for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# Loại ô đang chọn (mặc định là tường '#')
current_tile = "#"


# ========== Vẽ lưới ==========
def draw_grid():
    screen.fill(BLACK)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            rect = pygame.Rect(
                x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
            )
            char = grid[y][x]
            if char in tile_types:
                pygame.draw.rect(screen, tile_types[char], rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
    pygame.display.flip()


# ========== Lưu map ==========
def save_map():
    with open(MAP_FILE, "w") as f:
        for row in grid:
            f.write("".join(row) + "\n")
    print(f"✅ Map saved to {MAP_FILE}")


# ========== Main ==========
def main():
    global current_tile
    clock = pygame.time.Clock()
    running = True

    while running:
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    save_map()
                elif event.key == pygame.K_1:
                    current_tile = "#"
                elif event.key == pygame.K_2:
                    current_tile = "."
                elif event.key == pygame.K_3:
                    current_tile = "o"
                elif event.key == pygame.K_4:
                    current_tile = "M"
                elif event.key == pygame.K_b:
                    current_tile = "B"
                elif event.key == pygame.K_i:
                    current_tile = "I"
                elif event.key == pygame.K_c:
                    current_tile = "C"
                elif event.key == pygame.K_p:
                    current_tile = "P"
                elif event.key == pygame.K_5:
                    current_tile = "G"

            elif pygame.mouse.get_pressed()[0]:  # Chuột trái đặt ô
                x, y = pygame.mouse.get_pos()
                grid[y // TILE_SIZE][x // TILE_SIZE] = current_tile

            elif pygame.mouse.get_pressed()[2]:  # Chuột phải để xóa
                x, y = pygame.mouse.get_pos()
                grid[y // TILE_SIZE][x // TILE_SIZE] = " "

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
