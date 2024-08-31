import heapq
import time
import pygame
import sys
import random
import argparse

parser = argparse.ArgumentParser(description='Pathfinder')
parser.add_argument('algorithm', type=str, choices=['bfs', 'dfs', 'greedy', 'a*'], help='Pathfinding Algorithm')

args = parser.parse_args()

random.seed()

window_width = 500
window_height = 500

window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Pathfinding')

columns = 25
rows = 25

box_width = window_width // columns
box_height = window_height // rows

grid = []


class Box:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.frontier_cells = []

    def __lt__(self, other):
        return self.x < other.x


    def draw(self, window, color):
        pygame.draw.rect(window, color, 
                        (self.x * box_width, 
                         self.y * box_height, 
                         box_width - 2, 
                         box_height - 2))
        
    # Used for pathfinding
    def set_neighbours(self):
        self.neighbours = []
        n = []

        if self.x > 0 and not grid[self.x - 1][self.y].wall:
            n.append(grid[self.x - 1][self.y])
        
        if self.x < columns - 1 and not grid[self.x + 1][self.y].wall:
            n.append(grid[self.x + 1][self.y])

        if self.y > 0 and not grid[self.x][self.y - 1].wall:
            n.append(grid[self.x][self.y - 1])
        
        if self.y < rows - 1 and not grid[self.x][self.y + 1].wall:
            n.append(grid[self.x][self.y + 1])
        
        random.shuffle(n)
        self.neighbours.extend(n)

    # Used for maze generation
    def set_frontier_cells(self):
        n = []

        if self.x > 1 and grid[self.x - 2][self.y].wall:
            n.append(grid[self.x - 2][self.y])
        
        if self.x < columns - 2 and grid[self.x + 2][self.y].wall:
            n.append(grid[self.x + 2][self.y])

        if self.y > 1 and grid[self.x][self.y - 2].wall:
            n.append(grid[self.x][self.y - 2])
        
        if self.y < rows - 2 and grid[self.x][self.y + 2].wall:
            n.append(grid[self.x][self.y + 2])
        
        random.shuffle(n)
        self.frontier_cells.extend(n)


# Variation of Prim's algorithm for maze generation
def generate_maze(grid):
    visited = set()

    # Block all boxes
    for r in range(rows):
        for c in range(columns):
            grid[r][c].wall = True

    # Starting point
    r = random.randint(0, rows-1)
    c = random.randint(0, columns-1)
    visited.add((r, c))

    total_frontier_cells = set()
    grid[r][c].set_frontier_cells()
    grid[r][c].wall = False
    total_frontier_cells.update(grid[r][c].frontier_cells)

    while total_frontier_cells:
        # Picking random frontier cell
        frontier = random.choice(list(total_frontier_cells))
        r, c = frontier.x, frontier.y

        # Randomly connecting the frontier to a visited cell
        moves = [(r-2, c, r-1, c), (r+2, c, r+1, c), (r, c-2, r, c-1), (r, c+2, r, c+1)]
        random.shuffle(moves)

        for r1, c1, r2, c2 in moves:
            if r1 in range(rows) and c1 in range(columns) and not grid[r1][c1].wall:
                grid[r2][c2].wall = False
                break

        frontier.set_frontier_cells()
        frontier.wall = False
        total_frontier_cells.update(frontier.frontier_cells)
        total_frontier_cells.remove(grid[r][c])

    for c in range(columns):
        for r in range(rows):
            grid[c][r].set_neighbours()


# Populating and generating maze
for c in range(columns):
    grid.append([Box(c, r) for r in range(rows)])

for c in range(columns):
    for r in range(rows):
        grid[c][r].set_neighbours()

generate_maze(grid)


# Pathfinding Algorithms
global queue
queue = []
def bfs(target_box):
    current_box = queue.pop(0)
    current_box.visited = True

    if current_box == target_box:
        return True
    
    for n in current_box.neighbours:
        if not n.queued and not n.wall:
            n.queued = True
            queue.append(n)
    
    return False


global stack
stack = []
def dfs(target_box):
    current_box = stack.pop()
    current_box.queued = True
    current_box.visited = True
    
    if current_box == target_box:
        return True
    
    for n in current_box.neighbours:
        if not n.queued and not n.wall:
            stack.append(n)
    
    return False


