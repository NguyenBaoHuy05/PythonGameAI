from math import sqrt
from collections import deque
import random
import heapq

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def bfs_len(map_data, start, goal):
    queue = deque([start])
    visited = {start: None}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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

    # Truy ngược để đếm số bước
    length = 0
    node = goal
    while visited[node] is not None:
        node = visited[node]
        length += 1
    return length


def near_pacman(map_data, start, pacman_pos):
    best_dir = (1, 0)
    max_dist = -float("inf")

    for dx, dy in directions:
        nx, ny = start[0] + dx, start[1] + dy
        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]):
            if map_data[ny][nx] != "#":
                dist = bfs_len(map_data, (nx, ny), pacman_pos)
                if dist > max_dist:
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
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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


def bfs_direction(map_data, start, goal, ghost_positions=None):
    if ghost_positions is None:
        ghost_positions = []
    if start == goal:
        return (0, 0)
    rows, cols = len(map_data), len(map_data[0])
    queue = []
    heapq.heappush(queue, (0, start))  # (cost, position)
    visited = {start: None}
    costs = {start: 0}  # Track cost to reach each node

    while queue:
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
                        ghost_cost += 100  # High cost near ghost
                    elif dist_to_ghost <= 4:
                        ghost_cost += 20  # Moderate cost
                new_cost = costs[current] + 1 + ghost_cost
                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    visited[neighbor] = current
                    heapq.heappush(queue, (new_cost, neighbor))

    if goal not in visited:
        return (0, 0)

    node = goal
    while visited[node] != start:
        node = visited[node]
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy) if (dx, dy) != (0, 0) else (0, 0)


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
    while open_set:
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
                        ghost_cost += 100
                    elif dist_to_ghost <= 4:
                        ghost_cost += 20
                tentative_g_score = current_g + 1 + ghost_cost
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
        return (0, 0)
    node = goal
    while came_from[node] != start:
        node = came_from[node]
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy) if (dx, dy) != (0, 0) else (0, 0)
