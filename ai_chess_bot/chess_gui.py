"""
chess_gui.py — Pygame GUI for the Chess Bot
============================================
Requirements:
    pip install pygame

Usage:
    python chess_gui.py

Make sure bot_brain.pkl is in the same folder (or it starts fresh).
"""

import sys
import os
import threading
import random
import pickle

# ── Try importing pygame ──────────────────────────────────────────────────────
try:
    import pygame
except ImportError:
    print("pygame not found. Install it with:  pip install pygame")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
#  All bot logic (copied verbatim from bot.py so this file is self-contained)
# ─────────────────────────────────────────────────────────────────────────────

LEARNING_RATE   = 0.1
DISCOUNT_FACTOR = 0.95
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

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

_PAWN_TABLE_T   = tuple(tuple(r) for r in PAWN_TABLE)
_KNIGHT_TABLE_T = tuple(tuple(r) for r in KNIGHT_TABLE)
_BISHOP_TABLE_T = tuple(tuple(r) for r in BISHOP_TABLE)
_ROOK_TABLE_T   = tuple(tuple(r) for r in ROOK_TABLE)
_QUEEN_TABLE_T  = tuple(tuple(r) for r in QUEEN_TABLE)
_KING_MID_T     = tuple(tuple(r) for r in KING_TABLE_MID)
_KING_END_T     = tuple(tuple(r) for r in KING_TABLE_END)

_KNIGHT_MOVES = ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
_KING_MOVES   = ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1))
_ROOK_DIRS    = ((0,1),(0,-1),(1,0),(-1,0))
_BISHOP_DIRS  = ((1,1),(1,-1),(-1,1),(-1,-1))
_QUEEN_DIRS   = _ROOK_DIRS + _BISHOP_DIRS

