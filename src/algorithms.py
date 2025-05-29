from math import sqrt
from collections import deque
import random
import heapq

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def count_open_neighbors(map_data, x, y):
    count = 0
    rows, cols = len(map_data), len(map_data[0])
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= ny < rows and 0 <= nx < cols and map_data[ny][nx] != "#":
            count += 1
    return count


def bfs_len(map_data, start, goal):
    queue = deque([start])
    visited = {start: None}
    rows, cols = len(map_data), len(map_data[0])

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= ny < rows and 0 <= nx < cols:
                if map_data[ny][nx] != "#" and (nx, ny) not in visited:
                    visited[(nx, ny)] = current
                    queue.append((nx, ny))

    if goal not in visited:
        return float("inf")

    length = 0
    node = goal
    while visited[node] is not None:
        node = visited[node]
        length += 1
    return length


def near_pacman(map_data, start, pacman_pos):
    best_dir = (1, 0)
    max_dist = float("inf")

    for dx, dy in directions:
        nx, ny = start[0] + dx, start[1] + dy
        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]):
            if map_data[ny][nx] != "#":
                dist = bfs_len(map_data, (nx, ny), pacman_pos)
                if dist < max_dist:
                    max_dist = dist
                    best_dir = (dx, dy)

    return best_dir


def dfs_shortest_path(map_data, start, goal):
    stack = [start]
    visited = {start: None}
    rows = len(map_data)
    cols = len(map_data[0])
    while stack:
        current = stack.pop()
        if current == goal:
            break
        for dx, dy in directions:
            if 0 <= current[0] + dx < cols and 0 <= current[1] + dy < rows:
                nx, ny = current[0] + dx, current[1] + dy
                if map_data[ny][nx] != "#" and (nx, ny) not in visited:
                    visited[(nx, ny)] = current
                    stack.append((nx, ny))
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = visited.get(node)
        if node is None:
            return []
    path.reverse()
    return path


def bfs_shortest_path(map_data, start, goal):
    queue = deque()
    queue.append(start)
    visited = {start: None}
    rows = len(map_data)
    cols = len(map_data[0])
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if map_data[ny][nx] != "#" and (nx, ny) not in visited:
                    visited[(nx, ny)] = current
                    queue.append((nx, ny))
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = visited.get(node)
        if node is None:
            return []
    path.reverse()
    return path


def ucs_direction(map_data, start, goal, ghost_positions=None):
    if ghost_positions is None:
        ghost_positions = []
    if start == goal:
        return random.choice(directions)
    rows, cols = len(map_data), len(map_data[0])
    queue = []
    heapq.heappush(queue, (0, start))
    visited = {start: None}
    costs = {start: 0}
    max_nodes = 1500  # Tăng max_nodes
    node_count = 0

    while queue and node_count < max_nodes:
        node_count += 1
        current_cost, current = heapq.heappop(queue)
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if 0 <= ny < rows and 0 <= nx < cols and map_data[ny][nx] != "#":
                ghost_cost = 0
                for ghost_pos in ghost_positions:
                    dist_to_ghost = heuristic(neighbor, ghost_pos)
                    if dist_to_ghost <= 2:
                        ghost_cost += 100  # Giảm chi phí
                    elif dist_to_ghost <= 5:
                        ghost_cost += 20
                open_neighbors = count_open_neighbors(map_data, nx, ny)
                dead_end_cost = (
                    50
                    if open_neighbors <= 1
                    else 10 if open_neighbors == 2 else 0
                )  # Giảm chi phí
                new_cost = costs[current] + 1 + ghost_cost + dead_end_cost
                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    visited[neighbor] = current
                    heapq.heappush(queue, (new_cost, neighbor))

    if goal not in visited:
        valid_directions = [
            (dx, dy)
            for dx, dy in directions
            if 0 <= start[1] + dy < rows
            and 0 <= start[0] + dx < cols
            and map_data[start[1] + dy][start[0] + dx] != "#"
        ]
        return random.choice(valid_directions) if valid_directions else (0, 0)

    node = goal
    while visited[node] != start:
        node = visited[node]
        if node is None:
            valid_directions = [
                (dx, dy)
                for dx, dy in directions
                if 0 <= start[1] + dy < rows
                and 0 <= start[0] + dx < cols
                and map_data[start[1] + dy][start[0] + dx] != "#"
            ]
            return (
                random.choice(valid_directions) if valid_directions else (0, 0)
            )
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy)


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_direction(map_data, start, goal, ghost_positions=None):
    if ghost_positions is None:
        ghost_positions = []
    rows, cols = len(map_data), len(map_data[0])
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    max_nodes = 2000  # Tăng max_nodes
    node_count = 0
    while open_set and node_count < max_nodes:
        node_count += 1
        _, current_g, current = heapq.heappop(open_set)
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if 0 <= ny < rows and 0 <= nx < cols and map_data[ny][nx] != "#":
                ghost_cost = 0
                for ghost_pos in ghost_positions:
                    dist_to_ghost = heuristic(neighbor, ghost_pos)
                    if dist_to_ghost <= 2:
                        ghost_cost += 100  # Giảm chi phí
                    elif dist_to_ghost <= 5:
                        ghost_cost += 20
                open_neighbors = count_open_neighbors(map_data, nx, ny)
                dead_end_cost = (
                    50
                    if open_neighbors <= 1
                    else 10 if open_neighbors == 2 else 0
                )  # Giảm chi phí
                tentative_g_score = current_g + 1 + ghost_cost + dead_end_cost
                if (
                    neighbor not in g_score
                    or tentative_g_score < g_score[neighbor]
                ):
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(
                        open_set, (f_score, tentative_g_score, neighbor)
                    )
                    came_from[neighbor] = current
    if goal not in came_from:
        valid_directions = [
            (dx, dy)
            for dx, dy in directions
            if 0 <= start[1] + dy < rows
            and 0 <= start[0] + dx < cols
            and map_data[start[1] + dy][start[0] + dx] != "#"
        ]
        return random.choice(valid_directions) if valid_directions else (0, 0)
    node = goal
    while came_from[node] != start:
        node = came_from[node]
        if node is None:
            valid_directions = [
                (dx, dy)
                for dx, dy in directions
                if 0 <= start[1] + dy < rows
                and 0 <= start[0] + dx < cols
                and map_data[start[1] + dy][start[0] + dx] != "#"
            ]
            return (
                random.choice(valid_directions) if valid_directions else (0, 0)
            )
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy)


