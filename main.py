import pygame
import time
import random
from algorithms import WALL, EMPTY, scatter_weights, bfs, dfs, build_path, dijkstra, path_cost, start_search, make_grid, random_grid


START_COLOR = (0, 200, 0)
GOAL_COLOR = (220, 0, 0)
WALL_COLOR = (30, 30, 30)
PATH_COLOR = (255, 220, 0)
VISITED_COLOR = (120, 180, 255)
EMPTY_COLOR = (255, 255, 255)
WEIGHTED_COLOR = (150, 110, 70)

ROWS, COLS = 20,20
CELL_SIZE = 20
ORIGIN_X, ORIGIN_Y = 20, 20
WINDOW_SIZE = (COLS * CELL_SIZE + 2 * ORIGIN_X, ROWS * CELL_SIZE + 2 * ORIGIN_Y)

PANEL_WIDTH = 300
GRID_AREA_WIDTH = COLS * CELL_SIZE + 2 * ORIGIN_X
WINDOW_SIZE = (GRID_AREA_WIDTH + PANEL_WIDTH, max(ROWS * CELL_SIZE + 2 * ORIGIN_Y, 620))
PANEL_BG = (20, 24, 32)
TEXT_COLOR = (230, 230, 230)

CONTROLS = [
    ("B", "BFS"),
    ("D", "DFS"),
    ("J", "Dijkstra"),
    ("G", "Scatter weights"),
    ("C", "Clear grid"),
    ("L-drag", "Draw wall"),
    ("R-drag", "Erase wall"),
]

LEGEND = [
    (START_COLOR, "Start"),
    (GOAL_COLOR, "Goal"),
    (WALL_COLOR, "Wall"),
    (VISITED_COLOR, "Visited"),
    (PATH_COLOR, "Shortest path"),
    (WEIGHTED_COLOR, "Weighted terrain"),
]


def draw_legend(screen, font, x, y, legend, line_height):
    heading = font.render("LEGEND", True, TEXT_COLOR)
    screen.blit(heading, (x, y))
    curr_height = y + line_height
    for color, label in legend:
        pygame.draw.rect(screen, color, (x, curr_height, 14, 14))
        text = font.render(label, True, TEXT_COLOR)
        screen.blit(text, (x + 24, curr_height))
        curr_height += line_height
def draw_controls(screen, font, x, y, controls, line_height):
    heading = font.render("CONTROLS", True, TEXT_COLOR)
    screen.blit(heading, (x, y))
    curr_height = y + line_height
    for entry in controls:
        string = entry[0] + " : " + entry[1]
        command = font.render(string, True, TEXT_COLOR)
        screen.blit(command, (x,curr_height))
        curr_height += line_height
def draw_stats(screen, font, x, y, result, name, time_ms, revealed_count, total_cells, path, grid, line_height):
    heading = font.render("LIVE STATS", True, TEXT_COLOR)
    screen.blit(heading, (x, y))
    if not result:
        line = font.render("Press B, D or J to run", True, TEXT_COLOR)
        screen.blit(line, (x, y+line_height))
        return
    status = ""
    if revealed_count < total_cells:
        status = "Running"
    elif result["found"]:
        status = "Done (Path found)"
    else:
        status = "Done (No Path)"
    finished_with_path = revealed_count == total_cells and len(path) > 0
    length_text = str(len(path) - 1) if finished_with_path else "-"
    cost_text = str(path_cost(grid, path)) if finished_with_path else "-"

    rows = [
        ("Algorithm", name),
        ("Status", status),
        ("Expanded", str(result["nodes_popped"])),
        ("Generated", str(result["nodes_generated"])),
        ("Frontier max", str(result["max_frontier_size"])),
        ("Path length", length_text),
        ("Path cost", cost_text),
        ("Time", f"{time_ms:.1f}ms"),
    ]
    curr_height = y + line_height
    for entry in rows:
        string = entry[0] + " : " + entry[1]
        stat = font.render(string, True, TEXT_COLOR)
        screen.blit(stat, (x,curr_height))
        curr_height += line_height

def cell_color(cell, grid, start, goal, visited, path):
    if cell == start:
        return START_COLOR
    if cell == goal:
        return GOAL_COLOR
    r, c = cell
    if grid[r][c] == WALL:
        return WALL_COLOR
    if cell in path:
        return PATH_COLOR
    if cell in visited:
        return VISITED_COLOR
    if grid[r][c] > EMPTY:
        return WEIGHTED_COLOR
    return EMPTY_COLOR

