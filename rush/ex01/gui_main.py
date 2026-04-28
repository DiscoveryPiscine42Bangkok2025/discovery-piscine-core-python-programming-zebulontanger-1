import pygame
import random
import pickle
import sys
import threading
import time
from bot import lookup_opening

WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 100,  '♘': 320,  '♗': 330,  '♖': 500,  '♕': 900,  '♔': 20000,
    '♟': -100, '♞': -320, '♝': -330, '♜': -500, '♛': -900, '♚': -20000,
}

INF = 10_000_000

PAWN_TABLE = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [ 50, 50, 50, 50, 50, 50, 50, 50],
    [ 10, 10, 20, 30, 30, 20, 10, 10],
    [  5,  5, 10, 25, 25, 10,  5,  5],
    [  0,  0,  0, 20, 20,  0,  0,  0],
    [  5, -5,-10,  0,  0,-10, -5,  5],
    [  5, 10, 10,-20,-20, 10, 10,  5],
    [  0,  0,  0,  0,  0,  0,  0,  0],
]
KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50],
]
BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20],
]
ROOK_TABLE = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  5, 10, 10, 10, 10, 10, 10,  5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [  0,  0,  0,  5,  5,  0,  0,  0],
]
QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20],
]
KING_MID = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20],
]
KING_END = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50],
]
PST = {
    '♙': PAWN_TABLE,   '♟': PAWN_TABLE,
    '♘': KNIGHT_TABLE, '♞': KNIGHT_TABLE,
    '♗': BISHOP_TABLE, '♝': BISHOP_TABLE,
    '♖': ROOK_TABLE,   '♜': ROOK_TABLE,
    '♕': QUEEN_TABLE,  '♛': QUEEN_TABLE,
}

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
HM_WK=1; HM_BK=2; HM_WRA=4; HM_WRH=8; HM_BRA=16; HM_BRH=32
has_moved_bits = 0

en_passant_target = None
current_turn = 'white'
player_color = 'black'
bot_color    = 'white'
learned_values = {}
move_history = []

# depth, flag, score, best_move
tt = {}
TT_MAX = 2_000_000

# Threading
bot_thinking = False
bot_result_move = None

def is_white_piece(p): return p in WHITE_PIECES
def is_black_piece(p): return p in BLACK_PIECES

def load_knowledge():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
        print(f"[Brain] Loaded {len(learned_values)} positions.")
    except:
        learned_values = {}

def board_key():
    return "".join("".join(r) for r in board)

def _is_endgame():
    pieces = [p for row in board for p in row if p != '.']
    return sum(1 for p in pieces if p in {'♕','♛'}) == 0 or len(pieces) <= 12

def get_piece_pseudo_moves(r, c, ignore_ep=False):
    p = board[r][c]
    moves = []
    is_white = p in WHITE_PIECES
    enemy    = BLACK_PIECES if is_white else WHITE_PIECES
    friendly = WHITE_PIECES if is_white else BLACK_PIECES

    if p in {'♖','♜','♕','♛','♗','♝'}:
        dirs = []
        if p in {'♖','♜','♕','♛'}: dirs += [(0,1),(0,-1),(1,0),(-1,0)]
        if p in {'♗','♝','♕','♛'}: dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == '.':
                    moves.append((r,c,nr,nc))
                elif board[nr][nc] in enemy:
                    moves.append((r,c,nr,nc)); break
                else:
                    break
                nr += dr; nc += dc
    elif p in {'♘','♞'}:
        for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr,nc = r+dr, c+dc
            if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly:
                moves.append((r,c,nr,nc))
    elif p in {'♔','♚'}:
        for dr,dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nr,nc = r+dr, c+dc
            if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly:
                moves.append((r,c,nr,nc))
    elif p == '♙':
        if r>0 and board[r-1][c]=='.':
            moves.append((r,c,r-1,c))
            if r==6 and board[r-2][c]=='.': moves.append((r,c,r-2,c))
        for dc in [-1,1]:
            if r>0 and 0<=c+dc<8:
                if board[r-1][c+dc] in enemy: moves.append((r,c,r-1,c+dc))
                if not ignore_ep and (r-1,c+dc)==en_passant_target: moves.append((r,c,r-1,c+dc))
    elif p == '♟':
        if r<7 and board[r+1][c]=='.':
            moves.append((r,c,r+1,c))
            if r==1 and board[r+2][c]=='.': moves.append((r,c,r+2,c))
        for dc in [-1,1]:
            if r<7 and 0<=c+dc<8:
                if board[r+1][c+dc] in enemy: moves.append((r,c,r+1,c+dc))
                if not ignore_ep and (r+1,c+dc)==en_passant_target: moves.append((r,c,r+1,c+dc))
    return moves

