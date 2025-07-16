import sys
import heapq
from collections import deque

MOVES = [(-1,0,'N'), (1,0,'S'), (0,1,'E'), (0,-1,'W')]

def parse_world_file(world_file):
    """
    Parses the input world file to create the grid, robot's start position, and dirty cells.
    Args: world_file (str)
    Returns: tuple: (grid, robot_pos, dirty_cells) 
    """
    with open(world_file) as f:
        content = [line.rstrip() for line in f.readlines()]

    rows = int(content[1])
    grid = []
    robot_pos = None
    dirty_cells = set()

    for row_idx in range(rows):
        row = list(content[row_idx + 2])
        grid.append(row)

        for col_idx, cell in enumerate(row):
            if cell == '@':
                robot_pos = (row_idx, col_idx)
            elif cell == '*':
                dirty_cells.add((row_idx, col_idx))

    return grid, robot_pos, dirty_cells

def print_results(path, nodes_generated, nodes_expanded):
    """
    Prints the path and search stats.
    Args: path (list), nodes_generated (int), nodes_expanded (int)
    Returns: N/A
    """
    if path:
        for action in path:
            print(action)
    else:
        print("No path found")

    print(f"{nodes_generated} nodes generated")
    print(f"{nodes_expanded} nodes expanded")

def get_neighbors(grid, pos):
    """
    Returns valid neighboring cells to move to while ignoring obstacles.
    Args: grid (list), pos (tuple)
    Returns: list: ((new_row, new_col), action)
    """
    neighbors = []
    x, y = pos
    for dx, dy, action in MOVES:
        new_x, new_y = x + dx, y + dy

        # checks for obstacles and makes sure it moves inside the grid 
        if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]) and grid[new_x][new_y] != '#':
            neighbors.append(((new_x, new_y), action))

    return neighbors

def dfs(grid, starting_pos, dirty_cells):
    """
    Depth-First Search algorithm to clean dirty cells.
    Args: grid (list), starting_pos (tuple), dirty_cells (set)
    Returns: tuple: (path, nodes_generated, nodes_expanded)
    """
    start_state = (starting_pos, frozenset(dirty_cells))
    stack = deque([(start_state, [])]) # (state, path) where path is the moves it made 
    visited = set([start_state])
    nodes_generated = 1
    nodes_expanded = 0
    
    while stack:
        (pos, remaining_dirt), path = stack.pop()
        nodes_expanded += 1
        
        # done cleaning 
        if not remaining_dirt:
            return path, nodes_generated, nodes_expanded
        
        # update dirty cells, robot position, and visited cells 
        if pos in remaining_dirt:
            new_dirty = remaining_dirt - {pos}
            new_state = (pos, new_dirty)

            if new_state not in visited:
                visited.add(new_state)
                stack.append((new_state, path + ['V']))
                nodes_generated += 1
                continue 
        
        # go through valid cells and test out potential paths
        for (new_x, new_y), action in get_neighbors(grid, pos):
            new_state = ((new_x, new_y), remaining_dirt)

            if new_state not in visited:
                visited.add(new_state)
                stack.append((new_state, path + [action]))
                nodes_generated += 1
    
    return None, nodes_generated, nodes_expanded

def ucs(grid, starting_pos, dirty_cells):
    start_state = (starting_pos, frozenset(dirty_cells))
    queue = [(0, start_state, [])] # (cost, state, path)
    visited = {}
    nodes_generated = 1
    nodes_expanded = 0

    while queue:
        cost, (pos, remaining_dirt), path = heapq.heappop(queue)

        if not remaining_dirt:
            return path, nodes_generated, nodes_expanded
        
        # check if it has been visited and that it is the cheapest path possible
        if (pos, remaining_dirt) in visited and visited[(pos, remaining_dirt)] <= cost:
            continue

        visited[(pos, remaining_dirt)] = cost
        nodes_expanded += 1

        # update dirty cells, robot position, and visited cells 
        if pos in remaining_dirt:
            new_dirt = remaining_dirt - {pos}
            new_state = (pos, new_dirt)
            heapq.heappush(queue, (cost + 1, new_state, path + ['V']))
            nodes_generated += 1

        # go through valid cells and test out potential paths
        for (new_x, new_y), action in get_neighbors(grid, pos):
            new_state = ((new_x, new_y), remaining_dirt)
            heapq.heappush(queue, (cost + 1, new_state, path + [action]))
            nodes_generated += 1

    return None, nodes_generated, nodes_expanded


def main():
    if len(sys.argv) != 3:
        print("Usage: python planner.py [algorithm] [world-file]")
        sys.exit(1)

    algorithm = sys.argv[1]
    world_file = sys.argv[2]
    grid, starting_pos, dirty_cells = parse_world_file(world_file)

    if algorithm == "depth-first":
        path, nodes_generated, nodes_expanded = dfs(grid, starting_pos, dirty_cells)
        print_results(path, nodes_generated, nodes_expanded)
    elif algorithm == "uniform-cost":
        path, nodes_generated, nodes_expanded = ucs(grid, starting_pos, dirty_cells)
        print_results(path, nodes_generated, nodes_expanded)
    else:
        print("Invalid algorithm. Only supports uniform-cost or depth-first")
        sys.exit(1)

if __name__ == "__main__":
    main()