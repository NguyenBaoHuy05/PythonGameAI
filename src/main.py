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
    return not any("." in row or "o" in row for row in map_data)

def game_over_menu(screen, font):
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
    map_data = load_map(MAP_FILE)
    MAP_WIDTH = len(map_data[0])
    MAP_HEIGHT = len(map_data)
    screen = pygame.display.set_mode(
        (MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
    )
    pygame.display.set_caption("Pacman")

    class Game:
        def __init__(self, map_data, pacman, ghosts):
            self.map_data = map_data
            self.pacman = pacman
            self.ghosts = ghosts

    def reset_game():
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
        game = Game(new_map_data, pacman, ghosts)
        pacman.set_ai(game)  # Khởi tạo AI cho Pacman
        score = 0
        won = False
        return game, score, won

    game, score, won = reset_game()
    last_time = pygame.time.get_ticks()
    chase_time = 10000
    scatter_time = 5000
    chase_mode = False
    clock = pygame.time.Clock()
    running = True

    while running:
        now = pygame.time.get_ticks()
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.pacman.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.pacman.set_direction(1, 0)
                elif event.key == pygame.K_UP:
                    game.pacman.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.pacman.set_direction(0, 1)
                elif event.key == pygame.K_a:
                    game.pacman.ai.mode = 'A*'  # Kích hoạt A*
                elif event.key == pygame.K_b:
                    game.pacman.ai.mode = 'BFS'  # Kích hoạt BFS
                elif event.key == pygame.K_ESCAPE:
                    game.pacman.ai.mode = None  # Tắt AI

        if game.pacman.lives > 0:
            if game.pacman.alive:
                x, y = int(game.pacman.grid_pos.x), int(game.pacman.grid_pos.y)
                if game.map_data[y][x] in ['.', 'o']:
                    if game.map_data[y][x] == '.':
                        score += 10
                    else:  # 'o'
                        score += 50
                        for ghost in game.ghosts:
                            ghost.set_frightened()
                    game.map_data[y][x] = ' '  # Xóa điểm đã ăn
                    if check_win(game.map_data):
                        won = True

            for ghost in game.ghosts:
                ghost.update(game.map_data, game.pacman, chase_mode)
                if chase_mode:
                    if now - last_time > chase_time:
                        chase_mode = False
                        last_time = now
                else:
                    if now - last_time > scatter_time:
                        chase_mode = True
                        last_time = now
            game.pacman.update(game.map_data)

            draw_map(screen, game.map_data)
            game.pacman.draw(screen)
            for ghost in game.ghosts:
                ghost.draw(screen)
            draw_ui(screen, font, score, game.pacman.lives)

            if won:
                win_text = font.render("You Win!", True, YELLOW)
                rect = win_text.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2)
                )
                screen.blit(win_text, rect)

        else:
            action = game_over_menu(screen, font)
            if action == "retry":
                game, score, won = reset_game()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()