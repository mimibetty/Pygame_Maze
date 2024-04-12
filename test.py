import sys
import pygame
from queue import PriorityQueue
import time


class Node():
    def __init__(self, state, parent, action, priority = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.priority = priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        # if self.save_cost is None:
        #     return self.cost < other.cost
        # else:
        return self.priority < other.priority

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():

    def __init__(self, filename):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.player_pos = self.start
        self.solution = None

    def move_player(self, direction):
        row, col = self.player_pos
        if direction == "up":
            new_pos = (row - 1, col)
        elif direction == "down":
            new_pos = (row + 1, col)
        elif direction == "left":
            new_pos = (row, col - 1)
        elif direction == "right":
            new_pos = (row, col + 1)
        else:
            return

        if (
            0 <= new_pos[0] < self.height
            and 0 <= new_pos[1] < self.width
            and not self.walls[new_pos[0]][new_pos[1]]
        ):
            self.player_pos = new_pos
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("â–ˆ", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result


    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def solveA(self):
        """Finds a solution to the maze, if one exists."""

        # Keep track of the number of states explored
        self.num_explored = 0

        # Initialize the frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None, priority=0)
        frontier = PriorityQueue()
        frontier.put(start)  # Put the start node with priority 0

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until a solution is found
        while not frontier.empty():
            # Choose a node from the frontier with the lowest priority
            node = frontier.get()
            self.num_explored += 1

            # If the node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark the node as explored
            self.explored.add(node.state)

            # Add neighbors to the frontier
            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    # Calculate g(x) as the steps from the start to the current state
                    actions = []
                    g_score = len(actions) + 1
                    # Calculate h(x) as the Euclidean distance from the current state to the goal
                    h_score = self.get_distance(state, self.goal)
                    # Calculate the priority as the sum of g(x) and h(x)
                    priority = g_score + h_score
                    child = Node(state=state, parent=node, action=action, priority=priority)
                    frontier.put(child)

        raise Exception("No solution")

    def get_distance(self, p1, p2):
        """Calculates the Euclidean distance between two points."""
        x1, y1 = p1
        x2, y2 = p2
        return abs((x2 - x1) + (y2 - y1)) 

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)
    def draw(self):
        cell_size = 50
        wall_color = (40, 40, 40)
        start_color = (255, 0, 0)
        goal_color = (0, 171, 28)
        solution_color = (220, 235, 113)
        explored_color = (212, 97, 85)
        empty_color = (237, 240, 252)
        hint_color = (50, 171, 28)  # Cyan color for hint
        show_hint = False  # Flag to indicate whether to show the hint
        hint_text = "Press 'H' for a hint"

        pygame.init()

        width = self.width * cell_size
        height = self.height * cell_size
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Maze Game")

        clock = pygame.time.Clock()
        running = True

        start_time = time.time()  # Get the current time when the game starts

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_player("up")
                    elif event.key == pygame.K_DOWN:
                        self.move_player("down")
                    elif event.key == pygame.K_LEFT:
                        self.move_player("left")
                    elif event.key == pygame.K_RIGHT:
                        self.move_player("right")
                    elif event.key == pygame.K_h:
                        show_hint = True  # Set the flag to show the hint

            if self.player_pos == self.goal:
                screen.fill((0, 0, 0))  # Fill the screen with black color
                font = pygame.font.Font(None, 36)
                congrats_text = font.render("Congratulations!", True, (255, 255, 255))  # Render the text in white color
                congrats_rect = congrats_text.get_rect(center=(width // 2, height // 2))  # Center the text on the screen
                screen.blit(congrats_text, congrats_rect)  # Draw the text on the screen

                pygame.display.flip()
                continue

            screen.fill(empty_color)  # Fill the screen with the empty color

            for i in range(self.height):
                for j in range(self.width):
                    if self.walls[i][j]:
                        pygame.draw.rect(screen, wall_color, (j * cell_size, i * cell_size, cell_size, cell_size))
                    elif (i, j) == self.start:
                        pygame.draw.rect(screen, start_color, (j * cell_size, i * cell_size, cell_size, cell_size))
                    elif (i, j) == self.goal:
                        pygame.draw.rect(screen, goal_color, (j * cell_size, i * cell_size, cell_size, cell_size))
                    elif show_hint and self.solution is not None and (i, j) in self.solution[1]:
                        pygame.draw.rect(screen, hint_color, (j * cell_size, i * cell_size, cell_size, cell_size))
            pygame.draw.rect(screen, explored_color, (self.player_pos[1] * cell_size, self.player_pos[0] * cell_size, cell_size, cell_size))

            # Draw [H is hint button]   
            pygame.draw.rect(screen, hint_color, (10, height - 35, len(hint_text) * 12, 25))
            font = pygame.font.Font(None, 20)
            hint_surface = font.render(hint_text, True, (0, 0, 0))
            screen.blit(hint_surface, (15, height - 30))

             # Draw time
            current_time = round(time.time() - start_time)  # Calculate the elapsed time since the game started
            time_surface = font.render("Time: " + str(current_time) + " seconds", True, (255, 255, 0))
            screen.blit(time_surface, (15, 15))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
# print("Maze:")
# m.print()
# print("Solving...")
m.solveA()
print("States Explored:", m.num_explored)
# print("Solution:")

m.output_image("maze.png", show_explored=True)
m.draw()