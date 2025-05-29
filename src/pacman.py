import pygame
import os
import random
from algorithms import (
    a_star_direction,
    bfs_direction,
    ucs_direction,
    dfs_direction,
)

TILE_SIZE = 20


class Pacman:
    def __init__(
        self, x, y, sprite_folder="../assets/sprites/pacman", algorithm="a_star"
    ):
        self.start_x = x
        self.start_y = y
        self.grid_pos = pygame.Vector2(x, y)
        self.pixel_pos = self.grid_pos * TILE_SIZE

        self.direction = pygame.Vector2(0, 0)
        self.desired_direction = pygame.Vector2(0, 0)
        self.speed = 2
        self.lives = 3
        self.alive = True
        self.invincible = True
        self.fade_alpha = 255

        self.death_time = None
        self.respawn_time = pygame.time.get_ticks()
        self.algorithm = algorithm

        self.chase_ghosts = False
        self.chase_timer = 0
        self.eatGhost = 0

        self.frames = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(sprite_folder, f"pacman{i}.png")
                ).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for i in range(1, 5)
        ]
        self.current_frame = 0
        self.frame_delay = 100
        self.last_update_time = pygame.time.get_ticks()

    def reset_position(self):
        self.grid_pos = pygame.Vector2(self.start_x, self.start_y)
        self.pixel_pos = self.grid_pos * TILE_SIZE
        self.set_direction(0, 0)
        self.fade_alpha = 255
        self.alive = True
        self.invincible = False
        self.death_time = None
        self.respawn_time = None
        self.chase_ghosts = False
        self.chase_timer = 0
        self.eatGhost = 0

    def set_direction(self, dx, dy):
        self.desired_direction = pygame.Vector2(dx, dy)

    def find_nearest_item(
        self, map_data, ghost_positions, prioritize_power=False
    ):
        min_dist = float("inf")
        nearest = None
        px, py = int(self.grid_pos.x), int(self.grid_pos.y)
        map_info = self.analyze_map(map_data)
        powerup_priority = -50 if prioritize_power else 100
        ghost_count_near = sum(
            1
            for gp in ghost_positions
            if abs(px - gp[0]) + abs(py - gp[1]) <= 5
        )
        powerup_priority -= 10 * ghost_count_near
        for y, row in enumerate(map_data):
            for x, tile in enumerate(row):
                if tile == "." or (tile == "o" and prioritize_power):
                    dist = abs(px - x) + abs(py - y)
                    priority = powerup_priority if tile == "o" else 0
                    min_ghost_dist = min(
                        [
                            abs(x - gp[0]) + abs(y - gp[1])
                            for gp in ghost_positions
                        ],
                        default=float("inf"),
                    )
                    penalty = 50 if min_ghost_dist <= 3 else 0
                    score = dist + penalty + priority
                    if score < min_dist:
                        min_dist = score
                        nearest = (x, y)
        return nearest if nearest else (px, py)

    def find_nearest_frightened_ghost(self, ghosts):
        min_dist = float("inf")
        nearest = None
        px, py = int(self.grid_pos.x), int(self.grid_pos.y)
        for ghost in ghosts:
            if ghost.alive and ghost.frightened_timer > 0:
                gx, gy = int(ghost.grid_pos.x), int(ghost.grid_pos.y)
                dist = abs(px - gx) + abs(py - gy)
                if dist < min_dist:
                    min_dist = dist
                    nearest = (gx, gy)
        return nearest if nearest else (px, py)

    def find_safest_position(self, map_data, ghost_positions):
        max_score = -float("inf")
        safest_pos = (int(self.grid_pos[0]), int(self.grid_pos[1]))
        px, py = safest_pos
        height, width = len(map_data), len(map_data[0])
        map_info = self.analyze_map(map_data)
        distance_weight = 0.3 if map_info["size"] < 500 else 0.5
        for y in range(height):
            for x in range(width):
                if map_data[y][x] != "#":
                    pos = (x, y)
                    min_dist_to_ghost = min(
                        [
                            abs(pos[0] - gp[0]) + abs(pos[1] - gp[1])
                            for gp in ghost_positions
                        ],
                        default=float("inf"),
                    )
                    dist_to_pacman = abs(px - x) + abs(py - y)
                    open_neighbors = sum(
                        1
                        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                        if 0 <= y + dy < height
                        and 0 <= x + dx < width
                        and map_data[y + dy][x + dx] != "#"
                    )
                    escape_bonus = 20 * open_neighbors
                    score = (
                        min_dist_to_ghost
                        - distance_weight * dist_to_pacman
                        + escape_bonus
                    )
                    if score > max_score:
                        max_score = score
                        safest_pos = pos
        return safest_pos

    def analyze_map(self, map_data):
        height, width = len(map_data), len(map_data[0])
        wall_count = sum(row.count("#") for row in map_data)
        density = wall_count / (height * width)
        powerup_count = sum(row.count("o") for row in map_data)
        return {
            "size": height * width,
            "density": density,
            "powerups": powerup_count,
        }

    def predict_ghost_positions(self, ghosts):
        predicted = []
        for ghost in ghosts:
            if ghost.alive and ghost.frightened_timer <= 0:
                gx, gy = int(ghost.grid_pos.x), int(ghost.grid_pos.y)
                dx, dy = int(ghost.direction.x), int(ghost.direction.y)
                next_pos = (gx + dx, gy + dy)
                predicted.append(next_pos)
        return predicted

    def ReflexAgent(self, map_data, ghosts):
        now = pygame.time.get_ticks()
        if not self.alive:
            elapsed = now - self.death_time
            if elapsed > 2000:
                self.lives -= 1
                self.reset_position()
                self.invincible = True
                self.respawn_time = now
            return False

        if (
            self.invincible
            and self.respawn_time
            and now - self.respawn_time > 1500
        ):
            self.invincible = False

        if self.chase_ghosts and now - self.chase_timer > 7000:
            self.chase_ghosts = False

        if now - self.last_update_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update_time = now

        if self.alive:
            ghost_positions = [
                (int(ghost.grid_pos.x), int(ghost.grid_pos.y))
                for ghost in ghosts
                if ghost.alive and ghost.frightened_timer <= 0
            ]
            predicted_positions = self.predict_ghost_positions(ghosts)
            ghost_positions.extend(predicted_positions)
            pacman_pos = (int(self.grid_pos.x), int(self.grid_pos.y))
            map_info = self.analyze_map(map_data)
            ghost_proximity = 3 if map_info["size"] < 500 else 4
            ghost_near = any(
                abs(pacman_pos[0] - gp[0]) + abs(pacman_pos[1] - gp[1])
                <= ghost_proximity
                for gp in ghost_positions
            )

            if self.chase_ghosts:
                target = self.find_nearest_frightened_ghost(ghosts)
            elif ghost_near and not self.invincible:
                target = self.find_nearest_item(
                    map_data, ghost_positions, prioritize_power=True
                )
            else:
                target = self.find_nearest_item(
                    map_data, ghost_positions, prioritize_power=False
                )

            if self.algorithm == "a_star":
                move = a_star_direction(
                    map_data,
                    pacman_pos,
                    target,
                    ghost_positions=ghost_positions,
                )
            elif self.algorithm == "bfs":
                move = bfs_direction(
                    map_data,
                    pacman_pos,
                    target,
                    ghost_positions=ghost_positions,
                )
            elif self.algorithm == "dfs":
                move = dfs_direction(
                    map_data,
                    pacman_pos,
                    target,
                    ghost_positions=ghost_positions,
                )
            elif self.algorithm == "ucs":
                move = ucs_direction(
                    map_data,
                    pacman_pos,
                    target,
                    ghost_positions=ghost_positions,
                )
            else:
                move = (0, 0)

            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            valid_directions = [
                (dx, dy)
                for dx, dy in directions
                if self.can_move(pygame.Vector2(dx, dy), map_data)
            ]
            if move == (0, 0) or not self.can_move(
                pygame.Vector2(*move), map_data
            ):
                if self.direction != (0, 0) and self.can_move(
                    self.direction, map_data
                ):
                    move = (self.direction.x, self.direction.y)
                elif valid_directions:
                    move = random.choice(valid_directions)
                else:
                    print(
                        f"Pacman stuck at {pacman_pos}, no valid directions. Target: {target}, Ghost positions: {ghost_positions}"
                    )

            self.set_direction(move[0], move[1])

        if self.desired_direction != self.direction and self.can_move(
            self.desired_direction, map_data
        ):
            self.direction = self.desired_direction

        if self.can_move(self.direction, map_data):
            self.pixel_pos += self.direction * self.speed
            self.grid_pos = pygame.Vector2(
                round(self.pixel_pos.x / TILE_SIZE),
                round(self.pixel_pos.y / TILE_SIZE),
            )
        else:
            print(
                f"Pacman cannot move in direction {self.direction} at {pacman_pos}"
            )

    def activate_chase_ghosts(self):
        self.chase_ghosts = True
        self.chase_timer = pygame.time.get_ticks()

    def is_colliding_with(self, ghost):
        return int(self.grid_pos.x) == int(ghost.grid_pos.x) and int(
            self.grid_pos.y
        ) == int(ghost.grid_pos.y)

    def can_move(self, direction, map_data):
        if direction.length_squared() == 0:
            return False

        next_pixel_pos = self.pixel_pos + direction * self.speed
        left = int(next_pixel_pos.x)
        right = int(next_pixel_pos.x + TILE_SIZE - 1)
        top = int(next_pixel_pos.y)
        bottom = int(next_pixel_pos.y + TILE_SIZE - 1)

        tiles = {
            (top // TILE_SIZE, left // TILE_SIZE),
            (top // TILE_SIZE, right // TILE_SIZE),
            (bottom // TILE_SIZE, left // TILE_SIZE),
            (bottom // TILE_SIZE, right // TILE_SIZE),
        }

        for row, col in tiles:
            if (
                row < 0
                or row >= len(map_data)
                or col < 0
                or col >= len(map_data[0])
                or map_data[row][col] == "#"
            ):
                return False
        return True

    def set_dead(self):
        self.alive = False
        now = pygame.time.get_ticks()
        self.death_time = now
        self.fade_alpha = 255
        self.chase_ghosts = False
        self.eatGhost = 0

    def draw(self, screen):
        frame = self.frames[self.current_frame]
        angle = self._get_angle()
        rotated = pygame.transform.rotate(frame, angle)

        if not self.alive:
            faded = rotated.copy()
            faded.set_alpha(self.fade_alpha)
            screen.blit(faded, (int(self.pixel_pos.x), int(self.pixel_pos.y)))
        elif self.invincible:
            alpha = 128 if (pygame.time.get_ticks() // 300) % 2 == 0 else 255
            faded = rotated.copy()
            faded.set_alpha(alpha)
            screen.blit(faded, (int(self.pixel_pos.x), int(self.pixel_pos.y)))
        else:
            screen.blit(rotated, (int(self.pixel_pos.x), int(self.pixel_pos.y)))

    def _get_angle(self):
        if self.direction == pygame.Vector2(1, 0):
            return -180
        if self.direction == pygame.Vector2(0, -1):
            return -90
        if self.direction == pygame.Vector2(-1, 0):
            return 0
        if self.direction == pygame.Vector2(0, 1):
            return 90
        return 0
