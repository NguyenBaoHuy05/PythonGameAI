import pygame
import os

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
                print("Pacman died")
                self.lives -= 1
                self.reset_position()
                self.invincible = True
                self.respawn_time = now
            return

        # Hết trạng thái bất tử sau 5s
        if self.invincible and self.respawn_time and now - self.respawn_time > 5000:
            self.invincible = False

        # Cập nhật animation Pacman
        if now - self.last_update_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update_time = now

        # Đổi hướng nếu có thể
        if self.desired_direction != self.direction and self.can_move(self.desired_direction, map_data):
            self.direction = self.desired_direction

        # Di chuyển Pacman nếu có thể
        if self.can_move(self.direction, map_data):
            self.pixel_pos += self.direction * self.speed
            self.grid_pos = pygame.Vector2(
                int(self.pixel_pos.x // TILE_SIZE),
                int(self.pixel_pos.y // TILE_SIZE),
            )
        for ghost in ghosts:
            if self.is_colliding_with(ghost):
                if ghost.frightened_timer > 0 or self.invincible:  # Nếu ma đang yếu
                    ghost.set_alive(map_data, ghost.grid_pos, ghost.home_pos) # Đưa ma về nhà
                    if ghost.frightened_timer > 0:  
                        self.eatGhost += 1  # Tăng số lượng ma đã ăn
                else:
                    self.set_dead()

    def is_colliding_with(self, ghost):
        return int(self.grid_pos.x) == int(ghost.grid_pos.x) and int(self.grid_pos.y) == int(ghost.grid_pos.y)

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
            if row < 0 or row >= len(map_data) or col < 0 or col >= len(map_data[0]) or map_data[row][col] == "#":
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