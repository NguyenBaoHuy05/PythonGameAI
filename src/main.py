import pygame
import sys
from ghost import Ghost
from pacman import Pacman
from map_loader import (
    load_map,
    find_pacman_start,
    find_ghost_start,
    find_home_start,
)

# ==== CẤU HÌNH ====
TILE_SIZE = 20
MAP_FILE = "../assets/maps/level1.txt"
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)


# ==== HÀM TIỆN ÍCH ====
def draw_map(screen, map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            rect = pygame.Rect(
                x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
            )
            if tile == "#":
                pygame.draw.rect(screen, BLUE, rect)
            elif tile == ".":
                pygame.draw.circle(screen, YELLOW, rect.center, 3)
            elif tile == "o":
                pygame.draw.circle(screen, ORANGE, rect.center, 6)


def draw_ui(screen, font, score, lives):
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))


def check_win(map_data):
    return not any("." in row for row in map_data)


def game_over_menu(screen, font):
    # Hiển thị menu khi hết mạng
    screen.fill((0, 0, 0))
    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    retry_text = font.render(
        "Chose R to play again or Q to quit", True, (255, 255, 255)
    )

    screen.blit(
        game_over_text,
        game_over_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 3)
        ),
    )
    screen.blit(
        retry_text,
        retry_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2)
        ),
    )

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    return "retry"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# ==== MAIN GAME ====
def main():
    pygame.init()
    font = pygame.font.SysFont("arial", 24)

    # Tải map để lấy kích thước màn hình
    map_data = load_map(MAP_FILE)
    MAP_WIDTH = len(map_data[0])
    MAP_HEIGHT = len(map_data)

    screen = pygame.display.set_mode(
        (MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
    )
    pygame.display.set_caption("Pacman")

    def reset_game():
        # Load lại map, tạo lại pacman, ghosts, reset điểm, trạng thái
        new_map_data = load_map(MAP_FILE)
        pacman = Pacman(*find_pacman_start(new_map_data))
        ghosts = [
            Ghost(
                *find_ghost_start(new_map_data, "B"),
                *find_ghost_start(new_map_data, "B"),
                "Blinky",
            ),
            Ghost(
                *find_ghost_start(new_map_data, "P"),
                *find_ghost_start(new_map_data, "P"),
                "Pinky",
            ),
            Ghost(
                *find_ghost_start(new_map_data, "I"),
                *find_ghost_start(new_map_data, "I"),
                "Inky",
            ),
            Ghost(
                *find_ghost_start(new_map_data, "C"),
                *find_ghost_start(new_map_data, "C"),
                "Clyde",
            ),
        ]
        score = 0
        won = False
        return new_map_data, pacman, ghosts, score, won

    # Gọi reset_game() lần đầu sau khi tạo màn hình
    map_data, pacman, ghosts, score, won = reset_game()

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        # === XỬ LÝ SỰ KIỆN ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.set_direction(1, 0)
                elif event.key == pygame.K_UP:
                    pacman.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    pacman.set_direction(0, 1)

        # Cập nhật game chỉ khi còn mạng
        if pacman.lives > 0:

            if pacman.alive:
                x, y = int(pacman.grid_pos.x), int(pacman.grid_pos.y)
                if map_data[y][x] == ".":
                    map_data[y][x] = " "
                    score += 10
                    if check_win(map_data):
                        won = True
                elif map_data[y][x] == "o":
                    map_data[y][x] = " "
                    score += 50
                    for ghost in ghosts:
                        ghost.set_frightened()

            for ghost in ghosts:
                ghost.update(map_data, pacman)

            pacman.update(map_data, ghosts)
            draw_map(screen, map_data)
            pacman.draw(screen)
            for ghost in ghosts:
                ghost.draw(screen)
            draw_ui(screen, font, score, pacman.lives)

            if won:
                win_text = font.render("You Win!", True, YELLOW)
                rect = win_text.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2)
                )
                screen.blit(win_text, rect)

        else:
            # Hết mạng
            action = game_over_menu(screen, font)
            if action == "retry":
                # Reset game khi chơi lại
                map_data, pacman, ghosts, score, won = reset_game()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
