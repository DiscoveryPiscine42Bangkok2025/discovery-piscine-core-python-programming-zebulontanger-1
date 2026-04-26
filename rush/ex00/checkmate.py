#!/usr/bin/env python3

def checkmate(board: str):
    if not board or not board.strip():
        return

    grid = board.splitlines()
    grid_len = len(grid)
    
    if any(len(row) != grid_len for row in grid):
        print('error')
        return
    
    king_pos = None
    king_count = 0
    allowed_chars = {'K', 'P', 'B', 'Q', 'R', '.'}

    for r in range(grid_len):
        for c in range(grid_len):
            char = grid[r][c]
            
            if char not in allowed_chars:
                print('error')
                return
                
            if char == 'K':
                king_pos = (r, c)
                king_count += 1
    

    if king_count != 1:
        print('error')
        return

    kx, ky = king_pos
    
    directions = [
        (0, -1), (0, 1), (1, 0), (-1, 0),
        (1, 1), (-1, -1), (1, -1), (-1, 1)
    ]

    for dr, dc in directions:
        r, c = kx + dr, ky + dc
        while 0 <= r < grid_len and 0 <= c < grid_len:
            cell = grid[r][c]
            if cell != '.':
                if (dr == 0 or dc == 0) and cell in ('R', 'Q'):
                    print("Success")
                    return
                if (dr != 0 and dc != 0) and cell in ('B', 'Q'):
                    print("Success")
                    return
                break
            r += dr
            c += dc

    pawn_attackers = [(-1, -1), (-1, 1)] 
    for dr, dc in pawn_attackers:
        r, c = kx + dr, ky + dc
        if 0 <= r < grid_len and 0 <= c < grid_len:
            if grid[r][c] == 'P':
                print("Success")
                return

    print('Fail')