def is_square_attacked(r, c, attacker_color):
    """Fast direct attack detection — no move generation needed."""
    is_att_white = (attacker_color == 'white')
    att_pieces   = WHITE_PIECES if is_att_white else BLACK_PIECES

    # Knight attacks
    nkp = ('♘' if is_att_white else '♞')
    for dr, dc in ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)):
        nr, nc = r+dr, c+dc
        if 0<=nr<8 and 0<=nc<8 and board[nr][nc] == nkp:
            return True

    # King attacks
    kp = ('♔' if is_att_white else '♚')
    for dr, dc in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)):
        nr, nc = r+dr, c+dc
        if 0<=nr<8 and 0<=nc<8 and board[nr][nc] == kp:
            return True

    # Pawn attacks
    pawn = '♙' if is_att_white else '♟'
    pdr  = 1 if is_att_white else -1   # direction pawns attack
    for dc in (-1, 1):
        nr, nc = r+pdr, c+dc
        if 0<=nr<8 and 0<=nc<8 and board[nr][nc] == pawn:
            return True

    # Sliding: rook/queen (straight lines)
    rq = {'♖','♕'} if is_att_white else {'♜','♛'}
    for dr, dc in ((0,1),(0,-1),(1,0),(-1,0)):
        nr, nc = r+dr, c+dc
        while 0<=nr<8 and 0<=nc<8:
            sq = board[nr][nc]
            if sq != '.':
                if sq in rq: return True
                break
            nr += dr; nc += dc

    # Sliding: bishop/queen (diagonals)
    bq = {'♗','♕'} if is_att_white else {'♝','♛'}
    for dr, dc in ((1,1),(1,-1),(-1,1),(-1,-1)):
        nr, nc = r+dr, c+dc
        while 0<=nr<8 and 0<=nc<8:
            sq = board[nr][nc]
            if sq != '.':
                if sq in bq: return True
                break
            nr += dr; nc += dc

    return False

def get_all_valid_moves(color):
    pseudo = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if (color=='white' and p in WHITE_PIECES) or \
               (color=='black' and p in BLACK_PIECES):
                pseudo.extend(get_piece_pseudo_moves(r, c))

    valid = []
    enemy_color = 'black' if color=='white' else 'white'
    king_sym = '♔' if color=='white' else '♚'

    for sr,sc,er,ec in pseudo:
        orig_p, dest_p = board[sr][sc], board[er][ec]
        board[er][ec], board[sr][sc] = orig_p, '.'
        kp = next(((r,c) for r in range(8) for c in range(8) if board[r][c]==king_sym), None)
        if kp and not is_square_attacked(kp[0], kp[1], enemy_color):
            valid.append((sr,sc,er,ec))
        board[sr][sc], board[er][ec] = orig_p, dest_p

    if color=='white' and not (has_moved_bits & HM_WK):
        if not (has_moved_bits & HM_WRH) and board[7][5]=='.' and board[7][6]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,5,6]):
            valid.append((7,4,7,6))
        if not (has_moved_bits & HM_WRA) and board[7][1]=='.' and board[7][2]=='.' and board[7][3]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,3,2]):
            valid.append((7,4,7,2))
    elif color=='black' and not (has_moved_bits & HM_BK):
        if not (has_moved_bits & HM_BRH) and board[0][5]=='.' and board[0][6]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,5,6]):
            valid.append((0,4,0,6))
        if not (has_moved_bits & HM_BRA) and board[0][1]=='.' and board[0][2]=='.' and board[0][3]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,3,2]):
            valid.append((0,4,0,2))
    return valid

def apply_move(sr, sc, er, ec):
    global en_passant_target, has_moved_bits
    piece    = board[sr][sc]
    captured = board[er][ec]
    ep_save  = en_passant_target
    hm_save  = has_moved_bits

    ep_cap_pos = None
    ep_cap_piece = None
    if piece in {'♙','♟'} and (er,ec) == en_passant_target:
        ep_cap_pos   = (sr, ec)
        ep_cap_piece = board[sr][ec]
        board[sr][ec] = '.'

    en_passant_target = None
    if piece=='♙' and sr==6 and er==4: en_passant_target=(5,sc)
    if piece=='♟' and sr==1 and er==3: en_passant_target=(2,sc)

    rook_undo = None
    if piece=='♔' and sc==4:
        has_moved_bits |= HM_WK
        if ec==6: board[7][5],board[7][7]=board[7][7],'.'; rook_undo=((7,7),(7,5))
        if ec==2: board[7][3],board[7][0]=board[7][0],'.'; rook_undo=((7,0),(7,3))
    elif piece=='♚' and sc==4:
        has_moved_bits |= HM_BK
        if ec==6: board[0][5],board[0][7]=board[0][7],'.'; rook_undo=((0,7),(0,5))
        if ec==2: board[0][3],board[0][0]=board[0][0],'.'; rook_undo=((0,0),(0,3))
    if piece=='♖':
        if sr==7 and sc==0: has_moved_bits |= HM_WRA
        if sr==7 and sc==7: has_moved_bits |= HM_WRH
    elif piece=='♜':
        if sr==0 and sc==0: has_moved_bits |= HM_BRA
        if sr==0 and sc==7: has_moved_bits |= HM_BRH

    board[er][ec]=piece; board[sr][sc]='.'
    promoted = None
    if piece=='♙' and er==0: board[er][ec]='♕'; promoted='♕'
    if piece=='♟' and er==7: board[er][ec]='♛'; promoted='♛'

    return (sr,sc,er,ec,piece,captured,ep_save,hm_save,
            ep_cap_pos,ep_cap_piece,rook_undo,promoted)

