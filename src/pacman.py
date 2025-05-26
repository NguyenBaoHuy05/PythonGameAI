import pygame
import os
import random

TILE_SIZE = 20


class Pacman:
    def __init__(self, x, y, sprite_folder="../assets/sprites/pacman"):
        self.start_x = x
        self.start_y = y
        self.grid_pos = pygame.Vector2(x, y)
        self.pixel_pos = self.grid_pos * TILE_SIZE

        self.direction = pygame.Vector2(0, 0)
        self.desired_direction = pygame.Vector2(0, 0)
        self.speed = 2
        self.lives = 3
        self.alive = True
        self.invincible = False
        self.eatGhost = 0

        self.fade_alpha = 255

        self.death_time = None
        self.respawn_time = None
        self.inx = 0

        # Load animation frames
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
        self.frame_delay = 100  # ms
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
        self.eatGhost = 0
        self.inx = 0

    def set_direction(self, dx, dy):
        self.desired_direction = pygame.Vector2(dx, dy)

    def update(self, map_data, ghosts):
        now = pygame.time.get_ticks()
        if not self.alive:
            elapsed = now - self.death_time
            if now - self.death_time < 2000:
                self.fade_alpha = max(255 - int((elapsed / 2000) * 255), 0)
                print(elapsed)
            else:
                # Sau 2s hiệu ứng mờ dần thì giảm mạng, reset vị trí và kích hoạt bất tử
                print("Pacman died")
                self.lives -= 1
                self.reset_position()
                self.invincible = True
                self.respawn_time = now
            return

        # Hết trạng thái bất tử sau 5s
        if (
            self.invincible
            and self.respawn_time
            and now - self.respawn_time > 5000
        ):
            self.invincible = False

        # Cập nhật animation Pacman
        if now - self.last_update_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update_time = now

        # Di chuyển Pacman nếu có thể
        if self.can_move(self.direction, map_data):
            self.pixel_pos += self.direction * self.speed
            if self.pixel_pos.x < 0:
                self.pixel_pos.x = 27 * TILE_SIZE
            elif self.pixel_pos.x >= 27 * TILE_SIZE:
                self.pixel_pos.x = 0
            if self.pixel_pos.y < 0:
                self.pixel_pos.y = 30 * TILE_SIZE
            elif self.pixel_pos.y >= 30 * TILE_SIZE:
                self.pixel_pos.y = 0
            self.grid_pos = pygame.Vector2(
                int(self.pixel_pos.x // TILE_SIZE),
                int(self.pixel_pos.y // TILE_SIZE),
            )
        if self.inx % 5:
            self.ReflexAgent(map_data, ghosts)
        else:
            self.change_direction(map_data)
        self.inx += 1

    def change_direction(self, map_data, other_direction=None):
        directions = [
            pygame.Vector2(1, 0),
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, 1),
            pygame.Vector2(0, -1),
        ]
        do_directions = other_direction if other_direction else self.direction
        random.shuffle(directions)
        i = 0
        for d in directions:
            if d != -do_directions and self.can_move(d, map_data):
                i += 1
                self.direction = d
                break
        if i == 0:
            self.direction = -do_directions

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
            if map_data[row][col] == "#":
                return False
        return True

    def set_dead(self):
        self.alive = False
        now = pygame.time.get_ticks()
        self.death_time = now
        self.fade_alpha = 255

    def draw(self, screen):
        frame = self.frames[self.current_frame]
        angle = self._get_angle()
        rotated = pygame.transform.rotate(frame, angle)

        if not self.alive:
            faded = rotated.copy()
            faded.set_alpha(self.fade_alpha)
            screen.blit(faded, (int(self.pixel_pos.x), int(self.pixel_pos.y)))
        elif self.invincible:
            # Hiệu ứng nhấp nháy khi bất tử: alpha thay đổi 128 và 255 mỗi 300ms
            alpha = 128 if (pygame.time.get_ticks() // 300) % 2 == 0 else 255
            faded = rotated.copy()
            faded.set_alpha(alpha)
            screen.blit(faded, (int(self.pixel_pos.x), int(self.pixel_pos.y)))
        else:
            # Vẽ bình thường
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

    def get_cost(self, map_data, current_pos, ghosts):
        cost = 1
        directions = [
            pygame.Vector2(0, -1),
            pygame.Vector2(0, 1),
            pygame.Vector2(-1, 0),
            pygame.Vector2(1, 0),
        ]
        for ghost in ghosts:
            if ghost.frightened_timer > 0:
                dist_to_ghost = abs(current_pos.x - ghost.grid_pos.x) + abs(
                    current_pos.y - ghost.grid_pos.y
                )
                if dist_to_ghost <= 5:
                    cost -= (5 - dist_to_ghost) * 10000
                if map_data[int(current_pos.y)][int(current_pos.x)] == "o":
                    cost -= 100000
            else:
                dist_to_ghost = abs(current_pos.x - ghost.grid_pos.x) + abs(
                    current_pos.y - ghost.grid_pos.y
                )
                if dist_to_ghost == 0:
                    cost += 100000
                elif dist_to_ghost == 1:
                    cost += 40000
                else:
                    dist_to_pacman = abs(current_pos.x - self.grid_pos.x) + abs(
                        current_pos.y - self.grid_pos.y
                    )
                    cost += (dist_to_ghost - dist_to_pacman) * 10000
        if map_data[int(current_pos.y)][int(current_pos.x)] == ".":
            cost -= 100
        for direction in directions:
            if directions == -self.direction:
                continue
            next_pos = current_pos + direction
            if next_pos.x < 0:
                next_pos.x = 26
            elif next_pos.x >= 27:
                next_pos.x = 0
            if next_pos.y < 0:
                next_pos.y = 29
            elif next_pos.y > 30:
                next_pos.y = 0
            if (
                map_data[int(next_pos.y)][int(next_pos.x)] != "#"
                and next_pos != self.grid_pos
            ):

                cost -= 20000

        return cost

    def ReflexAgent(self, map_data, ghosts):
        directions = [
            pygame.Vector2(0, -1),
            pygame.Vector2(0, 1),
            pygame.Vector2(-1, 0),
            pygame.Vector2(1, 0),
        ]
        best_direction = self.direction
        min_cost = float("inf")

        reverse_direction = -self.direction

        for direction in directions:
            if direction == reverse_direction:
                continue
            cost = 0
            current_pos = self.grid_pos + direction
            if current_pos.x < 0:
                current_pos.x = 26
            elif current_pos.x > 26:
                current_pos.x = 0
            if current_pos.y < 0:
                current_pos.y = 29
            elif current_pos.y > 29:
                current_pos.y = 0
            while (
                map_data[int(current_pos.y)][int(current_pos.x)] != "#"
                and current_pos != self.grid_pos
            ):
                cost += self.get_cost(map_data, current_pos, ghosts)
                current_pos += direction
                if current_pos.x < 0:
                    current_pos.x = 26
                elif current_pos.x >= 26:
                    current_pos.x = 0
                if current_pos.y < 0:
                    current_pos.y = 29
                elif current_pos.y >= 29:
                    current_pos.y = 0
            if cost < min_cost:
                min_cost = cost
                best_direction = direction
        self.direction = best_direction
