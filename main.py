import pygame
import math
from queue import PriorityQueue

WIDTH = 800
HEIGHT = 800
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,255,0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
BLACK = (0,0,0)
TURQ = (64, 224, 208)

FPS = 60
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('pathFinding')

# node needs to hold value, keep track of where it is (row, column, position) in grid
# needs to know width of node and keep track of neighbors and color
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        # need to keep track of x,y
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    # methods tell state of node
    def get_pos(self):
        return self.row, self.col

    # if self.color == WHITE square haven't looked yet, RED have already looked at it, BLACK is barrier
    # orange is start node, purple is path
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQ

    def make_path(self):
        self.color = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color,(self.x, self.y, self.width, self.width))

    def update_neighbor(self, grid):
        #self.neighbors = []
        # checks if row is less than total amount of rows -1, this is so if at row 50 cant go down further
        # check if spot down 1 is a barrier(BLACK) if it isn't, append spot to neighbors
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    # lt stands for less than, handles when two spots are compared together
    # if self and other spot
    #def __lt__(self, other):
        #return False

def heu(p1, p2):
    # have to find distance between p1 and p2, expect x,y or row,col, using manhattan distance(L distance)
    x1, y1 = p1
    x2, y2 = p2
    # can split variable p2 = (1, 9), abs(absolute distance is built in function)
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    # can call function because of lambda, ex: draw = lambda: print("hello")
    count = 0
    open_set = PriorityQueue()
    # .put is same as append/push, add to priority queue, add start node with f score
    # count to keep track of when items were inserted in queue, if two items have f score, go with first insert
    open_set.put((0, count, start))
    # dictionary is going to keep track of what node did node come from, node c from d etc.
    came_from = {}

    #g_score = {spot: float('inf') for row in grid for spot in row} # list comp
    g_score = {}
    for row in grid:
        for spot in row:
            g_score[spot] = float('inf')
    g_score[start] = 0

    f_score = {}
    for row in grid:
        for spot in row:
            f_score[spot] = float('inf')
    # f_score is estimated distance from start node to end node
    f_score[start] = heu(start.get_pos(), end.get_pos())
    # checks if something in queue
    open_set_hash = {start}
    desc = {}
    while not open_set.empty(): # algorithm will run until open set is empty, consider every possible node
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # want node from tuple in open_set. current is current node looking at
        open_set_hash.remove(current)

        if current == end: # if current node is the end node, then shortest path was found
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1 # assume all edges are 1, going 1 more node over
            # if new path to neighbor is shorter, g_score can change depending on what node on
            # if we found better way to reach neighbor than found before, update path and store it
            if temp_g_score < g_score[neighbor]: # checks is g score of current is less than neighbors
                came_from[neighbor] = current # puts previous node in dictionary
                g_score[neighbor] = temp_g_score # sets g score of neighbor to new
                # set f_cost of neighbor
                f_score[neighbor] = temp_g_score + heu(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False

def make_grid(rows, width):
    grid = []
    # gap is width of each cube should be
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            # i is going to be row and j is going to be col, gap is width, rows is total rows
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        # start = 0, 1 * gap(50) = (0, 50), end = width(800), 1 * gap(50) = (800,50) == (0,50), (800,50)
        pygame.draw.line(window, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, width))

def draw(window, grid, rows, width):
    window.fill(BLACK)
    for row in grid:
        for spot in row:
            # gets grid and calls function from Node class
            spot.draw(window)
    # grid is drawn over spots
    draw_grid(window, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos
    row = y // gap
    col = x // gap
    # gap is 800 / rows, x and y are from pygame.clicked func, row = y divided by width of cube
    return row, col

def main(window, width):
    ROWS = 50
    # grid going to have 50 rows with a width of 800, gap(size of cube) = 800//50 = 16
    grid = make_grid(ROWS,width)

    start = None
    end = None

    clock = pygame.time.Clock()
    systemOn = True
    started = False
    while systemOn:
        draw(window, grid, ROWS, width)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                systemOn = False
            # [0] is for left button on mouse
            if pygame.mouse.get_pressed()[0]:

                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                # using row and col from function, can now get item from grid(matrix)
                spot = grid[row][col]

                if not start and spot != end: # if start has not been placed
                    start = spot
                    start.make_start()
                elif not end and spot != start: # if end has not been declared
                    end = spot
                    end.make_end()
                elif spot != end and spot != start: # if start/end have been declared and spot != end/start
                    spot.make_barrier()
            # [2] is for right button on mouse
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                # using row and col from function, can now get item from grid(matrix)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN: # if key pressed run algorithim
                if event.key == pygame.K_SPACE and start and end:
                    # for spot grid/row call function
                    for row in grid:
                        for spot in row:
                            spot.update_neighbor(grid)
                    algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
                    # call algorithm function, pass a function call
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WINDOW, WIDTH)