def dfs_direction(map_data, start, goal, ghost_positions=None, danger_range=2):
    if ghost_positions is None:
        ghost_positions = []

    def is_safe(pos):
        return all(heuristic(pos, g) > danger_range for g in ghost_positions)

    if start == goal:
        return random.choice(directions)

    rows, cols = len(map_data), len(map_data[0])
    stack = [start]
    visited = {start: None}

    while stack:
        current = stack.pop()
        if current == goal:
            break

        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if (
                0 <= ny < rows
                and 0 <= nx < cols
                and map_data[ny][nx] != "#"
                and neighbor not in visited
                and is_safe(neighbor)
            ):
                visited[neighbor] = current
                stack.append(neighbor)

    # Không đến được goal
    if goal not in visited:
        valid_dirs = [
            (dx, dy)
            for dx, dy in directions
            if 0 <= start[1] + dy < rows
            and 0 <= start[0] + dx < cols
            and map_data[start[1] + dy][start[0] + dx] != "#"
            and is_safe((start[0] + dx, start[1] + dy))
        ]
        return random.choice(valid_dirs) if valid_dirs else (0, 0)

    # Truy vết hướng
    node = goal
    while visited[node] != start:
        node = visited[node]
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy)


def bfs_direction(map_data, start, goal, ghost_positions=None, danger_range=2):
    if ghost_positions is None:
        ghost_positions = []

    def is_safe(pos):
        return all(heuristic(pos, g) > danger_range for g in ghost_positions)

    if start == goal:
        return random.choice(directions)

    rows, cols = len(map_data), len(map_data[0])
    queue = deque([start])
    visited = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if (
                0 <= ny < rows
                and 0 <= nx < cols
                and map_data[ny][nx] != "#"
                and neighbor not in visited
                and is_safe(neighbor)
            ):
                visited[neighbor] = current
                queue.append(neighbor)

    # Nếu không tới được goal
    if goal not in visited:
        valid_dirs = [
            (dx, dy)
            for dx, dy in directions
            if 0 <= start[1] + dy < rows
            and 0 <= start[0] + dx < cols
            and map_data[start[1] + dy][start[0] + dx] != "#"
            and is_safe((start[0] + dx, start[1] + dy))
        ]
        return random.choice(valid_dirs) if valid_dirs else (0, 0)

    # Truy vết lại hướng đi
    node = goal
    while visited[node] != start:
        node = visited[node]
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy)
