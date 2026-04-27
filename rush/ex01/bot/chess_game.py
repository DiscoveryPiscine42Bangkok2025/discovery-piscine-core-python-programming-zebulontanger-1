import random
import pickle

board = [
    ['♜','♞','♝','♛','♚','♝','♞','♜'],
    ['♟','♟','♟','♟','♟','♟','♟','♟'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['♙','♙','♙','♙','♙','♙','♙','♙'],
    ['♖','♘','♗','♕','♔','♗','♘','♖'],
]

current_turn = 'white'
learned_values = {}
move_history = [] 
moved_pieces = set() 

WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}

def is_white_piece(p): return p in WHITE_PIECES
def is_black_piece(p): return p in BLACK_PIECES

def get_state_key():
    return "".join(["".join(row) for row in board])

def load_knowledge():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
    except: 
        learned_values = {}

def save_knowledge():
    with open("bot_brain.pkl", 'wb') as f:
        pickle.dump(learned_values, f)

def update_learning(history, result):
    # result: 1 for white win, 0 for black win, 0.5 for draw
    reward = 5 if result == 1 else -1 if result == 0 else 0
    for state in history:
        learned_values[state] = learned_values.get(state, 0) + (reward * 0.01)

def execute_move(sr, sc, er, ec, promotion_piece=None):
    piece = board[sr][sc]
    captured = board[er][ec]
    
    # 1. Castling Logic
    if piece in ('♔', '♚') and abs(sc - ec) == 2:
        rook_sc = 7 if ec == 6 else 0
        rook_ec = 5 if ec == 6 else 3
        board[sr][rook_ec] = board[sr][rook_sc]
        board[sr][rook_sc] = '.'

    # 2. En Passant Logic
    if piece in ('♙', '♟') and sc != ec and board[er][ec] == '.':
        board[sr][ec] = '.' # Remove captured pawn

    # 3. Move Piece
    move_history.append((sr, sc, er, ec, piece, captured))
    board[er][ec] = piece
    board[sr][sc] = '.'
    moved_pieces.add((sr, sc))

    # 4. Promotion
    if piece == '♙' and er == 0: board[er][ec] = promotion_piece or '♕'
    if piece == '♟' and er == 7: board[er][ec] = promotion_piece or '♛'

def get_all_valid_moves(color):
    moves = []
    for r in range(8):
        for c in range(8):
            if (color == 'white' and is_white_piece(board[r][c])) or \
               (color == 'black' and is_black_piece(board[r][c])):
                for er in range(8):
                    for ec in range(8):
                        if valid_move(r, c, er, ec, check_safety=True):
                            moves.append((r, c, er, ec))
    return moves

def valid_move(sr, sc, er, ec, check_safety=True):
    if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8): return False
    p = board[sr][sc]
    target = board[er][ec]
    if p == '.': return False
    if target != '.' and (is_white_piece(p) == is_white_piece(target)): return False

    dr, dc = er - sr, ec - sc
    dist_r, dist_c = abs(dr), abs(dc)
    
    if p in ('♙', '♟'):
        direction = -1 if is_white_piece(p) else 1
        start_rank = 6 if is_white_piece(p) else 1
        if dc == 0 and target == '.':
            if dr == direction: pass
            elif dr == 2 * direction and sr == start_rank and board[sr+direction][sc] == '.': pass
            else: return False
        elif dist_c == 1 and dr == direction:
            if target != '.': pass
            elif len(move_history) > 0:
                lsr, lsc, ler, lec, lp, lcap = move_history[-1]
                if lp in ('♙', '♟') and abs(lsr - ler) == 2 and ler == sr and lec == ec: pass
                else: return False
            else: return False
        else: return False
    elif p in ('♖', '♜'):
        if sr != er and sc != ec: return False
        if not path_clear(sr, sc, er, ec): return False
    elif p in ('♗', '♝'):
        if dist_r != dist_c: return False
        if not path_clear(sr, sc, er, ec): return False
    elif p in ('♕', '♛'):
        if not (sr == er or sc == ec or dist_r == dist_c): return False
        if not path_clear(sr, sc, er, ec): return False
    elif p in ('♘', '♞'):
        if not ((dist_r == 2 and dist_c == 1) or (dist_r == 1 and dist_c == 2)): return False
    elif p in ('♔', '♚'):
        if dist_r <= 1 and dist_c <= 1: pass
        elif dist_r == 0 and dist_c == 2 and check_safety:
            rook_c = 7 if ec == 6 else 0
            if (sr, sc) in moved_pieces or (sr, rook_c) in moved_pieces: return False
            if not path_clear(sr, sc, sr, rook_c): return False
            if in_check('white' if is_white_piece(p) else 'black'): return False
        else: return False

    if check_safety:
        orig_p, dest_p = board[sr][sc], board[er][ec]
        board[er][ec], board[sr][sc] = orig_p, '.'
        color = 'white' if is_white_piece(orig_p) else 'black'
        safe = not in_check(color)
        board[sr][sc], board[er][ec] = orig_p, dest_p
        return safe
    return True

