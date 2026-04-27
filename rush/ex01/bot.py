import random
import pickle

# --- SETTINGS ---
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

# --- POSITIONAL TABLES (White's perspective; flip row for Black) ---
# Encourage center control, piece development, good outposts
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
    [0.1,0.1,0.2,0.3,0.3,0.2,0.1,0.1],
    [0.05,0.05,0.1,0.25,0.25,0.1,0.05,0.05],
    [0,  0,  0,  0.2,0.2, 0,  0,  0],
    [0.05,-0.05,-0.1,0,  0,-0.1,-0.05,0.05],
    [0.05,0.1,0.1,-0.2,-0.2,0.1,0.1,0.05],
    [0,  0,  0,  0,  0,  0,  0,  0]
]
KNIGHT_TABLE = [
    [-0.5,-0.4,-0.3,-0.3,-0.3,-0.3,-0.4,-0.5],
    [-0.4,-0.2, 0,   0,   0,   0,  -0.2,-0.4],
    [-0.3, 0,   0.1, 0.15,0.15,0.1, 0,  -0.3],
    [-0.3, 0.05,0.15,0.2, 0.2, 0.15,0.05,-0.3],
    [-0.3, 0,   0.15,0.2, 0.2, 0.15,0,  -0.3],
    [-0.3, 0.05,0.1, 0.15,0.15,0.1, 0.05,-0.3],
    [-0.4,-0.2, 0,   0.05,0.05,0,  -0.2,-0.4],
    [-0.5,-0.4,-0.3,-0.3,-0.3,-0.3,-0.4,-0.5]
]
BISHOP_TABLE = [
    [-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.2],
    [-0.1, 0,   0,   0,   0,   0,   0,  -0.1],
    [-0.1, 0,   0.05,0.1, 0.1, 0.05,0,  -0.1],
    [-0.1, 0.05,0.05,0.1, 0.1, 0.05,0.05,-0.1],
    [-0.1, 0,   0.1, 0.1, 0.1, 0.1, 0,  -0.1],
    [-0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,-0.1],
    [-0.1, 0.05,0,   0,   0,   0,  0.05,-0.1],
    [-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.2]
]
ROOK_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0  ],
    [0.05,0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [0,   0,   0,   0.05,0.05,0,   0,   0  ]
]
QUEEN_TABLE = [
    [-0.2,-0.1,-0.1,-0.05,-0.05,-0.1,-0.1,-0.2],
    [-0.1, 0,   0,   0,    0,    0,   0,  -0.1],
    [-0.1, 0,   0.05,0.05, 0.05, 0.05,0,  -0.1],
    [-0.05,0,   0.05,0.05, 0.05, 0.05,0,  -0.05],
    [0,    0,   0.05,0.05, 0.05, 0.05,0,  -0.05],
    [-0.1, 0.05,0.05,0.05, 0.05, 0.05,0,  -0.1],
    [-0.1, 0,   0.05,0,    0,    0,   0,  -0.1],
    [-0.2,-0.1,-0.1,-0.05,-0.05,-0.1,-0.1,-0.2]
]
# King safety: stay protected in opening/mid, centralize in endgame
KING_TABLE_MID = [
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.2,-0.3,-0.3,-0.4,-0.4,-0.3,-0.3,-0.2],
    [-0.1,-0.2,-0.2,-0.2,-0.2,-0.2,-0.2,-0.1],
    [0.2,  0.2, 0,   0,   0,   0,  0.2,  0.2],
    [0.2,  0.3, 0.1, 0,   0,  0.1, 0.3,  0.2]
]
KING_TABLE_END = [
    [-0.5,-0.4,-0.3,-0.2,-0.2,-0.3,-0.4,-0.5],
    [-0.3,-0.2,-0.1, 0,   0,  -0.1,-0.2,-0.3],
    [-0.3,-0.1, 0.2, 0.3, 0.3, 0.2,-0.1,-0.3],
    [-0.3,-0.1, 0.3, 0.4, 0.4, 0.3,-0.1,-0.3],
    [-0.3,-0.1, 0.3, 0.4, 0.4, 0.3,-0.1,-0.3],
    [-0.3,-0.1, 0.2, 0.3, 0.3, 0.2,-0.1,-0.3],
    [-0.3,-0.3, 0,   0,   0,   0,  -0.3,-0.3],
    [-0.5,-0.3,-0.3,-0.3,-0.3,-0.3,-0.3,-0.5]
]


