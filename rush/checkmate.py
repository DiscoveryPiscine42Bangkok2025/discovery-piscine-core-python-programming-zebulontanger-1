#!/usr/bin/env python3

def checkmate(board: str):

    grid = board.splitlines()
    grid_len = len(grid)
    if any(len(row) != grid_len for row in grid):
        print('error')
        return
        
    king_pos = None

    for i in range(grid_len):
        for j in range(grid_len):
            if grid[i][j] == 'K':
                king_pos = (i, j)
                break
        if king_pos:
            break
    if not king_pos:
        print('error')
        return

    x, y = king_pos

    direction = ([0, -1], [0, 1], [1, 0], [-1, 0], [1, 1], [-1, -1], [1, -1], [-1, 1])

    # rook check
    for dx, dy in direction:
            i, j = x + dx, y + dy
            while 0 <= i < grid_len and 0 <= j < grid_len:
                cell = grid[i][j]
                if cell != '.':
                    if (dx == 0 or dy == 0) and cell in ('R', 'Q'):
                        print("Success")
                        return
                    if (dx != 0 or dy != 0) and cell in ('B', 'Q'):
                        print('Success')
                        return
                    break
                
                i += dx
                j += dy

    pawn_direction = [(1, -1), (1, 1)]
    for dx, dy in pawn_direction:
        i, j = x + dx, y + dy
        if 0 <= i < grid_len and 0 <= j < grid_len:
            if grid[i][j] == 'P':
                print("Success")
                return

    print('fail')
