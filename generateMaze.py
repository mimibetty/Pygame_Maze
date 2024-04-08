import random

def generate_maze(m, n):
    maze = [['#' for _ in range(n)] for _ in range(m)]

    def dfs(row, col):
        maze[row][col] = ' '

        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_row, new_col = row + dx, col + dy
            if 0 <= new_row < m and 0 <= new_col < n and maze[new_row][new_col] == '#':
                maze[new_row][new_col] = ' '
                maze[row + dx // 2][col + dy // 2] = ' '
                dfs(new_row, new_col)

    start_row, start_col = random.randint(0, m // 2) * 2, random.randint(0, n // 2) * 2
    dfs(start_row, start_col)
    maze[start_row][start_col] = 'A'

    end_row, end_col = random.randint(0, m // 2) * 2, random.randint(0, n // 2) * 2
    maze[end_row][end_col] = 'B'

    return maze
def write_maze_to_file(maze, filename):
    with open(filename, 'w') as file:
        for row in maze:
            line = ' '.join(row) + '\n'
            file.write(line)
            
            
maze = generate_maze(10, 10)
write_maze_to_file(maze, "mazeGene.txt")
print(maze)

