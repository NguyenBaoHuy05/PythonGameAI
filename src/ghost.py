import pygame
import os
import random
import algorithms as alg

TILE_SIZE = 20


class Ghost:
    def __init__(
        self,
        x,
        y,
        home_pos_x,
        home_pos_y,
        name="Blinky",
        sprite_folder="../assets/sprites/ghosts",
        sprite_eyes="../assets/sprites/eyes",
        sprite_health="../assets/sprites/heal",
        sprite_frightened="../assets/sprites/frightened",
    ):
        self.grid_pos = pygame.Vector2(x, y)
        self.pixel_pos = pygame.Vector2(x * TILE_SIZE, y * TILE_SIZE)
        self.direction = pygame.Vector2(1, 0)
        self.speed = 1
        self.alive = True

        self.bfs_path = []
        self.chase_path = pygame.Vector2(0, 0)
        self.chase_path_prev = pygame.Vector2(0, 0)
        self.bfs_index = 0

        self.name = name.capitalize()
        self.sprite_folder = sprite_folder
        self.sprite_eyes = sprite_eyes
        self.FRIGHTENED_SPRITES = {
            "blue": [
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sprite_frightened, "blue1.png")
                    ).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                ),
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sprite_frightened, "blue2.png")
                    ).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                ),
            ],
            "white": [
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sprite_frightened, "white1.png")
                    ).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                ),
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sprite_frightened, "white2.png")
                    ).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                ),
            ],
        }
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(sprite_folder, f"{self.name}1.png")
                ).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(sprite_folder, f"{self.name}2.png")
                ).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            ),
        ]

        self.health_frames = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(sprite_health, "heal1.png")
                ).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(sprite_health, "heal2.png")
                ).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            ),
        ]

        self.eyes = {
            (1, 0): pygame.image.load(
                os.path.join(sprite_eyes, "eyeRight.png")
            ).convert_alpha(),
            (-1, 0): pygame.image.load(
                os.path.join(sprite_eyes, "eyeLeft.png")
            ).convert_alpha(),
            (0, -1): pygame.image.load(
                os.path.join(sprite_eyes, "eyeUp.png")
            ).convert_alpha(),
            (0, 1): pygame.image.load(
                os.path.join(sprite_eyes, "eyeDown.png")
            ).convert_alpha(),
        }

        self.current_frame = 0
        self.frame_delay = 200
        self.last_update_time = pygame.time.get_ticks()

        # Frightened mode
        self.frightened_timer = 0
        self.frightened_anim_frame = 0
        self.frightened_anim_counter = 0

        # Thời gian sống
        self.health_timer = 0
        self.health_anim_frame = 0
        self.health_anim_counter = 0

        self.home_pos = pygame.Vector2(home_pos_x, home_pos_y)

    def update(self, map_data, pacman, chase_mode):
        now = pygame.time.get_ticks()

        # Cập nhật hoạt ảnh frightened
        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            self.frightened_anim_counter += 1
            if self.frightened_anim_counter >= 15:
                self.frightened_anim_frame = (
                    self.frightened_anim_frame + 1
                ) % 2
                self.frightened_anim_counter = 0
        elif self.health_timer > 0:
            self.health_timer -= 1
            self.health_anim_counter += 1
            if self.health_anim_counter >= 15:
                self.health_anim_frame = (self.health_anim_frame + 1) % 2
            return
        else:
            if now - self.last_update_time > self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_update_time = now

        if not self.alive:
            self.revive_move()
            return

        self.check_collision(map_data, pacman)

        if self.frightened_timer > 0:
            if now - self.last_update_time > 300 or self.frightened_timer > 418:
                near_direction = self.direction
                target_dir = alg.near_pacman(
                    map_data,
                    (int(self.grid_pos.x), int(self.grid_pos.y)),
                    (int(pacman.grid_pos.x), int(pacman.grid_pos.y)),
                )
                near_direction = pygame.Vector2(target_dir)
                self.direction = -near_direction
                self.last_update_time = now
            if self.can_move(self.direction, map_data, self.speed):
                self.next_pos = (
                    pygame.Vector2(
                        int(self.pixel_pos.x // TILE_SIZE),
                        int(self.pixel_pos.y // TILE_SIZE),
                    )
                    + self.direction
                ) * TILE_SIZE
                self.pixel_pos += self.direction * self.speed
                if (self.next_pos - self.pixel_pos).length() < self.speed:
                    self.pixel_pos = self.next_pos
                self.grid_pos = pygame.Vector2(
                    round(self.pixel_pos.x / TILE_SIZE),
                    round(self.pixel_pos.y / TILE_SIZE),
                )
            else:
                self.change_direction(map_data)
            return

        if chase_mode and random.random() > 0.4:
            move = alg.bfs_direction(
                map_data,
                (int(self.grid_pos.x), int(self.grid_pos.y)),
                (int(pacman.grid_pos.x), int(pacman.grid_pos.y)),
            )
            self.chase_path = pygame.Vector2(move[0], move[1])
            if self.chase_path == pygame.Vector2(0, 0):
                directions = [
                    pygame.Vector2(1, 0),
                    pygame.Vector2(-1, 0),
                    pygame.Vector2(0, 1),
                    pygame.Vector2(0, -1),
                ]
                valid_directions = [
                    d
                    for d in directions
                    if self.can_move(d, map_data, self.speed)
                ]
                if valid_directions:
                    self.chase_path = random.choice(valid_directions)
                else:
                    print(
                        f"Ghost {self.name} stuck at {self.grid_pos}, no valid directions"
                    )
            move_direction = (
                self.chase_path
                if self.can_move(self.chase_path, map_data, self.speed)
                else self.direction
            )
            if self.can_move(move_direction, map_data, self.speed):
                self.direction = move_direction
                self.pixel_pos += self.direction * self.speed
                self.grid_pos = pygame.Vector2(
                    round(self.pixel_pos.x / TILE_SIZE),
                    round(self.pixel_pos.y / TILE_SIZE),
                )
            else:
                self.change_direction(map_data)
        else:
            if self.can_move(self.direction, map_data, self.speed):
                self.pixel_pos += self.direction * self.speed
                self.grid_pos = pygame.Vector2(
                    round(self.pixel_pos.x / TILE_SIZE),
                    round(self.pixel_pos.y / TILE_SIZE),
                )
            else:
                self.change_direction(map_data)
                if not self.can_move(self.direction, map_data, self.speed):
                    print(
                        f"Ghost {self.name} cannot move in direction {self.direction} at {self.grid_pos}"
                    )

    def check_collision(self, map_data, pacman):
        if self.is_colliding_with(pacman):
            if self.alive and pacman.alive:
                if self.frightened_timer > 0:
                    pacman.eatGhost += 1
                    self.set_alive(map_data, self.grid_pos, self.home_pos)
                elif not pacman.invincible:
                    pacman.set_dead()

    def is_colliding_with(self, pacman):
        return int(self.grid_pos.x) == int(pacman.grid_pos.x) and int(
            self.grid_pos.y
        ) == int(pacman.grid_pos.y)

    def can_move(self, direction, map_data, speed=1):
        if direction.length_squared() == 0:
            return True
        next_pos = self.pixel_pos + direction * speed

        left = next_pos.x
        right = next_pos.x + TILE_SIZE - 1
        top = next_pos.y
        bottom = next_pos.y + TILE_SIZE - 1

        tiles_to_check = {
            (int(top // TILE_SIZE), int(left // TILE_SIZE)),
            (int(top // TILE_SIZE), int(right // TILE_SIZE)),
            (int(bottom // TILE_SIZE), int(left // TILE_SIZE)),
            (int(bottom // TILE_SIZE), int(right // TILE_SIZE)),
        }

        for row, col in tiles_to_check:
            if (
                row < 0
                or row >= len(map_data)
                or col < 0
                or col >= len(map_data[0])
                or map_data[row][col] == "#"
            ):
                return False
        return True

    def change_direction(self, map_data, other_direction=None):
        directions = [
            pygame.Vector2(1, 0),
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, 1),
            pygame.Vector2(0, -1),
        ]
        do_directions = other_direction if other_direction else self.direction
        random.shuffle(directions)
        for d in directions:
            if (
                d != -do_directions
                and d != -self.direction
                and self.can_move(d, map_data, self.speed)
            ):
                self.direction = d
                break

    def draw(self, screen):
        if self.frightened_timer > 0:
            sprites = (
                self.FRIGHTENED_SPRITES["white"]
                if self.frightened_timer < 60
                else self.FRIGHTENED_SPRITES["blue"]
            )
            frame = sprites[self.frightened_anim_frame]
            screen.blit(frame, self.pixel_pos)
        elif self.health_timer > 0:
            frame = self.health_frames[self.health_anim_frame]
            screen.blit(frame, self.pixel_pos)
        else:
            frame = self.frames[self.current_frame]
            if self.alive:
                screen.blit(frame, self.pixel_pos)

            key = (int(self.direction.x), int(self.direction.y))
            if key in self.eyes:
                eye = pygame.transform.scale(
                    self.eyes[key], (TILE_SIZE, TILE_SIZE)
                )
                screen.blit(eye, self.pixel_pos)

    def set_frightened(self, duration_frames=420):
        self.frightened_timer = duration_frames
        self.frightened_anim_frame = 0
        self.frightened_anim_counter = 0

    def set_alive(self, map_data, start_pos, goal_pos):
        self.alive = False
        self.bfs_path = alg.bfs_shortest_path(
            map_data,
            (int(start_pos.x), int(start_pos.y)),
            (int(goal_pos.x), int(goal_pos.y)),
        )
        self.bfs_index = 0
        self.frightened_timer = 0
        self.frightened_anim_frame = 0
        self.frightened_anim_counter = 0

    def set_health(self, duration_frames=100):
        self.health_timer = duration_frames
        self.health_anim_frame = 0
        self.health_anim_counter = 0

    def revive_move(self):
        if self.bfs_index < len(self.bfs_path):
            next_grid_cell = self.bfs_path[self.bfs_index]
            target_pixel_pos = pygame.Vector2(
                next_grid_cell[0] * TILE_SIZE, next_grid_cell[1] * TILE_SIZE
            )
            direction_to_target = target_pixel_pos - self.pixel_pos
            if direction_to_target.length() < (self.speed + 2):
                self.pixel_pos = target_pixel_pos
                self.grid_pos = pygame.Vector2(
                    next_grid_cell[0], next_grid_cell[1]
                )
                self.bfs_index += 1
            else:
                self.pixel_pos += direction_to_target.normalize() * (
                    self.speed + 2
                )
                self.grid_pos = pygame.Vector2(
                    round(self.pixel_pos.x / TILE_SIZE),
                    round(self.pixel_pos.y / TILE_SIZE),
                )
            return
        else:
            self.alive = True
            self.bfs_path = []
            self.bfs_index = 0
            self.pixel_pos = pygame.Vector2(
                self.home_pos.x * TILE_SIZE, self.home_pos.y * TILE_SIZE
            )
            self.set_health(100)