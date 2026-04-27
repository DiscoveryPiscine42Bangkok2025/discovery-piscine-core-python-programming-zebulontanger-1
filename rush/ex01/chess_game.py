#!/usr/bin/env python3

def show_rules():
    print("""Welcome to chess..kind of.
Due to budget cuts, we couldn't afford the horsies.
=====================================================
Rules   1. How Pieces Move
            Rook: moves Vertically and Horizontally
            Bishop: moves Diagonally
            Queen: moves like a Rook + Bishop
            Pawn: moves forward, one square at a time.
          
        2. Pawn Promoting
            Once your pawn reaches the other side of the board,
            you may promote to either a Rook or a Bishop
            (A queen is way too strong)
        
        3. Checks
            Once your king is in check, you cannot move other pieces,
            unless they block the check itself.
          
        4. How to Win
            If you can Checkmate, you win.
        
        5. Stalemate
            If either side has only a king left, or only one bishop,
            it is an immediate draw.
=====================================================""")


board_size = 8
board = [
    ['R','.','B','Q','K','B','.','R'],
    ['P','P','P','P','P','P','P','P'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['p','p','p','p','p','p','p','p'],
    ['r','.','b','q','k','b','.','r']
]
current_turn = 'white'
position_history = {}

has_moved = {
    'white_king': False, 'white_rook_a': False, 'white_rook_h': False,
    'black_king': False, 'black_rook_a': False, 'black_rook_h': False
}

def show_board():
    print("\n   a b c d e f g h")
    print("   ----------------")
    for i in range(board_size):
        row_string = ""
        for j in range(board_size):
            row_string += board[i][j] + " "
        print(f"{8 - i}| {row_string.strip()}") 
    print(f"\nTurn: {current_turn.capitalize()}\n")

def get_king_pos(color):
    target = 'k' if color == 'white' else 'K'
    for x in range(board_size):
        for y in range(board_size):
            if board[x][y] == target:
                return (x, y)
    return None

def find_check(x, y, color_of_king):
    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    enemy_rook = 'R' if color_of_king == 'white' else 'r'
    enemy_bishop = 'B' if color_of_king == 'white' else 'b'
    enemy_queen = 'Q' if color_of_king == 'white' else 'q'
    enemy_pawn = 'P' if color_of_king == 'white' else 'p'

    for dx, dy in directions:
        i, j = x + dx, y + dy
        step = 1

        while 0 <= i < board_size and 0 <= j < board_size:
            piece = board[i][j]

            if piece != '.':
                if (dx == 0 or dy == 0) and piece in (enemy_rook, enemy_queen):
                    return True
                if (dx != 0 or dy != 0) and piece in (enemy_bishop, enemy_queen):
                    return True
                if step == 1 and (dx != 0 and dy != 0):
                    pawn_direction = -1 if color_of_king == 'white' else 1
                    if dx == pawn_direction and piece == enemy_pawn:
                        return True
                
                break
            i += dx
            j += dy
            step += 1
    return False

def in_check(color):
    position = get_king_pos(color)
    if not position:
        return False
    return find_check(position[0], position[1], color)

def check_castle(start_row, start_col, end_row, end_col):
    piece = board[start_row][start_col]
    if piece.lower() != 'k':
        return False
    
    if abs(end_col - start_col) != 2 or start_row != end_row:
        return False

    if in_check(current_turn):
        return False

    is_white = current_turn == 'white'
    row = 7 if is_white else 0
    king_moved = has_moved['white_king'] if is_white else has_moved['black_king']
    
    if king_moved or start_row != row or start_col != 4:
        return False

    if end_col == 6:
        rook_moved = has_moved['white_rook_h'] if is_white else has_moved['black_rook_h']
        rook_piece = 'r' if is_white else 'R'
        if rook_moved or board[row][7] != rook_piece:
            return False
        path = [(row, 5), (row, 6)]
    elif end_col == 2:
        rook_moved = has_moved['white_rook_a'] if is_white else has_moved['black_rook_a']
        rook_piece = 'r' if is_white else 'R'
        if rook_moved or board[row][0] != rook_piece:
            return False
        path = [(row, 1), (row, 2), (row, 3)]
    else:
        return False

    for r, c in path:
        if board[r][c] != '.':
            return False
    
    test_path = [(row, 5), (row, 6)] if end_col == 6 else [(row, 3), (row, 2)]
    for r, c in test_path:
        original_king_pos = board[row][4]
        board[r][c] = original_king_pos
        board[row][4] = '.'
        if find_check(r, c, current_turn):
            board[row][4] = original_king_pos
            board[r][c] = '.'
            return False
        board[row][4] = original_king_pos
        board[r][c] = '.'

    return True

# def check_enpassant():

def valid_move(start_row, start_column, end_row, end_column):
    if not (0 <= start_row < board_size and 0 <= start_column < board_size and 
            0 <= end_row < board_size and 0 <= end_column < board_size):
        return False

    piece = board[start_row][start_column]
    target = board[end_row][end_column]

    if piece == '.':
        return False
    if current_turn == 'white' and not piece.islower():
        return False
    if current_turn == 'black' and not piece.isupper():
        return False
    
    if piece.lower() == 'k' and abs(end_column - start_column) == 2:
        return check_castle(start_row, start_column, end_row, end_column)

    if target != '.' and target.islower() == piece.islower():
        return False
    
    delta_row, delta_column = end_row - start_row, end_column - start_column
    piece_type = piece.lower()

    if piece_type == 'r' and (delta_row != 0 and delta_column != 0):
        return False
    elif piece_type == 'b' and abs(delta_row) != abs(delta_column):
        return False
    elif piece_type == 'q' and not (delta_row == 0 or delta_column == 0 or abs(delta_row) == abs(delta_column)):
        return False
    elif piece_type == 'k' and (abs(delta_row) > 1 or abs(delta_column) > 1):
        return False
    elif piece_type == 'p':
        direction = -1 if current_turn == 'white' else 1
        start_row_pawn = 6 if current_turn == 'white' else 1
        
        if delta_column == 0 and target == '.' and delta_row == direction:
            pass
        elif delta_column == 0 and target == '.' and delta_row == 2 * direction:
            if start_row != start_row_pawn:
                return False
            passing_row = start_row + direction
            if board[passing_row][start_column] != '.':
                return False
            pass
        elif abs(delta_column) == 1 and delta_row == direction and target != '.':
            pass
        else:
            return False
        
    if piece_type in ('r', 'b', 'q'):
        step_row = 0 if delta_row == 0 else (1 if delta_row > 0 else -1)
        step_column = 0 if delta_column == 0 else (1 if delta_column > 0 else -1)
        current_row, current_column = start_row + step_row, start_column + step_column
        while (current_row, current_column) != (end_row, end_column):
            if board[current_row][current_column] != '.':
                return False
            current_row += step_row
            current_column += step_column
    
    original_start = board[start_row][start_column]
    original_end = board[end_row][end_column]
    
    board[end_row][end_column] = original_start
    board[start_row][start_column] = '.'
    
    safe = not in_check(current_turn)
    
    board[start_row][start_column] = original_start
    board[end_row][end_column] = original_end

    return safe

def check_stalemate():
    if in_check(current_turn):
        return False
    
    for start_row in range(board_size):
        for start_column in range(board_size):
                piece = board[start_row][start_column]

                if piece == '.':
                    continue

                if current_turn == 'white' and not piece.islower():
                    continue
                if current_turn == 'black' and not piece.isupper():
                    continue
    
                for end_row in range(board_size):
                    for end_column in range(board_size):
                        if valid_move(start_row, start_column, end_row, end_column):
                            return False
    
    return True

def get_position():
    board_state = tuple(tuple(row) for row in board)
    return(board_state, current_turn)

def record_position():
    key = get_position()
    position_history[key] = position_history.get(key, 0) + 1

def check_repeat():
    key = get_position()
    return position_history.get(key, 0) >= 3
