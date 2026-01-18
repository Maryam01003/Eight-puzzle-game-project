from collections import deque
import copy
import random

GOAL_STATE = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def tuple_to_state(tup):
    return [list(row) for row in tup]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0: return i, j

def get_neighbors(state):
    i, j = find_zero(state)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_state = copy.deepcopy(state)
            new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
            neighbors.append((state_to_tuple(new_state), (ni, nj)))
    return neighbors

def solve_puzzle(start_state):
    start_tuple = state_to_tuple(start_state)
    goal_tuple = state_to_tuple(GOAL_STATE)
    if start_tuple == goal_tuple: return [start_state]
    queue = deque([(start_tuple, [start_tuple])])
    visited = {start_tuple}
    while queue:
        current, path = queue.popleft()
        if current == goal_tuple: return [tuple_to_state(s) for s in path]
        for next_state, _ in get_neighbors(tuple_to_state(current)):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [next_state]))
    return None

def scramble_state():
    state = copy.deepcopy(GOAL_STATE)
    moves = random.randint(20, 50)
    for _ in range(moves):
        neighbors = get_neighbors(state)
        if neighbors:
            next_state, _ = random.choice(neighbors)
            state = tuple_to_state(next_state)
    return state