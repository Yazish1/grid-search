from collections import deque
import heapq
import time
WALL = -1
EMPTY = 1
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def random_grid(rows, cols, wall_density, weight_density, rng):
    grid = make_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            if (r==0 and c== 0) or (r == rows-1 and c == cols-1):
                continue
            pwall = rng.random()
            if pwall < wall_density:
                grid[r][c] = WALL
    scatter_weights(grid, (0,0), (rows-1,cols-1), weight_density, 9, rng)
    return grid
def make_grid(rows, cols):
    grid = [[EMPTY]*cols for _ in range(rows)]
    return grid

def start_search(algorithm, grid, start, goal):
    t0 = time.perf_counter()
    result = algorithm(grid, start, goal)
    time_ms = (time.perf_counter() - t0) * 1000
    path = build_path(result["parent_of"], goal) if result["found"] else []
    return (result, time_ms, path)

def build_path(parent_of, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent_of[node]
    return path[::-1]

def path_cost(grid, path):
    total = 0
    for r,c in path[1:]:
        total += grid[r][c]
    return total

def scatter_weights(grid, start, goal, density, max_weight, rng):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if (r,c) != start and (r,c) != goal and grid[r][c] == EMPTY:
                prob = rng.random()
                if prob < density:
                    grid[r][c] = rng.randint(2, max_weight)

def neighbours(grid, node):
    rows, cols = len(grid), len(grid[0])
    r, c = node
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != WALL:
            yield (nr, nc)

def bfs(grid, start: tuple , goal: tuple) -> dict:
    frontier = deque([start])
    parent_of = {start: None}
    visit_order = []
    nodes_popped = 0
    max_frontier_size = 0
    nodes_generated = 0
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        node = frontier.popleft()
        nodes_popped += 1
        visit_order.append(node)
        if node == goal:
            return {"found": True, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,"visit_order": visit_order}
    
        for neighbour in neighbours(grid, node):
            if neighbour not in parent_of:
                parent_of[neighbour] = node
                frontier.append(neighbour)
                nodes_generated += 1
    return {"found": False, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,"visit_order": visit_order}

def dfs(grid, start: tuple, goal: tuple) -> dict:
    frontier = [start]
    parent_of = {start: None}
    visited = set()
    visit_order = []
    nodes_popped = 0
    max_frontier_size = 0
    nodes_generated = 0
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        node = frontier.pop()
        if node in visited:
            continue
        visited.add(node)
        nodes_popped += 1
        visit_order.append(node)

        if node == goal:
            return {"found": True, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,"visit_order": visit_order}

        for neighbour in neighbours(grid, node):
            if neighbour not in visited:
                parent_of[neighbour] = node
                frontier.append(neighbour)
                nodes_generated += 1

    return {"found": False, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,"visit_order": visit_order}


def dijkstra(grid, start, goal):
    frontier = []
    heapq.heappush(frontier, (0,start))
    parent_of = {start: None}
    cost_of = {start: 0}
    visit_order = []
    visited = set()
    nodes_popped = 0
    max_frontier_size = 0
    nodes_generated = 0
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        cost, node = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        nodes_popped += 1
        visit_order.append(node)

        if node == goal:
            return {"found": True, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,"visit_order": visit_order}
        
        for neighbour in neighbours(grid, node):
            if neighbour in visited:
                continue
            nr, nc = neighbour
            new_cost = cost_of[node] + grid[nr][nc]
            if new_cost < cost_of.get(neighbour, float('inf')):
                cost_of[neighbour] =new_cost
                parent_of[neighbour]=node
                heapq.heappush(frontier, (new_cost, neighbour))
                nodes_generated += 1
        
    return {"found": False, "parent_of": parent_of, "nodes_popped": nodes_popped, "nodes_generated": nodes_generated,
            "max_frontier_size": max_frontier_size,"visit_order": visit_order}
