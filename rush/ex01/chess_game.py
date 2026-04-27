#!/usr/bin/env python3
import time

# --- Global State ---
player_times = {'white': 600.0, 'black': 600.0}
last_update_time = None
current_turn = 'white'
game_active = True  # Added to control the background timer

def show_rules():
    print("""Welcome to chess...?
=====================================================
Rules   1. How Pieces Move
            Rook: moves Vertically and Horizontally
            Bishop: moves Diagonally
            Knight: moves in an 'L' shape (2x1)
            Queen: moves like a Rook + Bishop
            Pawn: moves forward, one square at a time
            Castling: O-O (Kingside) or O-O-O (Queenside)
          
        2. Pawn Promoting
            Once your pawn reaches the other side of the board
            you may promote to a Queen, Rook, Bishop, or Knight
        
        3. Checks
            Once your king is in check, you cannot move other pieces
            unless they block the check or move the king
          
        4. Draw Rules
            - 50 move rule: 50 moves without pawn move/capture
            - 3 fold repetition
            - Stalemate
            - Insufficient Material
=====================================================""")

board_size = 8
board = [
    ['♖','♘','♗','♕','♔','♗','♘','♖'], # Black
    ['♙','♙','♙','♙','♙','♙','♙','♙'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['♟','♟','♟','♟','♟','♟','♟','♟'],
    ['♜','♞','♝','♛','♚','♝','♞','♜']  # White
]

current_turn = 'white'
position_history = {}
halfmove_clock = 0 
moved_pieces = {
    'white_king': False, 'white_rook_a': False, 'white_rook_h': False,
    'black_king': False, 'black_rook_a': False, 'black_rook_h': False
}

def show_board():
    print("\n   a b c d e f g h")
    print("   ----------------")

    for i in range(board_size):
        row_string = " ".join(board[i])
        print(f"{8 - i}| {row_string}") 

    # Removed the line printing the 50-Move Clock
    print(f"\nTurn: {current_turn.capitalize()}")

    print(f"\nTurn: {current_turn.capitalize()} | 50-Move Clock: {halfmove_clock}/100")
def get_king_pos(color):
    target = '♚' if color == 'white' else '♔'

    for x in range(board_size):
        for y in range(board_size):
            if board[x][y] == target:
                return (x, y)

    return None

def find_check(x, y, color_of_king):
    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    knight_jumps = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
    is_white = color_of_king == 'white'
    e_rook, e_bishop, e_queen, e_pawn, e_knight = ('♖','♗','♕','♙','♘') if is_white else ('♜','♝','♛','♟','♞')

    for dx, dy in knight_jumps:
        nx, ny = x + dx, y + dy

        if 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == e_knight:
            return True
        
    for dx, dy in directions:
        i, j = x + dx, y + dy
        step = 1
        
        while 0 <= i < 8 and 0 <= j < 8:
            piece = board[i][j]

            if piece != '.':

                if (dx == 0 or dy == 0) and piece in (e_rook, e_queen):
                    return True
                
                if (dx != 0 and dy != 0) and piece in (e_bishop, e_queen):
                    return True
                
                if step == 1 and (dx != 0 and dy != 0):
                    pawn_dir = -1 if is_white else 1

                    if dx == pawn_dir and piece == e_pawn:
                        return True
                break

            i += dx; j += dy; step += 1
    return False

def in_check(color):
    pos = get_king_pos(color)
    return find_check(pos[0], pos[1], color) if pos else False

def can_castle(side):
    row = 7 if current_turn == 'white' else 0
    k_key = f"{current_turn}_king"
    r_key = f"{current_turn}_rook_h" if side == 'short' else f"{current_turn}_rook_a"

    if moved_pieces[k_key] or moved_pieces[r_key] or in_check(current_turn):
        return False
    
    cols = [5, 6] if side == 'short' else [1, 2, 3]
    for c in cols:
        if board[row][c] != '.':
            return False
        
    test_cols = [5, 6] if side == 'short' else [2, 3]
    for c in test_cols:
        if find_check(row, c, current_turn):
            return False
    return True

def valid_move(sr, sc, er, ec):
    if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
        return False
    
    piece, target = board[sr][sc], board[er][ec]
    white_p, black_p = {'♜','♞','♝','♛','♚','♟'}, {'♖','♘','♗','♕','♔','♙'}

    if piece == '.' or (current_turn == 'white' and piece not in white_p) or (current_turn == 'black' and piece not in black_p):
        return False
    
    if target != '.' and ((target in white_p) == (piece in white_p)):
        return False
    
    p_type = 'p' if piece in ('♟','♙') else 'r' if piece in ('♜','♖') else 'n' if piece in ('♞','♘') else 'b' if piece in ('♝','♗') else 'q' if piece in ('♛','♕') else 'k'
    dr, dc = er - sr, ec - sc

    if p_type == 'n':
        if not ((abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2)):
            return False
    elif p_type == 'r' and (dr != 0 and dc != 0): 
        return False
    elif p_type == 'b' and abs(dr) != abs(dc):
        return False
    elif p_type == 'q' and not (dr == 0 or dc == 0 or abs(dr) == abs(dc)):
        return False
    elif p_type == 'k' and (abs(dr) > 1 or abs(dc) > 1):
        return False
    elif p_type == 'p':
        move_dir = -1 if current_turn == 'white' else 1

        if dc == 0 and target == '.' and dr == move_dir:
            pass
        elif dc == 0 and target == '.' and dr == 2 * move_dir:
            if sr != (6 if current_turn == 'white' else 1) or board[sr+move_dir][sc] != '.':
                return False
        elif abs(dc) == 1 and dr == move_dir and target != '.':
            pass
        else:
            return False
        
    if p_type in ('r', 'b', 'q'):
        step_r, step_c = (0 if dr == 0 else (1 if dr > 0 else -1)), (0 if dc == 0 else (1 if dc > 0 else -1))
        cr, cc = sr + step_r, sc + step_c

        while (cr, cc) != (er, ec):
            if board[cr][cc] != '.':
                return False
            
            cr, cc = cr + step_r, cc + step_c

    orig_s, orig_e = board[sr][sc], board[er][ec]
    board[er][ec], board[sr][sc] = orig_s, '.'
    safe = not in_check(current_turn)
    board[sr][sc], board[er][ec] = orig_s, orig_e
    return safe

def get_all_valid_moves():
    moves = []
    for r in range(8):
        for c in range(8):
            for er in range(8):
                for ec in range(8):
                    if valid_move(r, c, er, ec): moves.append((r, c, er, ec))
    if can_castle('short'):
        moves.append('O-O')
    if can_castle('long'):
        moves.append('O-O-O')
    return moves

def is_checkmate(color):
    if not in_check(color): return False
    for r in range(8):
        for c in range(8):
            for er in range(8):
                for ec in range(8):
                    global current_turn
                    prev = current_turn
                    current_turn = color
                    if valid_move(r, c, er, ec):
                        current_turn = prev
                        return False
                    current_turn = prev
    return True

def is_insufficient_material():
    p_list = [board[r][c] for r in range(8) for c in range(8) if board[r][c] != '.']
    return len(p_list) <= 2

def record_position(): position_history[get_position()] = position_history.get(get_position(), 0) + 1

def get_position():
    return (tuple(tuple(r) for r in board), current_turn)

def check_repeat():
    return position_history.get(get_position(), 0) >= 3

def check_50_moves():
    return halfmove_clock >= 100

def update_clocks():
    global last_update_time
    
    # Get the current system time in seconds
    current_real_time = time.time()
    
    if last_update_time is None:
        last_update_time = current_real_time
        return

    # calculate how many seconds have passed since the last update
    elapsed = current_real_time - last_update_time
    # update last_update_time to the current time for the next calculation
    last_update_time = current_real_time
    
    # if the game is still running, subtract the elapsed time from 
    # the current player's remaining time
    if game_active:
        player_times[current_turn] -= elapsed
        # ensure the timer doesn't show negative numbers
        if player_times[current_turn] < 0:
            player_times[current_turn] = 0

def format_time(seconds):
    # convert total seconds into whole minutes
    mins = int(seconds // 60)
    # get the remaining seconds after minutes are removed
    secs = int(seconds % 60)
    # return a string padded with zeros (e.g., '05:09' instead of '5:9')
    return f"{mins:02d}:{secs:02d}"
