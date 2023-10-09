import pygame
import tkinter as tk
from tkinter import simpledialog
from queue import PriorityQueue

#Constants for colors
WHITE = (148, 148, 148)

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (255,0,255)

PINK = (255, 102, 204)
ORANGE = (255,165,0)
GREY = (255,255,255)
AQUA = (118,238,198)

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

class Grid:
    def __init__(self, rows, width):
        self.rows = rows
        self.width = width
        self.spacing = width // rows
        self.grid = self.create_grid()

    def create_grid(self):
        grid = []
        for row in range(self.rows):
            grid.append([])
            for col in range(self.rows):
                node = Node(row, col, self.spacing, self.rows)
                grid[row].append(node)
        return grid

    def draw_grid(self, window):
        window.fill(WHITE)
        for row in self.grid:
            for node in row:
                node.draw(window)
        for i in range(self.rows):
            pygame.draw.line(window, GREY, (0, i * self.spacing), (self.width, i * self.spacing))
            for x in range(self.rows):
                pygame.draw.line(window, GREY, (x * self.spacing, 0), (x * self.spacing, self.width))
        pygame.display.update()

    def get_mouse_position(self, pos):
        y, x = pos
        row = y // self.spacing
        col = x // self.spacing
        return row, col

class AStarAlgorithm:
    @staticmethod
    def hueristic(p1, p2):
        x1, y1 = p1 
        x2, y2 = p2 
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def reconstruct_path(came_from, current, draw):
        while current in came_from:
            current = came_from[current]
            current.set_path()
            draw()

    @staticmethod
    def a_star(draw, grid, start, end):
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

        f_score[start] = AStarAlgorithm.hueristic(start.get_position(), end.get_position())
        open_set_hash = {start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:
                AStarAlgorithm.reconstruct_path(came_from, end, draw)
                end.set_end()
                return True

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + AStarAlgorithm.hueristic(neighbor.get_position(), end.get_position())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.set_open()

            draw()
            if current != start:
                current.set_closed()

        return False


class MainApp:
    def __init__(self, window, width, rows):
        self.window = window
        self.width = width
        self.rows = rows
        self.grid = Grid(rows, width)
        self.start = None
        self.end = None
        self.run = True
        self.started = False

    def run_app(self):
        pygame.init()  # initialize Pygame
        while self.run:
            self.grid.draw_grid(self.window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if self.started:
                    continue
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    row, col = self.grid.get_mouse_position(pos)
                    node = self.grid.grid[row][col]
                    if not self.start and node != self.end:
                        self.start = node
                        self.start.create_start()
                    elif not self.end and node != self.start:
                        self.end = node
                        self.end.set_end()
                    elif node != self.end and node != self.start:
                        node.set_obstacle()
                elif pygame.mouse.get_pressed()[2]:
                    pos = pygame.mouse.get_pos()
                    row, col = self.grid.get_mouse_position(pos)
                    node = self.grid.grid[row][col]
                    node.reset()
                    if node == self.start:
                        self.start = None
                    elif node == self.end:
                        self.end = None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.start and self.end:
                        for row in self.grid.grid:
                            for node in row:
                                node.update_neighbor(self.grid.grid)
                        AStarAlgorithm.a_star(lambda: self.grid.draw_grid(self.window), self.grid.grid, self.start, self.end)
                    if event.key == pygame.K_c:
                        self.start = None
                        self.end = None
                        self.grid = Grid(self.rows, self.width)
        pygame.quit()  # quit Pygame 

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

if __name__ == "__main__":
    ROWS = get_number_of_rows()
    if ROWS is not None:
        width = 800
        window = pygame.display.set_mode((width, width))
        pygame.display.set_caption("A* PathFinder")
        app = MainApp(window, width, ROWS)
        app.run_app()
        pygame.quit()
