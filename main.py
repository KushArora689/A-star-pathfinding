import pygame 
import math 
from queue import PriorityQueue
import tkinter as tk
from tkinter import simpledialog 


#colors 
WHITE = (148, 148, 148)

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (255,0,255)

PINK = (255, 102, 204)
ORANGE = (255,165,0)
GREY = (255,255,255)
AQUA = (118,238,198)


#Node class, each square in the grid will be an instance of this class 
class Node:
    def __init__(self, row, col, width , total_rows):
        self.row = row
        self.col = col 
        self.width = width 
        self.total_rows = total_rows
        self.x = row * width 
        self.y = col * width 
        self.color = WHITE
        self.neighbors = []
        
    
    #gets row and col
    def get_position(self):
        return self.row, self.col
    
    def is_obstacle(self):
        return self.color == BLACK
    
    def reset(self):
        self.color = WHITE

    def set_closed(self):
        self.color = AQUA

    def set_open(self):
        self.color = GREEN

    #obstacles are nodes that cannot be visited 
    def set_obstacle(self):
        self.color = BLACK
    
    def set_end(self):
        self.color = RED
    
    def set_path(self):
        self.color = PINK
    
    #draw function from pygame, draws the window
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def create_start(self):
        self.color = ORANGE         
    
    #need to keep track of neighbors for this algorithm so we update neighbor
    def update_neighbor(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle(): #check for up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle(): #check for down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle(): #check for right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle(): #check for left
            self.neighbors.append(grid[self.row][self.col - 1])
	    
# the hueristic which simply find the shortest path from one node to another   
def hueristic(p1, p2):
    x1, y1 = p1 
    x2, y2 = p2 
    return abs(x1 - x2) + abs(y1 - y2)

#draws the path after start node and end node has been selected, and space key entered
def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.set_path()
		draw()

#A Star algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {}
    for row in grid:
        for node in row:
            g_score[node] = float("inf")

    g_score[start] = 0
    f_score = {}
    for row in grid:
        for node in row:
            f_score[node] = float("inf")

    f_score[start] = hueristic(start.get_position(), end.get_position())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.set_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + hueristic(neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_open()

        draw()
        if current != start:
            current.set_closed()

    return False

#creates a nested list of nodes
def create_grid(rows, width):
    grid = []
    spacing = width // rows 
    for row in range(rows):
        grid.append([])
        for col in range(rows):
            node = Node(row, col, spacing, rows)
            grid[row].append(node)
   
    return grid

#draws the grid
def draw(wind, grid, rows, width):
    spacing = width // rows 
    wind.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(wind)
    for i in range(rows):
        pygame.draw.line(wind, GREY, (0, i*spacing), (width, i*spacing))
        for x in range(rows):
            pygame.draw.line(wind, GREY, (x*spacing, 0), (x*spacing, width))
    pygame.display.update()

def get_pos_mouse(pos, rows, width):
    spacing = width // rows 
    y, x = pos
    row = y // spacing
    col = x // spacing

    return row, col

def main(wind, width, rows):
    ROWS = rows
    grid = create_grid(ROWS, width)
    start = None
    end = None 
    run = True
    started = False
    while run:
        draw(wind, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue 
            #mouse button left click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_pos_mouse(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.create_start()
                elif not end and node != start:
                    end = node
                    end.set_end()
                elif node != end and node != start:
                    node.set_obstacle()
            #mouse button right click
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_pos_mouse(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None
            #key is pressed or released on keyboard       
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbor(grid)
                    #run the main algorithm
                    algorithm(lambda: draw(wind, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = create_grid(ROWS, width)
    pygame.quit()

def get_number_of_rows():
    root = tk.Tk()
    root.withdraw()
    while True:  
        rows = simpledialog.askinteger("A* PathFinder", "Enter the number of rows you want (Must be between 5 and 100):")
        if rows is not None and rows in range(5, 101):
            return rows
        elif rows is not None:
            print("Please enter a positive integer.")
        elif rows is None:
            root.destroy()
        

ROWS = get_number_of_rows()
if ROWS is not None:
    width = 800
    window = pygame.display.set_mode((width, width))
    pygame.display.set_caption("A* PathFinder")
    main(window, width, ROWS)