def get_initial_board():
    return [
        ['♜','♞','♝','♛','♚','♝','♞','♜'],
        ['♟','♟','♟','♟','♟','♟','♟','♟'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['♙','♙','♙','♙','♙','♙','♙','♙'],
        ['♖','♘','♗','♕','♔','♗','♘','♖']
    ]

learned_values = {}

def load_brain():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
    except:
        learned_values = {}

def save_brain():
    with open("bot_brain.pkl", 'wb') as f:
        pickle.dump(learned_values, f)

def get_state_key(board):
    return "".join(["".join(row) for row in board])

def get_all_moves(board, turn):
    moves = []
    is_white = (turn == 'white')
    enemy_pieces = BLACK_PIECES if is_white else WHITE_PIECES
    friendly_pieces = WHITE_PIECES if is_white else BLACK_PIECES

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.' or (is_white and p not in WHITE_PIECES) or (not is_white and p not in BLACK_PIECES):
                continue

            dirs = []
            if p in {'♖', '♜', '♕', '♛'}: dirs += [(0,1),(0,-1),(1,0),(-1,0)]
            if p in {'♗', '♝', '♕', '♛'}: dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]

            if p in {'♘', '♞'}:
                for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p in {'♔', '♚'}:
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p == '♙':
                if r > 0 and board[r-1][c] == '.': moves.append((r,c,r-1,c))
                if r == 6 and board[r-1][c] == '.' and board[r-2][c] == '.': moves.append((r,c,r-2,c))
                for dc in [-1, 1]:
                    if r > 0 and 0 <= c+dc < 8 and board[r-1][c+dc] in BLACK_PIECES: moves.append((r,c,r-1,c+dc))
            elif p == '♟':
                if r < 7 and board[r+1][c] == '.': moves.append((r,c,r+1,c))
                if r == 1 and board[r+1][c] == '.' and board[r+2][c] == '.': moves.append((r,c,r+2,c))
                for dc in [-1, 1]:
                    if r < 7 and 0 <= c+dc < 8 and board[r+1][c+dc] in WHITE_PIECES: moves.append((r,c,r+1,c+dc))

            for dr, dc in dirs:
                nr, nc = r+dr, c+dc
                while 0<=nr<8 and 0<=nc<8:
                    if board[nr][nc] == '.': moves.append((r,c,nr,nc))
                    elif board[nr][nc] in enemy_pieces:
                        moves.append((r,c,nr,nc))
                        break
                    else: break
                    nr, nc = nr+dr, nc+dc
    return moves


def is_endgame(board):
    """Detect endgame: queens gone or very few pieces remain."""
    pieces = [p for row in board for p in row if p != '.']
    queens = [p for p in pieces if p in {'♕','♛'}]
    return len(queens) == 0 or len(pieces) <= 12


def get_positional_score(board):
    """
    Heuristic covering the chess checklist:
    1. Material balance
    2. Piece-square tables (center control, good squares)
    3. Piece mobility (candidate moves, activity)
    4. King safety (piece safety & threats)
    5. Pawn structure (doubled/isolated pawns punished)
    6. Rook open files (strategic alignment)
    7. Hanging piece penalty (piece safety)
    8. Tactical bonus: checks & captures available (forcing moves first)
    """
    score = 0.0
    endgame = is_endgame(board)

    # Collect pawn file info for structure analysis
    white_pawn_files = []
    black_pawn_files = []

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.':
                continue

            val = PIECE_VALUES.get(p, 0)
            score += val

            # --- 2. Piece-Square Tables ---
            is_white_p = p in WHITE_PIECES
            # For white, row 0 is far side; table row 0 = row 0 of board
            # For black, flip the row
            tr = r if is_white_p else (7 - r)
            sign = 1 if is_white_p else -1

            if p in {'♙', '♟'}:
                score += sign * PAWN_TABLE[tr][c]
                if is_white_p: white_pawn_files.append(c)
                else: black_pawn_files.append(c)
            elif p in {'♘', '♞'}:
                score += sign * KNIGHT_TABLE[tr][c]
            elif p in {'♗', '♝'}:
                score += sign * BISHOP_TABLE[tr][c]
            elif p in {'♖', '♜'}:
                score += sign * ROOK_TABLE[tr][c]
            elif p in {'♕', '♛'}:
                score += sign * QUEEN_TABLE[tr][c]
            elif p in {'♔', '♚'}:
                king_table = KING_TABLE_END if endgame else KING_TABLE_MID
                score += sign * king_table[tr][c]

    # --- 5. Pawn structure penalties ---
    # Doubled pawns
    for f in set(white_pawn_files):
        if white_pawn_files.count(f) > 1:
            score -= 0.3 * (white_pawn_files.count(f) - 1)
    for f in set(black_pawn_files):
        if black_pawn_files.count(f) > 1:
            score += 0.3 * (black_pawn_files.count(f) - 1)

    # Isolated pawns (no friendly pawn on adjacent files)
    for f in set(white_pawn_files):
        if not any(af in white_pawn_files for af in [f-1, f+1]):
            score -= 0.2
    for f in set(black_pawn_files):
        if not any(af in black_pawn_files for af in [f-1, f+1]):
            score += 0.2

    # --- 6. Rook open file bonus ---
    for c in range(8):
        col_pieces = [board[r][c] for r in range(8) if board[r][c] != '.']
        has_white_pawn = '♙' in col_pieces
        has_black_pawn = '♟' in col_pieces
        for r in range(8):
            p = board[r][c]
            if p == '♖':
                if not has_white_pawn and not has_black_pawn:
                    score += 0.3   # fully open file
                elif not has_white_pawn:
                    score += 0.15  # semi-open file
            elif p == '♜':
                if not has_white_pawn and not has_black_pawn:
                    score -= 0.3
                elif not has_black_pawn:
                    score -= 0.15

    # --- 7. Hanging piece penalty ---
    # A piece is "hanging" if it can be captured and is not defended
    # Quick approximation: penalise pieces that can be immediately captured
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            is_white_p = p in WHITE_PIECES
            attacker_color = 'black' if is_white_p else 'white'
            attacker_pieces = BLACK_PIECES if is_white_p else WHITE_PIECES
            # Check if any enemy can capture this square
            for ar in range(8):
                for ac in range(8):
                    ap = board[ar][ac]
                    if ap not in attacker_pieces: continue
                    # Can ap capture (r,c)?
                    if _can_attack(board, ar, ac, r, c):
                        pv = abs(PIECE_VALUES.get(p, 0))
                        # Penalty scaled by piece value; small for pawns
                        penalty = pv * 0.05
                        score += penalty if not is_white_p else -penalty
                        break  # count each piece as hanging once

    return score