def path_clear(sr, sc, er, ec):
    step_r = (er - sr) // max(1, abs(er - sr)) if er != sr else 0
    step_c = (ec - sc) // max(1, abs(ec - sc)) if ec != sc else 0
    curr_r, curr_c = sr + step_r, sc + step_c
    while (curr_r, curr_c) != (er, ec):
        if board[curr_r][curr_c] != '.': return False
        curr_r += step_r
        curr_c += step_c
    return True

def in_check(color):
    king_char = '♔' if color == 'white' else '♚'
    kr, kc = -1, -1
    for r in range(8):
        for c in range(8):
            if board[r][c] == king_char: kr, kc = r, c
    opponent_color = 'black' if color == 'white' else 'white'
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if (opponent_color == 'white' and is_white_piece(piece)) or \
               (opponent_color == 'black' and is_black_piece(piece)):
                if valid_move(r, c, kr, kc, check_safety=False): return True
    return False

def evaluate_board():
    vals = {'♙':1,'♘':3,'♗':3,'♖':5,'♕':9,'♔':100,'♟':-1,'♞':-3,'♝':-3,'♜':-5,'♛':-9,'♚':-100}
    score = sum(vals.get(board[r][c], 0) for r in range(8) for c in range(8))
    score += learned_values.get(get_state_key(), 0)
    return score

def minimax(depth, alpha, beta, is_maximizing):
    if depth == 0: return evaluate_board(), None
    color = 'black' if is_maximizing else 'white'
    moves = get_all_valid_moves(color)
    if not moves:
        if in_check(color): return (-1000 if is_maximizing else 1000), None
        return 0, None
    best_move = random.choice(moves)
    if is_maximizing:
        max_val = -9999
        for m in moves:
            orig, dest = board[m[0]][m[1]], board[m[2]][m[3]]
            board[m[2]][m[3]], board[m[0]][m[1]] = orig, '.'
            val, _ = minimax(depth-1, alpha, beta, False)
            board[m[0]][m[1]], board[m[2]][m[3]] = orig, dest
            if val > max_val: max_val, best_move = val, m
            alpha = max(alpha, val)
            if beta <= alpha: break
        return max_val, best_move
    else:
        min_val = 9999
        for m in moves:
            orig, dest = board[m[0]][m[1]], board[m[2]][m[3]]
            board[m[2]][m[3]], board[m[0]][m[1]] = orig, '.'
            val, _ = minimax(depth-1, alpha, beta, True)
            board[m[0]][m[1]], board[m[2]][m[3]] = orig, dest
            if val < min_val: min_val, best_move = val, m
            beta = min(beta, val)
            if beta <= alpha: break
        return min_val, best_move