def undo_move(bundle):
    global en_passant_target, has_moved_bits
    sr,sc,er,ec,piece,captured,ep_save,hm_save, \
        ep_cap_pos,ep_cap_piece,rook_undo,promoted = bundle
    en_passant_target = ep_save
    has_moved_bits    = hm_save
    board[sr][sc] = piece
    board[er][ec] = captured
    if ep_cap_pos:
        board[ep_cap_pos[0]][ep_cap_pos[1]] = ep_cap_piece
    if rook_undo:
        orig_pos, moved_pos = rook_undo
        board[orig_pos[0]][orig_pos[1]] = board[moved_pos[0]][moved_pos[1]]
        board[moved_pos[0]][moved_pos[1]] = '.'

def static_eval():
    score = 0
    pieces = [p for row in board for p in row if p != '.']
    queens  = sum(1 for p in pieces if p in {'♕','♛'})
    endgame = (queens == 0 or len(pieces) <= 12)
    wpf, bpf = [], []

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            score += PIECE_VALUES[p]
            is_wp = p in WHITE_PIECES
            tr = r if is_wp else (7-r)
            sign = 1 if is_wp else -1

            if p in {'♔','♚'}:
                score += sign * (KING_END[tr][c] if endgame else KING_MID[tr][c])
            elif p in PST:
                score += sign * PST[p][tr][c]

            if p == '♙': wpf.append(c)
            elif p == '♟': bpf.append(c)

    for f in set(wpf):
        if wpf.count(f) > 1:  score -= 30 * (wpf.count(f)-1)
        if not any(af in wpf for af in [f-1,f+1]): score -= 20
    for f in set(bpf):
        if bpf.count(f) > 1:  score += 30 * (bpf.count(f)-1)
        if not any(af in bpf for af in [f-1,f+1]): score += 20

    for c in range(8):
        col = [board[r][c] for r in range(8) if board[r][c]!='.']
        hwp='♙' in col; hbp='♟' in col
        for r in range(8):
            p = board[r][c]
            if p=='♖':   score += 30 if not hwp and not hbp else (15 if not hwp else 0)
            elif p=='♜': score -= 30 if not hwp and not hbp else (15 if not hbp else 0)

    score += int(learned_values.get(board_key(), 0) * 100)
    return score

def order_moves(moves, tt_move=None):
    def priority(m):
        if m == tt_move: return 200_000
        sr,sc,er,ec = m
        victim   = board[er][ec]
        attacker = board[sr][sc]
        if victim != '.':
            return 10_000 + abs(PIECE_VALUES.get(victim,0)) - abs(PIECE_VALUES.get(attacker,0))//10

        is_wp = attacker in WHITE_PIECES
        tr_from = sr if is_wp else (7-sr)
        tr_to   = er if is_wp else (7-er)
        tbl = PST.get(attacker)
        return (tbl[tr_to][ec] - tbl[tr_from][sc]) if tbl else 0

    moves.sort(key=priority, reverse=True)
    return moves

_NULL_REDUCTION = 2 
_LMR_MIN_DEPTH  = 3 
_LMR_MIN_MOVE   = 4 

