import pygame
import sys
from map_generator import create_map
from ghost import Ghost
from pacman import Pacman
from map_loader import load_map, find_pacman_start, find_ghost_start
from menu import main_menu, pause_menu, game_over_menu, victory_menu, show_controls

# ==== CẤU HÌNH ====
TILE_SIZE = 20
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)


# ==== HÀM TIỆN ÍCH ====
def draw_map(screen, map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
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


def reset_game(map_choice, mode):
    if map_choice == "random":
        new_map_data = create_map()
    else:
        try:
            new_map_data = load_map(f"../assets/maps/{map_choice}")
        except Exception as e:
            print(f"Error loading map {map_choice}: {e}. Falling back to random map.")
            new_map_data = create_map()
            map_choice = "random"
    pacman = Pacman(*find_pacman_start(new_map_data), algorithm=mode)
    ghosts = [
        Ghost(*find_ghost_start(new_map_data, "B"), *find_ghost_start(new_map_data, "B"), "Blinky"),
        Ghost(*find_ghost_start(new_map_data, "P"), *find_ghost_start(new_map_data, "P"), "Pinky"),
        Ghost(*find_ghost_start(new_map_data, "I"), *find_ghost_start(new_map_data, "I"), "Inky"),
        Ghost(*find_ghost_start(new_map_data, "C"), *find_ghost_start(new_map_data, "C"), "Clyde"),
    ]
    score = 0
    won = False
    return new_map_data, pacman, ghosts, score, won, map_choice


def main():
    pygame.init()
    font = pygame.font.SysFont("arial", 24)

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pacman")

    map_choice, mode = main_menu(screen)
    if mode not in ["a_star", "bfs"]:
        print(f"Invalid mode: {mode}. Defaulting to a_star.")
        mode = "a_star"
        map_choice = "level1.txt"
    print(f"Selected map: {map_choice}, mode: {mode}")

    map_data, pacman, ghosts, score, won, map_choice = reset_game(map_choice, mode)
    MAP_WIDTH = len(map_data[0])
    MAP_HEIGHT = len(map_data)

    screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))

    last_time = pygame.time.get_ticks()
    chase_time = 15000
    scatter_time = 5000
    chase_mode = False
    clock = pygame.time.Clock()
    running = True
    paused = False

    while running:
        now = pygame.time.get_ticks()
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        result = pause_menu(screen, font)
                        if result == "menu":
                            map_choice, mode = main_menu(screen)
                            if mode not in ["a_star", "bfs"]:
                                print(f"Invalid mode: {mode}. Defaulting to a_star.")
                                mode = "a_star"
                                map_choice = "level1.txt"
                            map_data, pacman, ghosts, score, won, map_choice = reset_game(map_choice, mode)
                            screen = pygame.display.set_mode((len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE))
                            print(f"Reset game with map: {map_choice}, mode: {mode}")
                elif event.key == pygame.K_c:
                    show_controls(screen)
                    screen.fill((0, 0, 0))
                    draw_map(screen, map_data)
                    pacman.draw(screen)
                    for ghost in ghosts:
                        ghost.draw(screen)
                    draw_ui(screen, font, score + pacman.eatGhost * 100, pacman.lives)
                    pygame.display.flip()

        if paused:
            pygame.display.flip()
            continue

        if pacman.lives > 0:
            pacman.update(map_data, ghosts)

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
                    pacman.activate_chase_ghosts()
                    for ghost in ghosts:
                        ghost.set_frightened()

            for ghost in ghosts:
                ghost.update(map_data, pacman, chase_mode)
            if chase_mode:
                if now - last_time > chase_time:
                    chase_mode = False
                    last_time = now
            else:
                if now - last_time > scatter_time:
                    chase_mode = True
                    last_time = now

            draw_map(screen, map_data)
            pacman.draw(screen)
            for ghost in ghosts:
                ghost.draw(screen)
            draw_ui(screen, font, score + pacman.eatGhost * 100, pacman.lives)

            if won:
                result = victory_menu(screen, font, score + pacman.eatGhost * 100)
                if result == "next":
                    next_level = map_choice
                    if map_choice != "random" and map_choice.startswith("level"):
                        try:
                            level_num = int(map_choice[5])
                            if level_num < 6:
                                next_level = f"level{level_num + 1}.txt"
                            else:
                                next_level = "random"
                        except ValueError:
                            next_level = "random"
                    map_data, pacman, ghosts, score, won, map_choice = reset_game(next_level, mode)
                    screen = pygame.display.set_mode((len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE))
                    print(f"Next level: {map_choice}, mode: {mode}")
                elif result == "menu":
                    map_choice, mode = main_menu(screen)
                    if mode in ["a_star", "bfs"]:
                        map_data, pacman, ghosts, score, won, map_choice = reset_game(map_choice, mode)
                        screen = pygame.display.set_mode((len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE))
                        print(f"Reset game with map: {map_choice}, mode: {mode}")
                    else:
                        running = False
        else:
            action = game_over_menu(screen, font, score + pacman.eatGhost * 100)
            if action == "retry":
                map_data, pacman, ghosts, score, won, map_choice = reset_game(map_choice, mode)
                screen = pygame.display.set_mode((len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE))
                print(f"Retry with map: {map_choice}, mode: {mode}")
            elif action == "menu":
                map_choice, mode = main_menu(screen)
                if mode in ["a_star", "bfs"]:
                    map_data, pacman, ghosts, score, won, map_choice = reset_game(map_choice, mode)
                    screen = pygame.display.set_mode((len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE))
                    print(f"Reset game with map: {map_choice}, mode: {mode}")
                else:
                    running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()