def pixel_to_cell(mx, my, origin_x, origin_y, cell_size, rows, cols):
    row = (my-origin_y)//cell_size
    if row >= rows or row < 0:
        return None
    col = (mx-origin_x)//cell_size
    if col >= cols or col < 0:
        return None
    return (row, col)

def paint_cell(grid, cell, start, goal, erase=False):
    if cell is None or cell in (start, goal):
        return
    row, col = cell
    grid[row][col] = EMPTY if erase else WALL

def advance(revealed_count, steps_per_frame, total_cells):
    if revealed_count + steps_per_frame <= total_cells:
        revealed_count+= steps_per_frame
        return revealed_count
    return total_cells

def cell_to_rect(row, col, origin_x, origin_y, cell_size):
    y = (cell_size*row)+origin_y
    x = (cell_size*col)+origin_x
    return (x,y, cell_size, cell_size)
    
def change_speed(current, delta, lowest, highest):
    return max(lowest, min(highest, current + delta))
def main():
    pygame.init()
    font = pygame.font.SysFont("consolas", 16)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Grid search")
    clock = pygame.time.Clock()
    running = True
    grid = make_grid(ROWS, COLS)
    start = (0, 0)
    goal = (ROWS - 1, COLS - 1)
    visit_order = []
    revealed_count = 0
    path = []
    steps_per_frame = 5
    last_result = None
    last_name = ""
    last_time_ms = 0.0
    rng = random.Random()

    while running:
        # --- 1. EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    result, last_time_ms, path = start_search(bfs, grid, start, goal)
                    last_result = result
                    last_name = "BFS"
                    visit_order = result["visit_order"]
                    revealed_count = 0
                elif event.key == pygame.K_d:
                    result, last_time_ms, path = start_search(dfs, grid, start, goal)
                    last_result = result
                    last_name = "DFS"
                    visit_order = result["visit_order"]
                    revealed_count = 0
                elif event.key == pygame.K_j:
                    result, last_time_ms, path = start_search(dijkstra, grid, start, goal)
                    last_result = result
                    last_name = "Dijkstra"
                    visit_order = result["visit_order"]
                    revealed_count = 0
                elif event.key == pygame.K_g:
                    scatter_weights(grid, start, goal, 0.2, 9, rng)
                elif event.key == pygame.K_c:
                    for row in range(ROWS):
                        for col in range(COLS):
                            grid[row][col] = EMPTY
                    visit_order = []
                    revealed_count = 0
                    path = []
                    last_result = None
                    last_name = ""
                    last_time_ms = 0.0

        # --- 2. HELD INPUT (dedented: runs every frame) ---
        left_held, _, right_held = pygame.mouse.get_pressed()
        if left_held or right_held:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            cell = pixel_to_cell(mouse_x, mouse_y, ORIGIN_X, ORIGIN_Y, CELL_SIZE, ROWS, COLS)
            paint_cell(grid, cell, start, goal, erase=right_held)

        # --- 3. UPDATE ---
        revealed_count = advance(revealed_count, steps_per_frame, len(visit_order))

        # --- 4. DRAW ---
        screen.fill((200, 200, 200))
        visited = set(visit_order[:revealed_count])
        shown_path = set(path) if revealed_count == len(visit_order) else set()
        for row in range(ROWS):
            for col in range(COLS):
                color = cell_color((row, col), grid, start, goal, visited, shown_path)
                rect = cell_to_rect(row, col, ORIGIN_X, ORIGIN_Y, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)

        pygame.draw.rect(screen, PANEL_BG, (GRID_AREA_WIDTH, 0, PANEL_WIDTH, WINDOW_SIZE[1]))
        draw_legend(screen, font, GRID_AREA_WIDTH + 20, 20, LEGEND, 22)
        draw_controls(screen, font, GRID_AREA_WIDTH + 20, 200, CONTROLS, 22)
        draw_stats(screen, font, GRID_AREA_WIDTH + 20, 400, last_result, last_name, last_time_ms, revealed_count, len(visit_order), path, grid, 22)

        # --- 5. SHOW and WAIT ---
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
if __name__ == "__main__":
    main()