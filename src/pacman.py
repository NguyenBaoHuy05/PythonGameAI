import pygame
import os
import heapq
from collections import deque
from typing import List, Tuple
import random

TILE_SIZE = 20

class PacmanAI:
    def __init__(self, pacman, game):
        self.pacman = pacman
        self.game = game
        self.mode = None  # 'A*' hoặc 'BFS'
        self.targets = self.get_targets()  # Lưu danh sách mục tiêu
        self.visited_targets = set()  # Theo dõi mục tiêu đã thăm
        self.current_path = []  # Lưu đường đi hiện tại
        self.current_target = None  # Mục tiêu hiện tại
        self.last_target_update = 0  # Thời điểm cập nhật mục tiêu cuối
        self.last_direction = pygame.Vector2(0, 0)  # Lưu hướng di chuyển gần nhất

    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(nx, ny) for nx, ny in neighbors if self.can_move_to(nx, ny)]

    def can_move_to(self, x: int, y: int) -> bool:
        if (x < 0 or x >= len(self.game.map_data) or
            y < 0 or y >= len(self.game.map_data[0]) or
            self.game.map_data[x][y] == "#"):
            return False
        return True

    def is_safe(self, pos: Tuple[int, int]) -> bool:
        ghost_positions = [(int(ghost.grid_pos.x), int(ghost.grid_pos.y)) for ghost in self.game.ghosts]
        # Không an toàn nếu vị trí trùng với ma hoặc cách ma 1 ô
        for ghost_pos in ghost_positions:
            if self.manhattan_distance(pos, ghost_pos) <= 1:
                return False
        return True

    def get_targets(self) -> List[Tuple[int, int]]:
        targets = []
        for x in range(len(self.game.map_data)):
            for y in range(len(self.game.map_data[0])):
                if self.game.map_data[x][y] in ['.', 'o']:
                    targets.append((x, y))
        
        # Ưu tiên mục tiêu chưa thăm, sau đó theo khoảng cách
        current_pos = (int(self.pacman.grid_pos.x), int(self.pacman.grid_pos.y))
        unvisited = [t for t in targets if t not in self.visited_targets]
        if unvisited:
            targets = sorted(unvisited, key=lambda t: self.manhattan_distance(current_pos, t))
        else:
            # Nếu tất cả đã thăm, xóa visited_targets và lấy tất cả
            self.visited_targets.clear()
            targets = sorted(targets, key=lambda t: self.manhattan_distance(current_pos, t))
        
        print(f"Targets found: {targets}, Visited: {self.visited_targets}")  # Gỡ lỗi
        return targets

    def update_targets(self):
        """Cập nhật danh sách mục tiêu sau khi ăn dấu chấm."""
        self.targets = self.get_targets()
        self.current_path = []
        if self.current_target:
            self.visited_targets.add(self.current_target)  # Đánh dấu mục tiêu đã thăm
        self.current_target = None
        self.last_target_update = pygame.time.get_ticks()
        print(f"Targets updated: {self.targets}, Visited: {self.visited_targets}")  # Gỡ lỗi

    def a_star(self, start: Tuple[int, int]) -> List[Tuple[int, int]]:
        if not self.targets:
            print("No targets available for A*")  # Gỡ lỗi
            return self.get_safe_fallback_path(start)

        max_targets = min(3, len(self.targets))  # Giảm số mục tiêu để tăng tốc
        best_path = []
        min_cost = float('inf')
        for target in self.targets[:max_targets]:
            open_set = [(0, start, [start])]  # (f_score, pos, path)
            came_from = {}
            g_score = {start: 0}
            f_score = {start: self.manhattan_distance(start, target)}

            while open_set:
                current_f, current, path = heapq.heappop(open_set)
                if current == target:
                    if current_f < min_cost:
                        min_cost = current_f
                        best_path = path
                        self.current_target = target
                    break

                for neighbor in self.get_neighbors(current):
                    if not self.is_safe(neighbor):
                        continue
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.manhattan_distance(neighbor, target)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor, path + [neighbor]))

        if not best_path:
            best_path = self.get_safe_fallback_path(start)
        print(f"A* path: {best_path}")  # Gỡ lỗi
        return best_path

    def bfs(self, start: Tuple[int, int]) -> List[Tuple[int, int]]:
        if not self.targets:
            print("No targets available for BFS")  # Gỡ lỗi
            return self.get_safe_fallback_path(start)

        max_targets = min(3, len(self.targets))  # Giảm số mục tiêu để tăng tốc
        best_path = []
        min_dist = float('inf')
        for target in self.targets[:max_targets]:
            queue = deque([(start, [start])])
            visited = {start}

            while queue:
                current, path = queue.popleft()
                if current == target:
                    if len(path) < min_dist:
                        min_dist = len(path)
                        best_path = path
                        self.current_target = target
                    break

                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited and self.is_safe(neighbor):
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        if not best_path:
            best_path = self.get_safe_fallback_path(start)
        print(f"BFS path: {best_path}")  # Gỡ lỗi
        return best_path

    def get_safe_fallback_path(self, start: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Tìm ô lân cận hợp lệ, ưu tiên hướng chưa thăm gần đây."""
        neighbors = self.get_neighbors(start)
        safe_neighbors = [n for n in neighbors if self.is_safe(n)]
        
        # Ưu tiên hướng hiện tại nếu hợp lệ
        if self.last_direction != pygame.Vector2(0, 0):
            dx, dy = int(self.last_direction.x), int(self.last_direction.y)
            next_pos = (start[0] + dx, start[1] + dy)
            if next_pos in safe_neighbors:
                print(f"Fallback to current direction: {next_pos}")  # Gỡ lỗi
                return [start, next_pos]
        
        # Chọn ngẫu nhiên ô an toàn, ưu tiên chưa thăm
        current_pos = (int(self.pacman.grid_pos.x), int(self.pacman.grid_pos.y))
        unvisited_neighbors = [n for n in safe_neighbors if n not in self.visited_targets]
        if unvisited_neighbors:
            nearest = random.choice(unvisited_neighbors)
            print(f"Fallback to unvisited safe neighbor: {nearest}")  # Gỡ lỗi
            return [start, nearest]
        
        # Nếu không có ô an toàn, chọn ô bất kỳ không phải tường
        if neighbors:
            nearest = random.choice(neighbors)
            print(f"Fallback to any neighbor: {nearest}")  # Gỡ lỗi
            return [start, nearest]
        
        print("No valid neighbors for fallback")  # Gỡ lỗi
        return [start, start]

    def get_next_move(self) -> pygame.Vector2:
        if not self.mode:
            self.current_path = []
            self.last_direction = pygame.Vector2(0, 0)
            print("AI mode off")  # Gỡ lỗi
            return pygame.Vector2(0, 0)

        current_pos = (int(self.pacman.grid_pos.x), int(self.pacman.grid_pos.y))

        # Kiểm tra xem đường đi hiện tại có hợp lệ không
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            direction = pygame.Vector2(dx, dy)
            if not self.pacman.can_move(direction, self.game.map_data) or not self.is_safe(next_pos):
                print(f"Current path invalid (wall or unsafe: {next_pos}), resetting path")  # Gỡ lỗi
                self.current_path = []

        # Cập nhật đường đi nếu cần
        if (self.game.map_data[current_pos[1]][current_pos[0]] in ['.', 'o'] or
            not self.current_path):
            self.update_targets()
            if self.mode == 'A*':
                self.current_path = self.a_star(current_pos)
            elif self.mode == 'BFS':
                self.current_path = self.bfs(current_pos)
            self.last_target_update = pygame.time.get_ticks()

        # Lấy bước tiếp theo từ đường đi
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            direction = pygame.Vector2(dx, dy)
            if self.pacman.can_move(direction, self.game.map_data) and self.is_safe(next_pos):
                print(f"Next move: ({dx}, {dy}) to {next_pos}")  # Gỡ lỗi
                self.current_path.pop(0)
                self.last_direction = direction  # Lưu hướng hiện tại
                return direction
            else:
                print(f"Next move {next_pos} is invalid, trying fallback")  # Gỡ lỗi
                self.current_path = []

        # Thử hướng dự phòng
        self.current_path = self.get_safe_fallback_path(current_pos)
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            direction = pygame.Vector2(dx, dy)
            if self.pacman.can_move(direction, self.game.map_data) and self.is_safe(next_pos):
                print(f"Fallback move: ({dx}, {dy}) to {next_pos}")  # Gỡ lỗi
                self.current_path.pop(0)
                self.last_direction = direction  # Lưu hướng hiện tại
                return direction

        print("No valid move available, returning (0, 0)")  # Gỡ lỗi
        return pygame.Vector2(0, 0)

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
        self.fade_alpha = 255
        self.death_time = None
        self.respawn_time = None
        self.ai = None

        # Tải các frame hoạt ảnh
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

    def set_ai(self, game):
        self.ai = PacmanAI(self, game)

    def reset_position(self):
        self.grid_pos = pygame.Vector2(self.start_x, self.start_y)
        self.pixel_pos = self.grid_pos * TILE_SIZE
        self.set_direction(0, 0)
        self.fade_alpha = 255
        self.alive = True
        self.death_time = None
        self.respawn_time = None
        if self.ai:
            self.ai.mode = None
            self.ai.targets = self.ai.get_targets()
            self.ai.visited_targets.clear()
            self.ai.current_path = []
            self.ai.current_target = None
            self.ai.last_direction = pygame.Vector2(0, 0)

    def set_direction(self, dx, dy):
        self.desired_direction = pygame.Vector2(dx, dy)

    def update(self, map_data):
        now = pygame.time.get_ticks()
        if not self.alive:
            elapsed = now - self.death_time
            if now - self.death_time < 2000:
                self.fade_alpha = max(255 - int((elapsed / 2000) * 255), 0)
            else:
                print("Pacman chết")
                self.lives -= 1
                self.reset_position()
                self.invincible = True
                self.respawn_time = now
            return

        if self.invincible and self.respawn_time and now - self.respawn_time > 5000:
            self.invincible = False

        if now - self.last_update_time > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update_time = now

        # Sử dụng AI nếu được kích hoạt
        if self.ai and self.ai.mode:
            self.desired_direction = self.ai.get_next_move()
            print(f"AI direction: {self.desired_direction}")  # Gỡ lỗi
            if self.desired_direction != pygame.Vector2(0, 0):
                self.direction = self.desired_direction

        # Đổi hướng nếu có thể (cho điều khiển thủ công)
        if self.desired_direction != self.direction and self.can_move(self.desired_direction, map_data):
            self.direction = self.desired_direction

        # Di chuyển Pacman nếu có thể
        if self.can_move(self.direction, map_data):
            self.pixel_pos += self.direction * self.speed
            self.grid_pos = pygame.Vector2(
                int(self.pixel_pos.x / TILE_SIZE + 0.5),
                int(self.pixel_pos.y / TILE_SIZE + 0.5),
            )
        else:
            print(f"Cannot move in direction {self.direction}, resetting AI path")  # Gỡ lỗi
            if self.ai:
                self.ai.current_path = []
                self.ai.last_direction = pygame.Vector2(0, 0)

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
        if self.ai:
            self.ai.mode = None
            self.ai.current_path = []
            self.ai.current_target = None
            self.ai.last_direction = pygame.Vector2(0, 0)

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