#!/usr/bin/env python3

def checkmate(board: str):
    if not board or not board.strip():
        return

    grid = board.splitlines()
    size = len(grid)
    
    if any(len(row) != size for row in grid):
        return
    
    king_pos = None
    king_count = 0

    for r in range(size):
        for c in range(size):
            if grid[r][c] == 'K':
                king_pos = (r, c)
                king_count += 1
    
    if king_count != 1:
        return

    kx, ky = king_pos
    
    rays = [
        (0, -1), (0, 1), (1, 0), (-1, 0),
        (1, 1), (-1, -1), (1, -1), (-1, 1)
    ]

    for dr, dc in rays:
        r, c = kx + dr, ky + dc
        while 0 <= r < size and 0 <= c < size:
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

    pawn_threats = [(1, -1), (1, 1)] 
    for dr, dc in pawn_threats:
        r, c = kx + dr, ky + dc
        if 0 <= r < size and 0 <= c < size:
            if grid[r][c] == 'P':
                print("Success")
                return

    print("Fail")
