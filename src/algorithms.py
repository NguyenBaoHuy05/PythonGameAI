from math import sqrt
from collections import deque
import random
import heapq

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def near_pacman(map_data, start, pacman_pos):
    if random.random() < 0.02:
        d = random.choice(directions)
        nx, ny = start[0] + d[0], start[1] + d[1]
        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]):
            if map_data[ny][nx] != "#":
                return (nx, ny)
    worst_direction = (0, 0)
    max_distance = -1

    for dx, dy in directions:
        nx, ny = start[0] + dx, start[1] + dy

        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]):
            if map_data[ny][nx] != "#":
                distance = sqrt(
                    (nx - pacman_pos[0]) ** 2 + (ny - pacman_pos[1]) ** 2
                )

                if distance < max_distance:
                    max_distance = distance
                    worst_direction = (dx, dy)

    return worst_direction


def dfs_shortest_path(map_data, start, goal):
    stack = [start]
    visited = {start: None}
    rows = len(map_data)
    cols = len(map_data[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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


def bfs_direction(map_data, start, goal):
    if start == goal:
        return (0, 0)
    rows, cols = len(map_data), len(map_data[0])

    op = 0
    queue = deque([start])
    visited = {start: None}

    while queue:
        current = queue.popleft()
        op += 1
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if 0 <= ny < rows and 0 <= nx < cols:
                if map_data[ny][nx] != "#" and neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

    if goal not in visited:
        return (0, 0)

    node = goal
    while visited[node] != start:
        node = visited[node]
    dx = node[0] - start[0]
    dy = node[1] - start[1]
    return (dx, dy) if (dx, dy) != (0, 0) else (0, 0)


def heuristic(a, b):
    # Hàm đánh giá heuristic: khoảng cách Manhattan
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_direction(map_data, start, goal):
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
                tentative_g_score = current_g + 1

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
