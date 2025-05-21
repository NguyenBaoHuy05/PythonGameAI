from collections import deque


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