OPENING_BOOK = {
    (): ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"],
    ("e2e4",): ["e7e5", "c7c5", "e7e6", "c7c6", "d7d5", "g8f6", "d7d6", "g7g6"],
    ("e2e4","e7e5"): ["g1f3"],
    ("e2e4","e7e5","g1f3"): ["b8c6"],
    ("e2e4","e7e5","g1f3","b8c6"): ["f1b5"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5"): ["a7a6","g8f6","f8c5","d7d6","b7b5"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6"): ["b5a4","b5c6"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6","b5a4"): ["g8f6","d7d6"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6","b5a4","g8f6"): ["e1g1"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4"): ["f8c5","g8f6","f7f5"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5"): ["c2c3","b2b4","d2d3"],
    ("e2e4","e7e5","g1f3","b8c6","d2d4"): ["e5d4"],
    ("e2e4","e7e5","g1f3","b8c6","d2d4","e5d4"): ["f3d4"],
    ("e2e4","e7e5","f2f4"): ["e5f4","f8c5","d7d5"],
    ("e2e4","c7c5"): ["g1f3","b1c3","c2c3"],
    ("e2e4","c7c5","g1f3"): ["b8c6","d7d6","e7e6","g7g6","a7a6"],
    ("e2e4","c7c5","g1f3","d7d6"): ["d2d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4"): ["c5d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4"): ["f3d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4"): ["g8f6"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6"): ["b1c3"],
    ("e2e4","e7e6"): ["d2d4","b1c3"],
    ("e2e4","e7e6","d2d4"): ["d7d5"],
    ("e2e4","e7e6","d2d4","d7d5"): ["b1c3","b1d2","e4e5","e4d5"],
    ("e2e4","c7c6"): ["d2d4","b1c3"],
    ("e2e4","c7c6","d2d4"): ["d7d5"],
    ("e2e4","c7c6","d2d4","d7d5"): ["b1c3","b1d2","e4e5","e4d5"],
    ("e2e4","d7d5"): ["e4d5"],
    ("e2e4","d7d5","e4d5"): ["d8d5","g8f6"],
    ("e2e4","d7d5","e4d5","d8d5"): ["b1c3"],
    ("d2d4",): ["d7d5","g8f6","f7f5","e7e6","c7c5","g7g6","b8c6","d7d6"],
    ("d2d4","d7d5"): ["c2c4","g1f3","c2c3"],
    ("d2d4","d7d5","c2c4"): ["e7e6","c7c6","d5c4","b8c6","e7e5","g8f6"],
    ("d2d4","d7d5","c2c4","e7e6"): ["b1c3","g1f3"],
    ("d2d4","d7d5","c2c4","e7e6","b1c3"): ["g8f6","c7c6","f8e7"],
    ("d2d4","d7d5","c2c4","c7c6"): ["g1f3","b1c3","e2e3"],
    ("d2d4","g8f6"): ["c2c4","g1f3","b1c3"],
    ("d2d4","g8f6","c2c4"): ["g7g6","e7e6","c7c5","d7d6"],
    ("d2d4","g8f6","c2c4","g7g6"): ["b1c3","g1f3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3"): ["f8g7"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7"): ["e2e4","g1f3"],
    ("d2d4","g8f6","c2c4","e7e6"): ["b1c3","g1f3"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3"): ["f8b4"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4"): ["e2e3","d1c2","a2a3","g1f3","f2f3"],
    ("c2c4",): ["e7e5","c7c5","g8f6","e7e6","d7d5","g7g6","f7f5"],
    ("c2c4","e7e5"): ["b1c3","g1f3","g2g3"],
    ("c2c4","e7e5","b1c3"): ["g8f6","b8c6","f8c5","d7d6"],
    ("c2c4","g8f6"): ["b1c3","g1f3","g2g3","d2d4"],
    ("c2c4","d7d5"): ["b1c3","g1f3","c4d5"],
    ("g1f3",): ["d7d5","g8f6","c7c5","e7e6","g7g6","f7f5","b8c6"],
    ("g1f3","d7d5"): ["c2c4","g2g3","d2d4","b2b3"],
    ("g1f3","g8f6"): ["c2c4","g2g3","d2d4","b2b3"],
}


def lookup_opening(move_history, bot_color='white'):
    key = tuple(move_history)
    whose_turn = 'white' if len(key) % 2 == 0 else 'black'
    if whose_turn != bot_color:
        return None
    candidates = OPENING_BOOK.get(key)
    if candidates:
        return random.choice(candidates)
    return None


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
_transposition_table = {}


def clear_transposition_table():
    global _transposition_table
    _transposition_table = {}


def load_brain():
    global learned_values
    brain_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_brain.pkl")
    try:
        with open(brain_path, 'rb') as f:
            learned_values = pickle.load(f)
        print(f"Brain loaded: {len(learned_values)} positions")
    except Exception:
        learned_values = {}
        print("No brain file found, starting fresh.")


def get_state_key(board):
    return "".join(["".join(row) for row in board])


def get_all_moves(board, turn):
    moves = []
    is_white = (turn == 'white')
    enemy_pieces   = BLACK_PIECES if is_white else WHITE_PIECES
    friendly_pieces = WHITE_PIECES if is_white else BLACK_PIECES

    for r in range(8):
        row = board[r]
        for c in range(8):
            p = row[c]
            if p == '.': continue
            if is_white  and p not in WHITE_PIECES: continue
            if not is_white and p not in BLACK_PIECES: continue

            if p in ('♘','♞'):
                for dr,dc in _KNIGHT_MOVES:
                    nr,nc = r+dr,c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p in ('♔','♚'):
                for dr,dc in _KING_MOVES:
                    nr,nc = r+dr,c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p == '♙':
                if r > 0:
                    if board[r-1][c] == '.':
                        moves.append((r,c,r-1,c))
                        if r==6 and board[r-2][c]=='.':
                            moves.append((r,c,r-2,c))
                    for dc in (-1,1):
                        nc = c+dc
                        if 0<=nc<8 and board[r-1][nc] in BLACK_PIECES:
                            moves.append((r,c,r-1,nc))
            elif p == '♟':
                if r < 7:
                    if board[r+1][c] == '.':
                        moves.append((r,c,r+1,c))
                        if r==1 and board[r+2][c]=='.':
                            moves.append((r,c,r+2,c))
                    for dc in (-1,1):
                        nc = c+dc
                        if 0<=nc<8 and board[r+1][nc] in WHITE_PIECES:
                            moves.append((r,c,r+1,nc))
            else:
                if p in ('♖','♜'):    dirs = _ROOK_DIRS
                elif p in ('♗','♝'): dirs = _BISHOP_DIRS
                else:                 dirs = _QUEEN_DIRS
                for dr,dc in dirs:
                    nr,nc = r+dr,c+dc
                    while 0<=nr<8 and 0<=nc<8:
                        target = board[nr][nc]
                        if target == '.':
                            moves.append((r,c,nr,nc))
                        elif target in enemy_pieces:
                            moves.append((r,c,nr,nc)); break
                        else:
                            break
                        nr+=dr; nc+=dc
    return moves


def is_in_check(board, color):
    """Return True if the given color's king is under attack."""
    king = '♔' if color == 'white' else '♚'
    kr, kc = -1, -1
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                kr, kc = r, c
                break
    if kr == -1:
        return False
    enemy_turn = 'black' if color == 'white' else 'white'
    for move in get_all_moves(board, enemy_turn):
        if move[2] == kr and move[3] == kc:
            return True
    return False


def get_legal_moves(board, turn):
    """Filter pseudo-legal moves to only those that don't leave own king in check."""
    pseudo = get_all_moves(board, turn)
    legal = []
    for sr, sc, er, ec in pseudo:
        orig, dest = board[sr][sc], board[er][ec]
        board[er][ec] = orig
        board[sr][sc] = '.'
        # Pawn promotion: auto-queen
        if orig == '♙' and er == 0:
            board[er][ec] = '♕'
        elif orig == '♟' and er == 7:
            board[er][ec] = '♛'
        in_check = is_in_check(board, turn)
        board[sr][sc] = orig
        board[er][ec] = dest
        if not in_check:
            legal.append((sr, sc, er, ec))
    return legal


def is_endgame(board):
    piece_count = 0
    has_queen = False
    for row in board:
        for p in row:
            if p != '.':
                piece_count += 1
                if p in ('♕','♛'):
                    has_queen = True
    return (not has_queen) or piece_count <= 12


def get_positional_score(board, endgame=None):
    score = 0.0
    if endgame is None:
        endgame = is_endgame(board)
    white_pawn_files, black_pawn_files = [], []
    for r in range(8):
        row = board[r]
        for c in range(8):
            p = row[c]
            if p == '.': continue
            score += PIECE_VALUES.get(p, 0)
            is_white_p = p in WHITE_PIECES
            tr   = r if is_white_p else (7-r)
            sign = 1 if is_white_p else -1
            if p in ('♙','♟'):
                score += sign * _PAWN_TABLE_T[tr][c]
                (white_pawn_files if is_white_p else black_pawn_files).append(c)
            elif p in ('♘','♞'):  score += sign * _KNIGHT_TABLE_T[tr][c]
            elif p in ('♗','♝'):  score += sign * _BISHOP_TABLE_T[tr][c]
            elif p in ('♖','♜'):  score += sign * _ROOK_TABLE_T[tr][c]
            elif p in ('♕','♛'):  score += sign * _QUEEN_TABLE_T[tr][c]
            elif p in ('♔','♚'):
                kt = _KING_END_T if endgame else _KING_MID_T
                score += sign * kt[tr][c]
    return score


def evaluate_board(board, state_key=None):
    if not state_key:
        state_key = get_state_key(board)
    positional = get_positional_score(board)
    knowledge  = learned_values.get(state_key, 0)
    return positional + knowledge


def _minimax(board, depth, alpha, beta, maximizing):
    flat = get_state_key(board)
    if '♔' not in flat: return -500.0
    if '♚' not in flat: return  500.0
    if depth == 0:       return evaluate_board(board, flat)

    tt_key   = (flat, depth, maximizing)
    tt_entry = _transposition_table.get(tt_key)
    if tt_entry:
        flag, val = tt_entry
        if flag == 'exact':          return val
        if flag == 'lower' and val >= beta:  return val
        if flag == 'upper' and val <= alpha: return val

    turn  = 'white' if maximizing else 'black'
    moves = get_all_moves(board, turn)
    if not moves: return evaluate_board(board, flat)

    moves.sort(key=lambda m: abs(PIECE_VALUES.get(board[m[2]][m[3]], 0)), reverse=True)
    orig_alpha = alpha

    if maximizing:
        best = -9999.0
        for sr,sc,er,ec in moves:
            orig,dest = board[sr][sc], board[er][ec]
            board[er][ec]=orig; board[sr][sc]='.'
            val = _minimax(board, depth-1, alpha, beta, False)
            board[sr][sc]=orig; board[er][ec]=dest
            if val > best: best = val
            if best > alpha: alpha = best
            if alpha >= beta: break
        flag = 'exact' if best > orig_alpha else 'upper'
        _transposition_table[tt_key] = (flag, best)
        return best
    else:
        best = 9999.0; orig_beta = beta
        for sr,sc,er,ec in moves:
            orig,dest = board[sr][sc], board[er][ec]
            board[er][ec]=orig; board[sr][sc]='.'
            val = _minimax(board, depth-1, alpha, beta, True)
            board[sr][sc]=orig; board[er][ec]=dest
            if val < best: best = val
            if best < beta: beta = best
            if alpha >= beta: break
        flag = 'exact' if best < orig_beta else 'lower'
        _transposition_table[tt_key] = (flag, best)
        return best


def bot_pick_move(board, turn, search_depth, epsilon, move_history, bot_color):
    """Full bot move selection with opening book, legal filtering, and minimax."""
    # Opening book
    book_str = lookup_opening(move_history, bot_color)

    legal = get_legal_moves(board, turn)
    if not legal:
        return None

    # Try book move if legal
    if book_str:
        try:
            fc = ord(book_str[0])-ord('a')
            fr = 8-int(book_str[1])
            tc = ord(book_str[2])-ord('a')
            tr = 8-int(book_str[3])
            book_tuple = (fr,fc,tr,tc)
            if book_tuple in legal:
                return book_tuple
        except Exception:
            pass

    if random.random() < epsilon:
        return random.choice(legal)

    maximizing = (turn == 'white')
    best_move  = None
    best_score = -9999.0 if maximizing else 9999.0
    alpha, beta = -9999.0, 9999.0

    legal_sorted = sorted(legal, key=lambda m: abs(PIECE_VALUES.get(board[m[2]][m[3]], 0)), reverse=True)

    for sr,sc,er,ec in legal_sorted:
        orig,dest = board[sr][sc], board[er][ec]
        board[er][ec]=orig; board[sr][sc]='.'
        val = _minimax(board, search_depth, alpha, beta, not maximizing)
        board[sr][sc]=orig; board[er][ec]=dest
        if maximizing:
            if val > best_score:
                best_score = val; best_move = (sr,sc,er,ec)
            alpha = max(alpha, best_score)
        else:
            if val < best_score:
                best_score = val; best_move = (sr,sc,er,ec)
            beta = min(beta, best_score)

    return best_move or random.choice(legal)


def format_move(move):
    fr,fc,tr,tc = move
    return f"{chr(ord('a')+fc)}{8-fr}{chr(ord('a')+tc)}{8-tr}"


# ─────────────────────────────────────────────────────────────────────────────
#  Pygame GUI
# ─────────────────────────────────────────────────────────────────────────────

# Colours
C_LIGHT      = (240, 217, 181)
C_DARK       = (181, 136,  99)
C_SELECTED   = (100, 200, 100, 160)
C_LEGAL      = ( 50, 150, 255, 100)
C_CHECK      = (220,  60,  60, 180)
C_LAST_MOVE  = (180, 220, 100, 120)
C_BG         = ( 30,  30,  30)
C_PANEL_BG   = ( 45,  45,  45)
C_TEXT       = (240, 240, 240)
C_TEXT_DIM   = (160, 160, 160)
C_BTN        = ( 70,  70,  70)
C_BTN_HOV    = ( 95,  95,  95)
C_BTN_ACT    = ( 50, 130, 200)
C_WHITE_PIE  = (255, 255, 255)
C_BLACK_PIE  = ( 20,  20,  20)
C_PROMO_BG   = ( 50,  50,  50, 220)

PIECE_UNICODE = {
    '♙':'♙','♖':'♖','♘':'♘','♗':'♗','♕':'♕','♔':'♔',
    '♟':'♟','♜':'♜','♞':'♞','♝':'♝','♛':'♛','♚':'♚',
}

SQUARE  = 80          # px per square
BOARD_W = SQUARE * 8
BOARD_H = SQUARE * 8
PANEL_W = 260
WIN_W   = BOARD_W + PANEL_W
WIN_H   = BOARD_H
BOARD_X = 0
BOARD_Y = 0


class ChessGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess Bot")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock  = pygame.time.Clock()

        # Try to load a unicode-capable font
        self.piece_font = None
        candidates = [
            "seguisym.ttf","NotoChess.ttf",
            "DejaVuSans.ttf","FreeSerif.ttf",
        ]
        for name in candidates:
            try:
                f = pygame.font.Font(name, int(SQUARE*0.78))
                self.piece_font = f
                break
            except Exception:
                pass
        if self.piece_font is None:
            # Fallback: system font that usually has chess symbols on Linux/Mac
            for sysname in ["segoeuisymbol","symbola","freesans","dejavusans","notosans"]:
                try:
                    f = pygame.font.SysFont(sysname, int(SQUARE*0.78))
                    self.piece_font = f
                    break
                except Exception:
                    pass
        if self.piece_font is None:
            self.piece_font = pygame.font.Font(None, int(SQUARE*0.78))

        self.label_font  = pygame.font.SysFont("Arial", 14)
        self.ui_font     = pygame.font.SysFont("Arial", 16)
        self.big_font    = pygame.font.SysFont("Arial", 20, bold=True)
        self.small_font  = pygame.font.SysFont("Arial", 13)

        load_brain()
        self._init_state()

    # ── State ────────────────────────────────────────────────────────────────

    def _init_state(self):
        self.state = "menu"   # menu | game | promo | gameover
        self.board = get_initial_board()
        self.turn  = 'white'

        self.human_color = 'white'
        self.bot_color   = 'black'
        self.difficulty  = 2          # 1/2/3
        self.search_depth_map = {1:1, 2:2, 3:3}
        self.epsilon_map      = {1:0.30, 2:0.05, 3:0.00}

        self.selected    = None       # (r,c) of selected piece
        self.legal_moves = []         # legal moves for selected piece
        self.last_move   = None       # (sr,sc,er,ec)
        self.move_history_str  = []   # for opening book ("e2e4" strings)
        self.move_history_log  = []   # display log
        self.in_check    = False
        self.game_result = None       # None | "white" | "black" | "draw"
        self.status_msg  = ""

        self.bot_thinking = False
        self.bot_result   = None      # filled by thread

        # Pawn promotion
        self.promo_pending = None     # (sr,sc,er,ec) awaiting choice
        self.promo_color   = None

        # Menu state
        self.menu_human   = 'white'
        self.menu_diff    = 2

        clear_transposition_table()

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.clock.tick(60)
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.state == "menu":
                    self._handle_menu_event(ev)
                elif self.state == "game":
                    self._handle_game_event(ev)
                elif self.state == "promo":
                    self._handle_promo_event(ev)
                elif self.state == "gameover":
                    self._handle_gameover_event(ev)

            # Check for bot thread result
            if self.state == "game" and self.bot_thinking and self.bot_result is not None:
                self._apply_bot_move(self.bot_result)
                self.bot_result   = None
                self.bot_thinking = False

            if self.state == "menu":
                self._draw_menu()
            elif self.state in ("game","promo"):
                self._draw_game()
                if self.state == "promo":
                    self._draw_promo_overlay()
            elif self.state == "gameover":
                self._draw_game()
                self._draw_gameover_overlay()

            pygame.display.flip()

    # ── Menu ─────────────────────────────────────────────────────────────────

    def _menu_buttons(self):
        cx = WIN_W // 2
        return {
            "white_btn": pygame.Rect(cx-130, 200, 120, 44),
            "black_btn": pygame.Rect(cx+10,  200, 120, 44),
            "d1_btn":    pygame.Rect(cx-180, 300, 100, 44),
            "d2_btn":    pygame.Rect(cx-55,  300, 100, 44),
            "d3_btn":    pygame.Rect(cx+70,  300, 100, 44),
            "start_btn": pygame.Rect(cx-100, 400, 200, 54),
        }

    def _handle_menu_event(self, ev):
        if ev.type != pygame.MOUSEBUTTONDOWN: return
        btns = self._menu_buttons()
        mx,my = ev.pos
        if btns["white_btn"].collidepoint(mx,my): self.menu_human = 'white'
        if btns["black_btn"].collidepoint(mx,my): self.menu_human = 'black'
        if btns["d1_btn"].collidepoint(mx,my):    self.menu_diff  = 1
        if btns["d2_btn"].collidepoint(mx,my):    self.menu_diff  = 2
        if btns["d3_btn"].collidepoint(mx,my):    self.menu_diff  = 3
        if btns["start_btn"].collidepoint(mx,my):
            self._start_game()

    def _start_game(self):
        self._init_state()
        self.human_color  = self.menu_human
        self.bot_color    = 'black' if self.human_color == 'white' else 'white'
        self.difficulty   = self.menu_diff
        self.state        = "game"
        # If bot goes first (human is black)
        if self.turn != self.human_color:
            self._trigger_bot_move()

    def _draw_menu(self):
        s = self.screen
        s.fill(C_BG)
        cx = WIN_W // 2

        # Title
        t = self.big_font.render("♟  CHESS BOT  ♙", True, C_TEXT)
        s.blit(t, (cx - t.get_width()//2, 80))
        t2 = self.ui_font.render("Select your settings and press Start", True, C_TEXT_DIM)
        s.blit(t2, (cx - t2.get_width()//2, 130))

        btns = self._menu_buttons()
        mx,my = pygame.mouse.get_pos()

        # Color choice
        lbl = self.ui_font.render("Play as:", True, C_TEXT)
        s.blit(lbl, (cx - lbl.get_width()//2, 168))
        for key, label, chosen_val in [("white_btn","White",'white'),("black_btn","Black",'black')]:
            r = btns[key]
            active = self.menu_human == chosen_val
            col = C_BTN_ACT if active else (C_BTN_HOV if r.collidepoint(mx,my) else C_BTN)
            pygame.draw.rect(s, col, r, border_radius=8)
            t = self.ui_font.render(label, True, C_TEXT)
            s.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))

        # Difficulty
        lbl = self.ui_font.render("Difficulty:", True, C_TEXT)
        s.blit(lbl, (cx - lbl.get_width()//2, 268))
        for key, label, dval in [("d1_btn","Easy",1),("d2_btn","Medium",2),("d3_btn","Hard",3)]:
            r = btns[key]
            active = self.menu_diff == dval
            col = C_BTN_ACT if active else (C_BTN_HOV if r.collidepoint(mx,my) else C_BTN)
            pygame.draw.rect(s, col, r, border_radius=8)
            t = self.ui_font.render(label, True, C_TEXT)
            s.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))

        # Depth info
        depth_info = {1:"(depth 1, random 30%)",2:"(depth 2, minimax)",3:"(depth 3, full power)"}
        di = self.small_font.render(depth_info[self.menu_diff], True, C_TEXT_DIM)
        s.blit(di, (cx - di.get_width()//2, 356))

        # Start button
        r = btns["start_btn"]
        col = C_BTN_HOV if r.collidepoint(mx,my) else C_BTN_ACT
        pygame.draw.rect(s, col, r, border_radius=10)
        t = self.big_font.render("Start Game", True, C_TEXT)
        s.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))

    # ── Game event handling ───────────────────────────────────────────────────

    def _handle_game_event(self, ev):
        if ev.type != pygame.MOUSEBUTTONDOWN: return
        mx,my = ev.pos
        # Restart button
        rb = self._restart_btn()
        if rb.collidepoint(mx,my):
            self.state = "menu"; return

        if self.bot_thinking: return
        if self.game_result:  return
        if self.turn != self.human_color: return

        # Board click
        if BOARD_X <= mx < BOARD_X+BOARD_W and BOARD_Y <= my < BOARD_Y+BOARD_H:
            c = (mx - BOARD_X) // SQUARE
            r = (my - BOARD_Y) // SQUARE
            if self.human_color == 'black':
                r = 7 - r; c = 7 - c
            self._handle_board_click(r, c)

    def _handle_board_click(self, r, c):
        piece = self.board[r][c]
        my_pieces = WHITE_PIECES if self.human_color == 'white' else BLACK_PIECES

        if self.selected:
            sr, sc = self.selected
            move = (sr, sc, r, c)
            legal = get_legal_moves(self.board, self.turn)
            if move in legal:
                # Check for pawn promotion
                p = self.board[sr][sc]
                if (p == '♙' and r == 0) or (p == '♟' and r == 7):
                    self.promo_pending = move
                    self.promo_color   = 'white' if p == '♙' else 'black'
                    self.state = "promo"
                else:
                    self._apply_human_move(move)
                self.selected    = None
                self.legal_moves = []
                return
            # Clicked own piece: reselect
            if piece in my_pieces:
                self.selected    = (r, c)
                self.legal_moves = [m for m in get_legal_moves(self.board, self.turn) if m[0]==r and m[1]==c]
                return
            self.selected    = None
            self.legal_moves = []
        else:
            if piece in my_pieces:
                self.selected    = (r, c)
                self.legal_moves = [m for m in get_legal_moves(self.board, self.turn) if m[0]==r and m[1]==c]

    def _apply_human_move(self, move, promo_piece=None):
        sr,sc,er,ec = move
        p = self.board[sr][sc]
        self.board[er][ec] = promo_piece if promo_piece else p
        self.board[sr][sc] = '.'
        self.last_move      = move
        self.move_history_str.append(format_move(move))
        self.move_history_log.append(format_move(move))
        self.turn = 'black' if self.turn == 'white' else 'white'
        self._check_game_over()
        if self.game_result is None:
            self._trigger_bot_move()

    def _trigger_bot_move(self):
        if self.game_result: return
        self.bot_thinking = True
        board_copy = [row[:] for row in self.board]
        depth      = self.search_depth_map[self.difficulty]
        eps        = self.epsilon_map[self.difficulty]
        turn       = self.turn
        hist       = list(self.move_history_str)
        bot_col    = self.bot_color

        def worker():
            clear_transposition_table()
            result = bot_pick_move(board_copy, turn, depth, eps, hist, bot_col)
            self.bot_result = result

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _apply_bot_move(self, move):
        if not move:
            self._check_game_over(); return
        sr,sc,er,ec = move
        p = self.board[sr][sc]
        # Auto-promote to queen
        promo = None
        if p == '♙' and er == 0: promo = '♕'
        if p == '♟' and er == 7: promo = '♛'
        self.board[er][ec] = promo if promo else p
        self.board[sr][sc] = '.'
        self.last_move      = move
        ms = format_move(move)
        self.move_history_str.append(ms)
        self.move_history_log.append(f"Bot: {ms}")
        self.turn = 'black' if self.turn == 'white' else 'white'
        self._check_game_over()

    def _check_game_over(self):
        flat = get_state_key(self.board)
        if '♔' not in flat:
            self.game_result = 'black'; self.state = "gameover"
            self.status_msg  = "Black wins! White king captured."
            return
        if '♚' not in flat:
            self.game_result = 'white'; self.state = "gameover"
            self.status_msg  = "White wins! Black king captured."
            return
        legal = get_legal_moves(self.board, self.turn)
        if not legal:
            if is_in_check(self.board, self.turn):
                winner = 'black' if self.turn == 'white' else 'white'
                self.game_result = winner
                self.status_msg  = f"Checkmate! {winner.capitalize()} wins."
            else:
                self.game_result = 'draw'
                self.status_msg  = "Stalemate! It's a draw."
            self.state = "gameover"
            return
        self.in_check = is_in_check(self.board, self.turn)

    # ── Promo ────────────────────────────────────────────────────────────────

    def _handle_promo_event(self, ev):
        if ev.type != pygame.MOUSEBUTTONDOWN: return
        mx, my = ev.pos
        pieces = ['♕','♖','♗','♘'] if self.promo_color == 'white' else ['♛','♜','♝','♞']
        rects  = self._promo_rects()
        for i, r in enumerate(rects):
            if r.collidepoint(mx, my):
                move = self.promo_pending
                self.state         = "game"
                self.promo_pending = None
                self._apply_human_move(move, promo_piece=pieces[i])
                return

    def _promo_rects(self):
        bx = BOARD_W // 2 - 110
        by = BOARD_H // 2 - 40
        return [pygame.Rect(bx + i*60, by, 55, 80) for i in range(4)]

    def _draw_promo_overlay(self):
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        self.screen.blit(overlay, (0,0))
        pieces = ['♕','♖','♗','♘'] if self.promo_color == 'white' else ['♛','♜','♝','♞']
        rects  = self._promo_rects()
        lbl    = self.big_font.render("Promote pawn:", True, C_TEXT)
        bx = BOARD_W//2 - lbl.get_width()//2
        self.screen.blit(lbl, (bx, BOARD_H//2 - 70))
        mx, my = pygame.mouse.get_pos()
        for i, (p, r) in enumerate(zip(pieces, rects)):
            col = C_BTN_HOV if r.collidepoint(mx,my) else C_BTN
            pygame.draw.rect(self.screen, col, r, border_radius=8)
            pt = self.piece_font.render(p, True, C_WHITE_PIE if self.promo_color=='white' else C_BLACK_PIE)
            self.screen.blit(pt, (r.centerx - pt.get_width()//2, r.centery - pt.get_height()//2))

    # ── Game over ────────────────────────────────────────────────────────────

    def _handle_gameover_event(self, ev):
        if ev.type != pygame.MOUSEBUTTONDOWN: return
        rb = self._restart_btn()
        mb = self._menu_btn()
        mx,my = ev.pos
        if rb.collidepoint(mx,my): self.state = "menu"
        if mb.collidepoint(mx,my): self.state = "menu"

    def _draw_gameover_overlay(self):
        overlay = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        self.screen.blit(overlay, (BOARD_X, BOARD_Y))
        lbl = self.big_font.render(self.status_msg, True, (255,230,50))
        x   = BOARD_X + BOARD_W//2 - lbl.get_width()//2
        self.screen.blit(lbl, (x, BOARD_H//2 - 20))
        sub = self.ui_font.render("Click 'Menu' to play again", True, C_TEXT)
        self.screen.blit(sub, (BOARD_X + BOARD_W//2 - sub.get_width()//2, BOARD_H//2 + 20))

    # ── Drawing ──────────────────────────────────────────────────────────────

    def _restart_btn(self):
        px = BOARD_W + 20
        return pygame.Rect(px, WIN_H - 60, 100, 40)

    def _menu_btn(self):
        px = BOARD_W + 135
        return pygame.Rect(px, WIN_H - 60, 100, 40)

    def _draw_game(self):
        s = self.screen
        s.fill(C_BG)
        self._draw_board()
        self._draw_pieces()
        self._draw_panel()

    def _draw_board(self):
        s = self.screen
        # Coordinate labels
        files = "abcdefgh"
        ranks  = "87654321"
        if self.human_color == 'black':
            files = files[::-1]
            ranks  = ranks[::-1]

        # Highlight last move
        lm_squares = set()
        if self.last_move:
            lm_squares = {(self.last_move[0], self.last_move[1]),
                          (self.last_move[2], self.last_move[3])}

        # Highlight legal target squares
        legal_targets = {(m[2], m[3]) for m in self.legal_moves}

        # Find king in check
        check_sq = None
        if self.in_check and self.state == "game":
            king = '♔' if self.turn == 'white' else '♚'
            for r in range(8):
                for c in range(8):
                    if self.board[r][c] == king:
                        check_sq = (r, c)

        for r in range(8):
            for c in range(8):
                br = r if self.human_color == 'white' else 7-r
                bc = c if self.human_color == 'white' else 7-c
                x  = BOARD_X + c * SQUARE
                y  = BOARD_Y + r * SQUARE
                base_col = C_LIGHT if (br+bc) % 2 == 0 else C_DARK
                pygame.draw.rect(s, base_col, (x, y, SQUARE, SQUARE))

                # Last move tint
                if (br,bc) in lm_squares:
                    tint = pygame.Surface((SQUARE,SQUARE), pygame.SRCALPHA)
                    tint.fill(C_LAST_MOVE)
                    s.blit(tint, (x,y))

                # Selected square
                if self.selected and self.selected == (br,bc):
                    tint = pygame.Surface((SQUARE,SQUARE), pygame.SRCALPHA)
                    tint.fill(C_SELECTED)
                    s.blit(tint, (x,y))

                # Legal move dots
                if (br,bc) in legal_targets:
                    tint = pygame.Surface((SQUARE,SQUARE), pygame.SRCALPHA)
                    tint.fill(C_LEGAL)
                    s.blit(tint, (x,y))
                    dot_r = SQUARE//8
                    pygame.draw.circle(s, (50,130,220), (x+SQUARE//2, y+SQUARE//2), dot_r)

                # Check highlight
                if check_sq and check_sq == (br,bc):
                    tint = pygame.Surface((SQUARE,SQUARE), pygame.SRCALPHA)
                    tint.fill(C_CHECK)
                    s.blit(tint, (x,y))

        # Draw coords
        for i in range(8):
            # File labels (bottom row)
            lbl = self.label_font.render(files[i], True, C_TEXT_DIM)
            s.blit(lbl, (BOARD_X + i*SQUARE + SQUARE - lbl.get_width() - 3,
                          BOARD_Y + 8*SQUARE - lbl.get_height() - 2))
            # Rank labels (left column)
            lbl = self.label_font.render(ranks[i], True, C_TEXT_DIM)
            s.blit(lbl, (BOARD_X + 3, BOARD_Y + i*SQUARE + 3))

    def _draw_pieces(self):
        s = self.screen
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == '.': continue
                dr = r if self.human_color == 'white' else 7-r
                dc = c if self.human_color == 'white' else 7-c
                x  = BOARD_X + dc * SQUARE
                y  = BOARD_Y + dr * SQUARE

                # Skip selected piece if held
                if self.selected == (r, c): pass

                is_white_p = p in WHITE_PIECES
                # Shadow / outline
                shadow_col = (80,80,80) if is_white_p else (180,180,180)
                pt = self.piece_font.render(p, True, shadow_col)
                cx = x + SQUARE//2 - pt.get_width()//2
                cy = y + SQUARE//2 - pt.get_height()//2
                for ox,oy in ((-1,0),(1,0),(0,-1),(0,1)):
                    s.blit(pt, (cx+ox*2, cy+oy*2))
                # Main piece
                main_col = C_WHITE_PIE if is_white_p else C_BLACK_PIE
                pt2 = self.piece_font.render(p, True, main_col)
                s.blit(pt2, (cx, cy))

    def _draw_panel(self):
        s    = self.screen
        px   = BOARD_W
        pw   = PANEL_W
        ph   = WIN_H
        pygame.draw.rect(s, C_PANEL_BG, (px, 0, pw, ph))

        y = 16
        # Title
        t = self.big_font.render("Chess Bot", True, C_TEXT)
        s.blit(t, (px + pw//2 - t.get_width()//2, y)); y += 36

        # Difficulty badge
        diff_labels = {1:"Easy",2:"Medium",3:"Hard"}
        diff_cols   = {1:(80,160,80),2:(160,130,50),3:(160,60,60)}
        dl = diff_labels[self.difficulty]
        dc = diff_cols[self.difficulty]
        dbadge = pygame.Rect(px + pw//2 - 45, y, 90, 26)
        pygame.draw.rect(s, dc, dbadge, border_radius=6)
        dt = self.ui_font.render(dl, True, C_TEXT)
        s.blit(dt, (dbadge.centerx - dt.get_width()//2, dbadge.centery - dt.get_height()//2))
        y += 40

        # Turn / status
        turn_str = ("Your turn" if self.turn == self.human_color else
                    ("Bot thinking..." if self.bot_thinking else "Bot's turn"))
        col = (100,200,100) if self.turn==self.human_color else (200,140,80)
        ts = self.ui_font.render(turn_str, True, col)
        s.blit(ts, (px + pw//2 - ts.get_width()//2, y)); y += 28

        if self.in_check and self.game_result is None:
            ct = self.ui_font.render("CHECK!", True, (230,70,70))
            s.blit(ct, (px + pw//2 - ct.get_width()//2, y)); y += 24

        y += 8
        # Separator
        pygame.draw.line(s, (80,80,80), (px+10, y), (px+pw-10, y)); y += 10

        # Human / bot info
        ht = self.small_font.render(f"You:  {self.human_color.capitalize()}", True, C_TEXT_DIM)
        bt = self.small_font.render(f"Bot:  {self.bot_color.capitalize()}", True, C_TEXT_DIM)
        s.blit(ht, (px+12, y));     y += 20
        s.blit(bt, (px+12, y));     y += 26

        pygame.draw.line(s, (80,80,80), (px+10, y), (px+pw-10, y)); y += 10

        # Move log header
        mh = self.small_font.render("Move history:", True, C_TEXT_DIM)
        s.blit(mh, (px+12, y)); y += 22

        # Move log (last 20 moves)
        log_area_h = WIN_H - y - 80
        log = self.move_history_log[-(log_area_h//18):]
        for i, mv in enumerate(log):
            col = C_TEXT if i==len(log)-1 else C_TEXT_DIM
            mt = self.small_font.render(f"{len(self.move_history_log)-len(log)+i+1}. {mv}", True, col)
            s.blit(mt, (px+12, y)); y += 18

        # Buttons
        rb = self._restart_btn()
        mb = self._menu_btn()
        mx_m, my_m = pygame.mouse.get_pos()
        for btn, label in [(rb,"Restart"),(mb,"Menu")]:
            c = C_BTN_HOV if btn.collidepoint(mx_m,my_m) else C_BTN
            pygame.draw.rect(s, c, btn, border_radius=7)
            bt = self.ui_font.render(label, True, C_TEXT)
            s.blit(bt, (btn.centerx - bt.get_width()//2, btn.centery - bt.get_height()//2))

        # Thinking spinner
        if self.bot_thinking:
            dots = "." * ((pygame.time.get_ticks()//400) % 4)
            sp = self.small_font.render(f"Calculating{dots}", True, (180,180,80))
            s.blit(sp, (px + pw//2 - sp.get_width()//2, WIN_H - 90))


def main():
    gui = ChessGUI()
    gui.run()


if __name__ == "__main__":
    main()