def negamax(depth, alpha, beta, color, null_ok=True):
    global en_passant_target
    orig_alpha = alpha
    key = board_key()

    if key in tt:
        td, flag, ts, tm = tt[key]
        if td >= depth:
            if flag == 'exact':  return ts
            if flag == 'lower':  alpha = max(alpha, ts)
            elif flag == 'upper': beta = min(beta, ts)
            if alpha >= beta:    return ts

    cur_color_name = 'white' if color == 1 else 'black'
    enemy_color    = 'black' if color == 1 else 'white'
    king_sym       = '♔'     if color == 1 else '♚'

    if depth == 0:
        return color * static_eval()

    if null_ok and depth >= _NULL_REDUCTION + 1:
        kp = next(((r,c) for r in range(8) for c in range(8) if board[r][c]==king_sym), None)
        in_check = kp and is_square_attacked(kp[0], kp[1], enemy_color)
        pieces = sum(1 for row in board for p in row if p != '.' and p in WHITE_PIECES | BLACK_PIECES)
        not_endgame = pieces > 12
        if not in_check and not_endgame:
            ep_save2 = en_passant_target
            null_score = -negamax(depth - 1 - _NULL_REDUCTION, -beta, -beta+1, -color, False)
            en_passant_target = ep_save2
            if null_score >= beta:
                return beta

    moves = get_all_valid_moves(cur_color_name)

    if not moves:
        kp = next(((r,c) for r in range(8) for c in range(8) if board[r][c]==king_sym), None)
        if kp and is_square_attacked(kp[0], kp[1], enemy_color):
            return -INF + (100 - depth)
        return 0  # stalemate

    tt_move = tt[key][3] if key in tt else None
    moves = order_moves(moves, tt_move)

    best_score = -INF
    best_move  = moves[0]

    for i, m in enumerate(moves):
        bnd = apply_move(*m)

        is_capture = (bnd[5] != '.')
        if (depth >= _LMR_MIN_DEPTH and i >= _LMR_MIN_MOVE
                and not is_capture and m != tt_move):
            # Search at reduced depth first
            reduction = 1 + (depth // 4)
            score = -negamax(depth - 1 - reduction, -alpha-1, -alpha, -color)
            if alpha < score < beta:
                score = -negamax(depth - 1, -beta, -alpha, -color)
        else:
            score = -negamax(depth - 1, -beta, -alpha, -color)

        undo_move(bnd)

        if score > best_score:
            best_score, best_move = score, m
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    if len(tt) < TT_MAX:
        flag = ('exact'  if orig_alpha < best_score < beta else
                'lower'  if best_score >= beta else
                'upper')
        tt[key] = (depth, flag, best_score, best_move)

    return best_score


def find_best_move(max_depth=8, time_limit=12.0):
    best_move = None
    start = time.time()

    moves = get_all_valid_moves(bot_color)
    if not moves: return None

    for depth in range(1, max_depth + 1):
        alpha, beta = -INF, INF

        tt_move = tt.get(board_key(), (None,)*4)[3]
        moves = order_moves(moves, tt_move)

        iter_best_score = -INF
        iter_best_move  = moves[0]

        for m in moves:
            bnd = apply_move(*m)
            score = -negamax(depth-1, -beta, -alpha, -1)
            undo_move(bnd)

            if score > iter_best_score:
                iter_best_score, iter_best_move = score, m
            alpha = max(alpha, score)

        best_move = iter_best_move

        if time.time() - start > time_limit:
            break

    return best_move



def execute_move(sr, sc, er, ec):
    global en_passant_target, has_moved_bits
    move_history.append((sr, sc, er, ec))
    piece = board[sr][sc]

    if piece in {'♙','♟'} and (er,ec)==en_passant_target:
        board[sr][ec] = '.'

    en_passant_target = None
    if piece=='♙' and sr==6 and er==4: en_passant_target=(5,sc)
    if piece=='♟' and sr==1 and er==3: en_passant_target=(2,sc)

    if piece=='♔' and sc==4:
        has_moved_bits |= HM_WK
        if ec==6: board[7][5],board[7][7]=board[7][7],'.'
        if ec==2: board[7][3],board[7][0]=board[7][0],'.'
    elif piece=='♚' and sc==4:
        has_moved_bits |= HM_BK
        if ec==6: board[0][5],board[0][7]=board[0][7],'.'
        if ec==2: board[0][3],board[0][0]=board[0][0],'.'

    if piece=='♖':
        if sr==7 and sc==0: has_moved_bits |= HM_WRA
        if sr==7 and sc==7: has_moved_bits |= HM_WRH
    elif piece=='♜':
        if sr==0 and sc==0: has_moved_bits |= HM_BRA
        if sr==0 and sc==7: has_moved_bits |= HM_BRH

    board[er][ec]=piece; board[sr][sc]='.'
    if piece=='♙' and er==0: board[er][ec]='♕'
    if piece=='♟' and er==7: board[er][ec]='♛'

def bot_think_thread():
    global bot_thinking, bot_result_move
    bot_thinking = True

    book_move = lookup_opening(move_history, bot_color)
    if book_move:
        bot_result_move = book_move
        bot_thinking = False
        print(f"[Bot] {book_move} (book)")
        return

    move = find_best_move(max_depth=8, time_limit=12.0)
    bot_result_move = move
    bot_thinking = False
    print(f"[Bot] {move}")

pygame.init()
load_knowledge()
WIDTH, SQ = 600, 75
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Chess — Depth 8")
FONT_SM  = pygame.font.SysFont("segoeuisymbol", 20)
FONT_MED = pygame.font.SysFont("segoeuisymbol", 32)
FONT_BIG = pygame.font.SysFont("segoeuisymbol", 52)
CLK     = pygame.time.Clock()


def choose_color_screen():
    """Show a colour-selection splash and return 'white' or 'black'."""
    btn_w, btn_h = 200, 60
    pad = 30

    white_rect = pygame.Rect(WIDTH//2 - btn_w - pad//2, WIDTH//2 - btn_h//2, btn_w, btn_h)
    black_rect = pygame.Rect(WIDTH//2 + pad//2,          WIDTH//2 - btn_h//2, btn_w, btn_h)

    hover_w = hover_b = False
    while True:
        screen.fill((40, 40, 40))

        # Title
        title = FONT_BIG.render("♛  Chess  ♚", True, (230, 200, 100))
        screen.blit(title, title.get_rect(center=(WIDTH//2, WIDTH//3 - 20)))

        sub = FONT_MED.render("Choose your colour", True, (200, 200, 200))
        screen.blit(sub, sub.get_rect(center=(WIDTH//2, WIDTH//3 + 50)))

        mx, my = pygame.mouse.get_pos()
        hover_w = white_rect.collidepoint(mx, my)
        hover_b = black_rect.collidepoint(mx, my)

        # White button
        pygame.draw.rect(screen, (255, 255, 255) if not hover_w else (220, 220, 180), white_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 150), white_rect, 2, border_radius=10)
        wlbl = FONT_MED.render("♔  White", True, (30, 30, 30))
        screen.blit(wlbl, wlbl.get_rect(center=white_rect.center))

        # Black button
        pygame.draw.rect(screen, (50, 50, 50) if not hover_b else (80, 60, 30), black_rect, border_radius=10)
        pygame.draw.rect(screen, (180, 180, 180), black_rect, 2, border_radius=10)
        blbl = FONT_MED.render("♚  Black", True, (230, 230, 230))
        screen.blit(blbl, blbl.get_rect(center=black_rect.center))

        note = FONT_SM.render("White moves first", True, (140, 140, 140))
        screen.blit(note, note.get_rect(center=(WIDTH//2, WIDTH//2 + btn_h + 20)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if white_rect.collidepoint(event.pos):
                    return 'white'
                if black_rect.collidepoint(event.pos):
                    return 'black'
        CLK.tick(30)

import io, base64

def _svg_surface(svg_str, size=SQ-4):
    """Rasterise an SVG string to a pygame.Surface (with alpha)."""
    try:
        import cairosvg
        png_bytes = cairosvg.svg2png(bytestring=svg_str.encode(), output_width=size, output_height=size)
        buf = io.BytesIO(png_bytes)
        surf = pygame.image.load(buf, "piece.png").convert_alpha()
        return surf
    except Exception:
        return None

_W = "#ffffff"  # white fill
_B = "#1a1a1a"  # black fill
_SO = "#1a1a1a" # stroke for white pieces
_SW = "#ffffff"  # stroke for black pieces

def _piece_svg(paths_fill, paths_stroke, fill_col, stroke_col, bg=None):
    bg_rect = f'<rect width="45" height="45" rx="2" fill="{bg}" />' if bg else ""
    fills   = "".join(f'<path d="{d}" fill="{fill_col}" />' for d in paths_fill)
    strokes = "".join(f'<path d="{d}" fill="none" stroke="{stroke_col}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' for d in paths_stroke)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">'
            f'{bg_rect}{fills}{strokes}</svg>')

_PATHS = {
    "pawn_fill": [
        "M22.5 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03C15.41 27.09 14 29.5 14 32c0 1.1.9 2 2 2h17c1.1 0 2-.9 2-2 0-2.5-1.41-4.91-4.41-5.97C32.06 24.84 33 23.03 33 21c0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z"
    ],
    "pawn_stroke": [],
    "knight_fill": [
        "M 22,10 C 32.5,11 38.5,18 38,39 L 15,39 C 15,30 25,32.5 23,18"
        " M 24,18 C 24.38,20.91 18.45,25.37 16,27 C 13,29 13.18,31.34 11,31"
        " C 9.958,30.06 12.41,27.96 11,28 C 10,28 11.19,29.23 10,30"
        " C 9,30 5.997,31 6,26 C 6,24 12,14 12,14 C 12,14 13.89,12.1 14,10.5"
        " C 13.27,9.506 13.5,8.5 13.5,7.5 C 14.5,6.5 16.5,10 16.5,10"
        " L 18.5,10 C 18.5,10 19.28,8.008 21,7 C 22,7 22,10 22,10"
    ],
    "knight_stroke": [
        "M 11.5,37 C 17,40.5 27,40.5 32.5,37 L 32.5,30 C 32.5,30 41.5,25.5 38.5,19.5"
        " C 34.5,13 25,16 22,23.5 L 22,27 L 12.5,27 L 12.5,37"
        " M 11.5,30 L 32.5,30 M 11.5,33 L 32.5,33 M 11.5,36 L 32.5,36"
    ],
    "bishop_fill": [
        "M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36"
        " C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5"
        " C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5"
        " C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.06 9,36 9,36 z",
        "M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30"
        " C 30,27.5 27.5,26 22.5,25 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z",
        "M 25,8 A 2.5,2.5 0 1,1 20,8 A 2.5,2.5 0 1,1 25,8 z",
        "M 17,16 L 27,16 M 15,20 L 30,20 M 22.5,15 L 22.5,36 M 22.5,24 L 15,32"
        " M 22.5,24 L 30,32"
    ],
    "bishop_stroke": [
        "M 15,32 C 17.5,34.5 27.5,34.5 30,32",
        "M 15,32 C 15,29 30,29 30,32"
    ],
    "rook_fill": [
        "M 9,39 L 36,39 L 36,36 L 9,36 L 9,39 z",
        "M 12,36 L 12,32 L 33,32 L 33,36 L 12,36 z",
        "M 11,14 L 11,9 L 15,9 L 15,11 L 20,11 L 20,9 L 25,9 L 25,11 L 30,11 L 30,9 L 34,9 L 34,14"
    ],
    "rook_stroke": [
        "M 11,14 L 11,32 L 34,32 L 34,14 L 11,14 z"
    ],
    "queen_fill": [
        "M 9,26 C 17.5,24.5 30,24.5 36,26 L 38.5,13.5 L 31,25"
        " L 30.7,10.9 L 22.5,24.5 L 14.3,10.9 L 14,25 L 6.5,13.5 L 9,26 z",
        "M 9,26 C 9,28 10.5,28 11.5,30 C 12.5,31.5 12.5,31 12,33.5"
        " C 10.5,34.5 10.5,36 10.5,36 C 9,37.5 11,38.5 11,38.5"
        " C 17.5,39.5 27.5,39.5 34,38.5 C 34,38.5 35.5,37.5 34,36"
        " C 34,36 34.5,34.5 33,33.5 C 32.5,31 32.5,31.5 33.5,30"
        " C 34.5,28 36,28 36,26 C 27.5,24.5 17.5,24.5 9,26 z",
        "M 11.5,11.5 A 1,1 0 1,1 9.5,11.5 A 1,1 0 1,1 11.5,11.5 z",
        "M 14.5,8 A 1,1 0 1,1 12.5,8 A 1,1 0 1,1 14.5,8 z",
        "M 22.5,6 A 1,1 0 1,1 20.5,6 A 1,1 0 1,1 22.5,6 z",
        "M 30.5,8 A 1,1 0 1,1 28.5,8 A 1,1 0 1,1 30.5,8 z",
        "M 33.5,11.5 A 1,1 0 1,1 31.5,11.5 A 1,1 0 1,1 33.5,11.5 z"
    ],
    "queen_stroke": [
        "M 9,26 C 17.5,24.5 30,24.5 36,26",
        "M 11,38.5 A 35,35 1 0 0 34,38.5",
        "M 11,29 A 35,35 1 0 1 34,29",
        "M 12.5,31.5 L 32.5,31.5",
        "M 11.5,34.5 A 35,35 1 0 0 33.5,34.5"
    ],
    "king_fill": [
        "M 22.5,11.63 L 22.5,6",
        "M 20,8 L 25,8",
        "M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 25.5,14.5 24.5,12 22.5,12"
        " C 20.5,12 19.5,14.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25",
        "M 11.5,37 C 17,40.5 27,40.5 32.5,37 L 32.5,30 C 27,33 17,33 11.5,30 L 11.5,37 z",
        "M 11.5,30 C 17,27 27,27 32.5,30 L 32.5,35 C 27,38 17,38 11.5,35 L 11.5,30 z",
        "M 11.5,30 C 17,33 27,33 32.5,30"
    ],
    "king_stroke": [
        "M 22.5,11.63 L 22.5,6 M 20,8 L 25,8",
        "M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 25.5,14.5 24.5,12 22.5,12"
        " C 20.5,12 19.5,14.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25",
        "M 11.5,37 C 17,40.5 27,40.5 32.5,37 L 32.5,30 C 27,33 17,33 11.5,30 L 11.5,37 z",
        "M 11.5,30 C 17,27 27,27 32.5,30"
    ],
}

def _build_piece_surface(piece_type, is_white):
    fill_col   = _W  if is_white else _B
    stroke_col = _SO if is_white else _SW
    pt = piece_type
    fills   = _PATHS.get(f"{pt}_fill",   [])
    strokes = _PATHS.get(f"{pt}_stroke", [])
    svg = _piece_svg(fills, strokes, fill_col, stroke_col)
    surf = _svg_surface(svg)
    return surf

# type_str, is_white
_PIECE_INFO = {
    '♙': ("pawn",   True),  '♟': ("pawn",   False),
    '♘': ("knight", True),  '♞': ("knight", False),
    '♗': ("bishop", True),  '♝': ("bishop", False),
    '♖': ("rook",   True),  '♜': ("rook",   False),
    '♕': ("queen",  True),  '♛': ("queen",  False),
    '♔': ("king",   True),  '♚': ("king",   False),
}

_piece_surfs = {}

def _pygame_fallback(piece_sym, sq=SQ):
    """Draw a clean piece using pygame primitives — no font required."""
    surf = pygame.Surface((sq, sq), pygame.SRCALPHA)
    pt, iw = _PIECE_INFO[piece_sym]
    body_col    = (255, 255, 255) if iw else (30, 30, 30)
    outline_col = (30,  30,  30)  if iw else (220, 220, 220)
    detail_col  = (30,  30,  30)  if iw else (220, 220, 220)
    cx, cy = sq // 2, sq // 2

    def ellipse(rect, col, width=0):
        pygame.draw.ellipse(surf, col, rect, width)
    def circle(pos, r, col, width=0):
        pygame.draw.circle(surf, col, pos, r, width)
    def rect_f(r, col):
        pygame.draw.rect(surf, col, r)
    def poly(pts, col, width=0):
        pygame.draw.polygon(surf, col, pts, width)

    s = sq / 45  # scale factor (design is 45×45)

    def sc(x, y):   # scale a design coord
        return (int(x * s), int(y * s))
    def sr_(v):
        return max(1, int(v * s))

    if pt == "pawn":
        # base
        pygame.draw.ellipse(surf, body_col,    (sc(10,35)[0], sc(35,35)[1], int(25*s), int(6*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(10,35)[0], sc(35,35)[1], int(25*s), int(6*s)), sr_(1.5))
        # body
        pygame.draw.ellipse(surf, body_col,    (sc(14,22)[0], sc(22,22)[1], int(17*s), int(16*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(14,22)[0], sc(22,22)[1], int(17*s), int(16*s)), sr_(1.5))
        # head
        circle(sc(22,13), sr_(6), body_col)
        circle(sc(22,13), sr_(6), outline_col, sr_(1.5))

    elif pt == "knight":
        # base
        pygame.draw.ellipse(surf, body_col,    (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)), sr_(1.5))
        # body (horse silhouette approximation)
        pts_body = [sc(x,y) for x,y in [
            (11,36),(11,30),(14,25),(14,19),(17,14),(22,9),(27,10),(31,16),
            (31,22),(28,27),(28,33),(34,36)
        ]]
        poly(pts_body, body_col)
        poly(pts_body, outline_col, sr_(1.5))
        # eye
        circle(sc(25,13), sr_(2), detail_col)

    elif pt == "bishop":
        # base
        pygame.draw.ellipse(surf, body_col,    (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)), sr_(1.5))
        # body
        pygame.draw.ellipse(surf, body_col,    (sc(13,24)[0], sc(24,24)[1], int(19*s), int(14*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(13,24)[0], sc(24,24)[1], int(19*s), int(14*s)), sr_(1.5))
        # head
        circle(sc(22,16), sr_(7), body_col)
        circle(sc(22,16), sr_(7), outline_col, sr_(1.5))
        # top ball
        circle(sc(22,9),  sr_(3), body_col)
        circle(sc(22,9),  sr_(3), outline_col, sr_(1.5))
        # dot
        circle(sc(22,9),  sr_(1.5), detail_col)

    elif pt == "rook":
        # base
        pygame.draw.rect(surf, body_col,    (*sc(9,36), int(27*s), int(6*s)))
        pygame.draw.rect(surf, outline_col, (*sc(9,36), int(27*s), int(6*s)), sr_(1.5))
        # shaft
        pygame.draw.rect(surf, body_col,    (*sc(12,16), int(21*s), int(21*s)))
        pygame.draw.rect(surf, outline_col, (*sc(12,16), int(21*s), int(21*s)), sr_(1.5))
        # battlements
        for bx in [10, 17, 25]:
            pygame.draw.rect(surf, body_col,    (*sc(bx,9), int(7*s), int(8*s)))
            pygame.draw.rect(surf, outline_col, (*sc(bx,9), int(7*s), int(8*s)), sr_(1.5))

    elif pt == "queen":
        # base
        pygame.draw.ellipse(surf, body_col,    (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)), sr_(1.5))
        # body
        pts_q = [sc(x,y) for x,y in [
            (9,26),(11,36),(34,36),(36,26),(30,16),(22,30),(14,16)
        ]]
        poly(pts_q, body_col)
        poly(pts_q, outline_col, sr_(1.5))
        # crown balls
        for bx,by in [(9,24),(22,7),(36,24),(14,12),(30,12)]:
            circle(sc(bx,by), sr_(3), body_col)
            circle(sc(bx,by), sr_(3), outline_col, sr_(1.5))

    elif pt == "king":
        # base
        pygame.draw.ellipse(surf, body_col,    (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)))
        pygame.draw.ellipse(surf, outline_col, (sc(8,36)[0], sc(36,36)[1], int(29*s), int(6*s)), sr_(1.5))
        # body
        pygame.draw.rect(surf, body_col,    (*sc(11,28), int(23*s), int(9*s)))
        pygame.draw.rect(surf, outline_col, (*sc(11,28), int(23*s), int(9*s)), sr_(1.5))
        pygame.draw.rect(surf, body_col,    (*sc(14,20), int(17*s), int(9*s)))
        pygame.draw.rect(surf, outline_col, (*sc(14,20), int(17*s), int(9*s)), sr_(1.5))
        # cross vertical
        pygame.draw.rect(surf, body_col,    (*sc(20,6), int(5*s), int(15*s)))
        pygame.draw.rect(surf, outline_col, (*sc(20,6), int(5*s), int(15*s)), sr_(1.5))
        # cross horizontal
        pygame.draw.rect(surf, body_col,    (*sc(15,9), int(15*s), int(5*s)))
        pygame.draw.rect(surf, outline_col, (*sc(15,9), int(15*s), int(5*s)), sr_(1.5))

    return surf

def _load_piece_surfaces():
    for sym, (pt, iw) in _PIECE_INFO.items():
        surf = _build_piece_surface(pt, iw)
        if surf is None:
            surf = _pygame_fallback(sym)
        _piece_surfs[sym] = surf

_load_piece_surfaces()


def draw_board(sel, hints):
    for r in range(8):
        for c in range(8):
            col = (240,217,181) if (r+c)%2==0 else (181,136,99)
            pygame.draw.rect(screen, col, (c*SQ, r*SQ, SQ, SQ))
            if sel==(r,c):
                s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
                s.fill((255,255,0,90))
                screen.blit(s, (c*SQ, r*SQ))
                pygame.draw.rect(screen,(220,200,0),(c*SQ,r*SQ,SQ,SQ),3)
            if (r,c) in hints:
                hint_s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
                pygame.draw.circle(hint_s,(50,200,50,170),(SQ//2,SQ//2),13)
                screen.blit(hint_s,(c*SQ, r*SQ))
            p = board[r][c]
            if p != '.':
                surf = _piece_surfs.get(p)
                if surf:
                    # centre the piece in the square
                    pw, ph = surf.get_size()
                    ox = c*SQ + (SQ - pw)//2
                    oy = r*SQ + (SQ - ph)//2
                    screen.blit(surf, (ox, oy))

    if bot_thinking:
        overlay = pygame.Surface((WIDTH,28), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        screen.blit(overlay,(0,WIDTH-28))
        screen.blit(FONT_SM.render("  Bot thinking (depth 8)…",True,(255,220,50)),(0,WIDTH-26))


def main():
    global current_turn, bot_result_move, player_color, bot_color

    player_color = choose_color_screen()
    bot_color    = 'black' if player_color == 'white' else 'white'
    caption = (f"Chess — You (White) vs Bot (Black) | Depth 8"
               if player_color == 'white' else
               "Chess — You (Black) vs Bot (White) | Depth 8")
    pygame.display.set_caption(caption)

    sel, hints  = None, []
    bot_started = False

    while True:
        CLK.tick(30)

        if current_turn == bot_color and not bot_thinking and not bot_started and bot_result_move is None:
            t = threading.Thread(target=bot_think_thread, daemon=True)
            t.start()
            bot_started = True

        if current_turn == bot_color and not bot_thinking and bot_result_move is not None:
            execute_move(*bot_result_move)
            tt.clear()
            bot_result_move = None
            bot_started     = False
            current_turn    = player_color

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and current_turn == player_color:
                c = event.pos[0] // SQ
                r = event.pos[1] // SQ
                if player_color == 'white':
                    br, bc = r, c
                else:
                    br, bc = r, c   # board is always stored the same way

                if 0 <= br < 8 and 0 <= bc < 8:
                    player_pieces = WHITE_PIECES if player_color == 'white' else BLACK_PIECES
                    if (br, bc) in hints:
                        execute_move(sel[0], sel[1], br, bc)
                        tt.clear()
                        current_turn = bot_color
                        sel, hints = None, []
                    elif board[br][bc] in player_pieces:
                        sel = (br, bc)
                        hints = [(m[2], m[3]) for m in get_all_valid_moves(player_color)
                                 if m[0] == br and m[1] == bc]
                    else:
                        sel, hints = None, []

        draw_board(sel, hints)
        pygame.display.flip()


if __name__ == "__main__":
    main()