def man_distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

global pq 
pq = []
heapq.heapify(pq)
def greedy_search(target_box):
    p, current_box = heapq.heappop(pq)
    current_box.queued = True
    current_box.visited = True
    
    if current_box == target_box:
        return True
    
    for n in current_box.neighbours:
        if not n.queued and not n.wall:
            heapq.heappush(pq, (man_distance(n, target_box), n))
    
    return False


global cost_so_far
cost_so_far = dict()
def a_star(target_box):
    p, current_box = heapq.heappop(pq)
    current_box.queued = True
    current_box.visited = True
    
    if current_box == target_box:
        return True
    
    for n in current_box.neighbours:
        new_cost = cost_so_far[current_box] + 1

        if (not n.queued and not n.wall) and (n not in cost_so_far or new_cost < cost_so_far[n]):
            cost_so_far[n] = new_cost
            priority = new_cost + man_distance(n, target_box)
            heapq.heappush(pq, (priority, n))
    
    return False


def main():
    begin_search = False
    target_box_set = False
    searching = True
    target_box = None
    start_box = None

    while True:
        for event in pygame.event.get():
            # Quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Mouse Click
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Set Start
                if event.button == 1 and not start_box:   
                    r = x // box_width
                    c = y // box_height
                    start_box = grid[r][c]
                    start_box.start = True
                    start_box.visited = True  
                    queue.append(start_box) 
                    stack.append(start_box)
                    cost_so_far[start_box] = 0

                # Set Target
                if event.button == 3 and not target_box_set:
                    r = x // box_width
                    c = y // box_height
                    target_box = grid[r][c]
                    target_box.target = True
                    target_box_set = True

                if start_box and target_box and args.algorithm == 'greedy':
                    heapq.heappush(pq, (man_distance(start_box, target_box), start_box))

                if start_box and target_box and args.algorithm == 'a*':
                    heapq.heappush(pq, (0, start_box))

            # Hold mouse and drag
            elif event.type == pygame.MOUSEMOTION:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                # Draw Wall
                if event.buttons[0]:
                    r = x // box_width
                    c = y // box_height
                    if not grid[r][c].start and not grid[r][c].target:
                        grid[r][c].wall = True

                # Erase Wall
                if event.buttons[2]:
                    r = x // box_width
                    c = y // box_height

                    if grid[r][c].wall:
                        grid[r][c].wall = False
                        for r2 in range(r-1, r+2):
                            for c2 in range(c-1, c+2):
                                grid[r2][c2].set_neighbours()

            # Start/Reset Algorithm
            if event.type == pygame.KEYDOWN and target_box_set:
                if event.key == pygame.K_SPACE:
                    begin_search = True

                # Clear previous path
                if event.key == pygame.K_TAB:
                    begin_search = False
                    searching = True
                    start_box = None
                    target_box = None
                    target_box_set = False

                    stack.clear()
                    queue.clear()
                    pq.clear()
                    heapq.heapify(pq)
                    cost_so_far.clear()

                    for r in range(rows):
                        for c in range(columns):
                            grid[r][c].start = False
                            grid[r][c].target = False
                            grid[r][c].queued = False
                            grid[r][c].visited = False
                            
        # Pathfinding
        if begin_search and searching:
            if stack and args.algorithm == 'dfs':
                searching = not dfs(target_box)

            if queue and args.algorithm == 'bfs':
                searching = not bfs(target_box)

            if pq and args.algorithm == 'greedy':
                searching = not greedy_search(target_box)

            if pq and args.algorithm == 'a*':
                searching = not a_star(target_box)


        window.fill((128, 128, 128))

        for c in range(columns):
            for r in range(rows):
                box = grid[c][r]
                box.draw(window, (255, 255, 255)) 

                if box.queued:
                    box.draw(window, (69, 123, 157))

                if box.visited:
                    box.draw(window, (168, 218, 220)) 

                if box.start:
                    box.draw(window, (56, 176, 0))

                if box.wall:
                    box.draw(window, (0, 0, 0))

                if box.target:
                    box.draw(window, (230, 57, 70)) 

        time.sleep(0.005)              
        pygame.display.flip()

main()