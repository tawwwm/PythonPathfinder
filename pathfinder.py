#REQUIRES INSTALLING COLORSPY AND PYGAME TO RUN
import pygame
import colorspy as colors
import math
import random
from queue import PriorityQueue

WIDTH = 500
WIN = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("Pathfinder")

class Node:

	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = colors.orange
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	#RETURN FUNCTIONS
	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == colors.golden

	def is_open(self):
		return self.color == colors.orange

	def is_obstacle(self):
		return self.color == colors.blue

	def is_start(self):
		return self.color == colors.green

	def is_finish(self):
		return self.color == colors.red

	#UPDATE FUNCTIONS
	def reset(self):
		self.color = colors.orange

	def make_closed(self):
		self.color = colors.golden

	def make_open(self):
		self.color = colors.orange

	def make_obstacle(self):
		self.color = colors.blue

	def make_start(self):
		self.color = colors.green

	def make_finish(self):
		self.color = colors.red

	def make_path(self):
		self.color = colors.turquoise

	def draw(self,win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self,grid):
		self.neighbors = []
		#BELOW
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
			self.neighbors.append(grid[self.row + 1][self.col])
		#ABOVE
		if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
			self.neighbors.append(grid[self.row - 1][self.col])
		#LEFT
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
			self.neighbors.append(grid[self.row][self.col + 1])
		#RIGHT
		if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self,other):
		return False


def h(p1,p2):
	x1,y1 = p1
	x2,y2 = p2
	return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw):
	steps = 0
	pathway = []
	while current in came_from:
		steps+=1
		pathway.insert(0,current.get_pos())
		current = came_from[current]
		current.make_path()
		draw()

	print(pathway)
	print("Path shown in turquoise.")
	print("Number of steps:", steps)


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	#Keeps track of nodes
	came_from = {}
	#Keeps track of distance from start node to current node
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	#Keeps track of current distace to end node
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		#If current node is the end complete
		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_finish()
			return True
		
		#Otherwise consider neighbouring nodes	
		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
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
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Node(i, j, gap, rows)
			grid[i].append(spot)

	return grid

def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, colors.white, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, colors.white, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(colors.orange)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row,col

def main(win,width):

	print("Click SPACE to run pathfinder, ESC to reset, R to add 10 random obstacles")

	ROWS = 10
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True 
	started = False

	grid[9][7].make_obstacle()
	grid[8][7].make_obstacle()
	grid[6][7].make_obstacle()
	grid[6][8].make_obstacle()

	while run:
		draw(win, grid, ROWS, width)
		grid[0][0].make_start()
		grid[9][9].make_finish()
		start = grid[0][0]
		end = grid[9][9]


		

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			
			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row,col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if spot != start and spot != end:
					spot.make_obstacle()

			if pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row,col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if spot != start and spot != end:
					spot.make_open()
					

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)


				if event.key == pygame.K_ESCAPE:
					start = None
					end = None
					grid = make_grid(ROWS, width)


				if event.key == pygame.K_r:
					for i in range(10):
						random_x = random.randrange(10)
						random_y = random.randrange(10)
						target = grid[random_x][random_y]

						if target != start and target != end:
							if target.col != colors.blue:
								target.make_obstacle()
	pygame.quit()

main(WIN, WIDTH)