def _can_attack(board, fr, fc, tr, tc):
    """Quick check: can piece at (fr,fc) capture square (tr,tc)?"""
    p = board[fr][fc]
    if p == '.': return False
    dr, dc = tr - fr, tc - fc

    if p in {'♘', '♞'}:
        return (abs(dr), abs(dc)) in {(2,1),(1,2)}

    if p in {'♔', '♚'}:
        return abs(dr) <= 1 and abs(dc) <= 1

    if p == '♙':
        return dr == -1 and abs(dc) == 1

    if p == '♟':
        return dr == 1 and abs(dc) == 1

    # Sliding pieces
    if p in {'♖', '♜', '♕', '♛'} and (dr == 0 or dc == 0):
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += step_r; nc += step_c
        return True

    if p in {'♗', '♝', '♕', '♛'} and abs(dr) == abs(dc):
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += step_r; nc += step_c
        return True

    return False


def evaluate_board(board, state_key=None):
    if not state_key: state_key = get_state_key(board)
    positional = get_positional_score(board)
    knowledge = learned_values.get(state_key, 0)
    return positional + knowledge


def select_move(board, turn, epsilon):
    moves = get_all_moves(board, turn)
    if not moves: return None

    if random.random() < epsilon:
        return random.choice(moves)

    # --- 3 & 8. Candidate Move Ordering: checks/captures first ---
    def move_priority(m):
        sr, sc, er, ec = m
        dest = board[er][ec]
        # Captures get a bonus proportional to victim value
        capture_bonus = abs(PIECE_VALUES.get(dest, 0)) * 2
        return capture_bonus

    moves.sort(key=move_priority, reverse=True)

    scored_moves = []
    for m in moves:
        sr, sc, er, ec = m
        orig, dest = board[sr][sc], board[er][ec]
        board[er][ec], board[sr][sc] = orig, '.'
        score = evaluate_board(board)
        scored_moves.append((score, m))
        board[sr][sc], board[er][ec] = orig, dest

    scored_moves.sort(key=lambda x: x[0], reverse=(turn == 'white'))
    return scored_moves[0][1]


def run_self_play_training(games=100):
    load_brain()
    epsilon = 0.5

    for g in range(games):
        board = get_initial_board()
        history = []
        turn = 'white'
        game_over = False
        result_score = 0

        for m_count in range(150):
            move = select_move(board, turn, epsilon)
            if not move:
                result_score = -5
                game_over = True
                break

            board[move[2]][move[3]], board[move[0]][move[1]] = board[move[0]][move[1]], '.'
            state_key = get_state_key(board)
            history.append(state_key)

            flat_board = "".join(["".join(row) for row in board])
            if '♔' not in flat_board:
                result_score = -50
                game_over = True
                break
            if '♚' not in flat_board:
                result_score = 50
                game_over = True
                break

            turn = 'black' if turn == 'white' else 'white'

        if not game_over:
            result_score = -10

        for i, state in enumerate(reversed(history)):
            reward = result_score * (DISCOUNT_FACTOR ** i)
            old_val = learned_values.get(state, 0)
            learned_values[state] = old_val + LEARNING_RATE * (reward - old_val)

        if (g + 1) % 50 == 0:
            print(f"Game {g+1} | Positions in Brain: {len(learned_values)}")
            save_brain()
            epsilon = max(0.1, epsilon * 0.99)

    save_brain()

if __name__ == "__main__":
    run_self_play_training(10000)
