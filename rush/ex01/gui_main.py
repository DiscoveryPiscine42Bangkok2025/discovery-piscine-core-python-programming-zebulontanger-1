import pygame
import random
import pickle
import sys
import threading
import time

# ── Piece sets ───────────────────────────────────────────────────────────────
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 100,  '♘': 320,  '♗': 330,  '♖': 500,  '♕': 900,  '♔': 20000,
    '♟': -100, '♞': -320, '♝': -330, '♜': -500, '♛': -900, '♚': -20000,
}

INF = 10_000_000

# ── Piece-square tables (White perspective; flip row index for Black) ─────────
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

# ── Global game state ─────────────────────────────────────────────────────────
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
has_moved = {
    'white_king': False, 'black_king': False,
    'white_rook_a': False, 'white_rook_h': False,
    'black_rook_a': False, 'black_rook_h': False,
}
en_passant_target = None
current_turn = 'white'
learned_values = {}

# Transposition table: key -> (depth, flag, score, best_move)
tt = {}
TT_MAX = 2_000_000

# Threading
bot_thinking = False
bot_result_move = None


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════

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


# ═══════════════════════════════════════════
# MOVE GENERATION
# ═══════════════════════════════════════════

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
    for ar in range(8):
        for ac in range(8):
            p = board[ar][ac]
            if (attacker_color=='white' and p in WHITE_PIECES) or \
               (attacker_color=='black' and p in BLACK_PIECES):
                for _,_,tr,tc in get_piece_pseudo_moves(ar, ac, ignore_ep=True):
                    if tr==r and tc==c: return True
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

    if color=='white' and not has_moved['white_king']:
        if not has_moved['white_rook_h'] and board[7][5]=='.' and board[7][6]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,5,6]):
            valid.append((7,4,7,6))
        if not has_moved['white_rook_a'] and board[7][1]=='.' and board[7][2]=='.' and board[7][3]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,3,2]):
            valid.append((7,4,7,2))
    elif color=='black' and not has_moved['black_king']:
        if not has_moved['black_rook_h'] and board[0][5]=='.' and board[0][6]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,5,6]):
            valid.append((0,4,0,6))
        if not has_moved['black_rook_a'] and board[0][1]=='.' and board[0][2]=='.' and board[0][3]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,3,2]):
            valid.append((0,4,0,2))
    return valid


# ═══════════════════════════════════════════
# APPLY / UNDO  (for search — reversible)
# ═══════════════════════════════════════════

def apply_move(sr, sc, er, ec):
    global en_passant_target
    piece    = board[sr][sc]
    captured = board[er][ec]
    ep_save  = en_passant_target
    hm_save  = has_moved.copy()

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
        has_moved['white_king']=True
        if ec==6: board[7][5],board[7][7]=board[7][7],'.'; rook_undo=((7,7),(7,5))
        if ec==2: board[7][3],board[7][0]=board[7][0],'.'; rook_undo=((7,0),(7,3))
    elif piece=='♚' and sc==4:
        has_moved['black_king']=True
        if ec==6: board[0][5],board[0][7]=board[0][7],'.'; rook_undo=((0,7),(0,5))
        if ec==2: board[0][3],board[0][0]=board[0][0],'.'; rook_undo=((0,0),(0,3))
    if piece=='♖':
        if sr==7 and sc==0: has_moved['white_rook_a']=True
        if sr==7 and sc==7: has_moved['white_rook_h']=True
    elif piece=='♜':
        if sr==0 and sc==0: has_moved['black_rook_a']=True
        if sr==0 and sc==7: has_moved['black_rook_h']=True

    board[er][ec]=piece; board[sr][sc]='.'
    promoted = None
    if piece=='♙' and er==0: board[er][ec]='♕'; promoted='♕'
    if piece=='♟' and er==7: board[er][ec]='♛'; promoted='♛'

    return (sr,sc,er,ec,piece,captured,ep_save,hm_save,
            ep_cap_pos,ep_cap_piece,rook_undo,promoted)

def undo_move(bundle):
    global en_passant_target, has_moved
    sr,sc,er,ec,piece,captured,ep_save,hm_save, \
        ep_cap_pos,ep_cap_piece,rook_undo,promoted = bundle
    en_passant_target = ep_save
    has_moved = hm_save
    board[sr][sc] = piece
    board[er][ec] = captured
    if ep_cap_pos:
        board[ep_cap_pos[0]][ep_cap_pos[1]] = ep_cap_piece
    if rook_undo:
        orig_pos, moved_pos = rook_undo
        board[orig_pos[0]][orig_pos[1]] = board[moved_pos[0]][moved_pos[1]]
        board[moved_pos[0]][moved_pos[1]] = '.'


# ═══════════════════════════════════════════
# STATIC EVALUATION
# ═══════════════════════════════════════════

def static_eval():
    score = 0
    endgame = _is_endgame()
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

    # Pawn structure
    for f in set(wpf):
        if wpf.count(f) > 1:  score -= 30 * (wpf.count(f)-1)
        if not any(af in wpf for af in [f-1,f+1]): score -= 20
    for f in set(bpf):
        if bpf.count(f) > 1:  score += 30 * (bpf.count(f)-1)
        if not any(af in bpf for af in [f-1,f+1]): score += 20

    # Rook open files
    for c in range(8):
        col = [board[r][c] for r in range(8) if board[r][c]!='.']
        hwp='♙' in col; hbp='♟' in col
        for r in range(8):
            p = board[r][c]
            if p=='♖':   score += 30 if not hwp and not hbp else (15 if not hwp else 0)
            elif p=='♜': score -= 30 if not hwp and not hbp else (15 if not hbp else 0)

    # RL learned knowledge blended in (scaled to centipawns)
    score += int(learned_values.get(board_key(), 0) * 100)
    return score


# ═══════════════════════════════════════════
# MOVE ORDERING
# ═══════════════════════════════════════════

def order_moves(moves, tt_move=None):
    def priority(m):
        if m == tt_move: return 200_000
        sr,sc,er,ec = m
        victim   = board[er][ec]
        attacker = board[sr][sc]
        if victim != '.':
            # MVV-LVA
            return 10_000 + abs(PIECE_VALUES.get(victim,0)) - abs(PIECE_VALUES.get(attacker,0))//10
        # Quiet move: PST delta
        is_wp = attacker in WHITE_PIECES
        tr_from = sr if is_wp else (7-sr)
        tr_to   = er if is_wp else (7-er)
        tbl = PST.get(attacker)
        return (tbl[tr_to][ec] - tbl[tr_from][sc]) if tbl else 0

    moves.sort(key=priority, reverse=True)
    return moves


# ═══════════════════════════════════════════
# ALPHA-BETA  (negamax + TT)
# ═══════════════════════════════════════════

def negamax(depth, alpha, beta, color):
    """
    Negamax alpha-beta with transposition table.
    color: +1 = White to move, -1 = Black to move.
    Returns score from the perspective of the side to move.
    """
    orig_alpha = alpha
    key = board_key()

    # TT probe
    if key in tt:
        td, flag, ts, tm = tt[key]
        if td >= depth:
            if flag == 'exact':  return ts
            if flag == 'lower':  alpha = max(alpha, ts)
            elif flag == 'upper': beta = min(beta, ts)
            if alpha >= beta:    return ts

    cur_color_name = 'white' if color == 1 else 'black'
    moves = get_all_valid_moves(cur_color_name)

    if not moves:
        king_sym    = '♔' if color == 1 else '♚'
        enemy_color = 'black' if color == 1 else 'white'
        kp = next(((r,c) for r in range(8) for c in range(8) if board[r][c]==king_sym), None)
        if kp and is_square_attacked(kp[0], kp[1], enemy_color):
            return -INF + (100 - depth)  # checkmate; prefer quicker mates
        return 0  # stalemate

    if depth == 0:
        return color * static_eval()

    tt_move = tt[key][3] if key in tt else None
    moves = order_moves(moves, tt_move)

    best_score = -INF
    best_move  = moves[0]

    for m in moves:
        bnd = apply_move(*m)
        score = -negamax(depth-1, -beta, -alpha, -color)
        undo_move(bnd)

        if score > best_score:
            best_score, best_move = score, m

        alpha = max(alpha, score)
        if alpha >= beta:
            break  # β cutoff

    # TT store
    if len(tt) < TT_MAX:
        flag = ('exact'  if orig_alpha < best_score < beta else
                'lower'  if best_score >= beta else
                'upper')
        tt[key] = (depth, flag, best_score, best_move)

    return best_score


def find_best_move(max_depth=8, time_limit=12.0):
    """Iterative deepening: search depth 1→max_depth, stop on time limit."""
    best_move = None
    start = time.time()

    moves = get_all_valid_moves('white')
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
        elapsed = time.time() - start
        print(f"  depth={depth}  score={iter_best_score:+d}  "
              f"move={best_move}  t={elapsed:.2f}s  TT={len(tt)}")

        if elapsed > time_limit:
            print(f"  [time limit hit at depth {depth}]")
            break

    return best_move


# ═══════════════════════════════════════════
# EXECUTE MOVE  (real game, with GUI state)
# ═══════════════════════════════════════════

def execute_move(sr, sc, er, ec):
    global en_passant_target
    piece = board[sr][sc]

    if piece in {'♙','♟'} and (er,ec)==en_passant_target:
        board[sr][ec] = '.'

    en_passant_target = None
    if piece=='♙' and sr==6 and er==4: en_passant_target=(5,sc)
    if piece=='♟' and sr==1 and er==3: en_passant_target=(2,sc)

    if piece=='♔' and sc==4:
        has_moved['white_king']=True
        if ec==6: board[7][5],board[7][7]=board[7][7],'.'
        if ec==2: board[7][3],board[7][0]=board[7][0],'.'
    elif piece=='♚' and sc==4:
        has_moved['black_king']=True
        if ec==6: board[0][5],board[0][7]=board[0][7],'.'
        if ec==2: board[0][3],board[0][0]=board[0][0],'.'

    if piece=='♖':
        if sr==7 and sc==0: has_moved['white_rook_a']=True
        if sr==7 and sc==7: has_moved['white_rook_h']=True
    elif piece=='♜':
        if sr==0 and sc==0: has_moved['black_rook_a']=True
        if sr==0 and sc==7: has_moved['black_rook_h']=True

    board[er][ec]=piece; board[sr][sc]='.'
    if piece=='♙' and er==0: board[er][ec]='♕'
    if piece=='♟' and er==7: board[er][ec]='♛'


# ═══════════════════════════════════════════
# BOT THREAD
# ═══════════════════════════════════════════

def bot_think_thread():
    global bot_thinking, bot_result_move
    bot_thinking = True
    print("[Bot] Thinking…")
    move = find_best_move(max_depth=8, time_limit=12.0)
    bot_result_move = move
    bot_thinking = False
    print(f"[Bot] Chose {move}")


# ═══════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════

pygame.init()
load_knowledge()
WIDTH, SQ = 600, 75
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Chess — You (Black) vs Bot (White) | Depth 8")
FONT    = pygame.font.SysFont("segoeuisymbol", 50)
FONT_SM = pygame.font.SysFont("segoeuisymbol", 20)
CLK     = pygame.time.Clock()


def draw_board(sel, hints):
    for r in range(8):
        for c in range(8):
            col = (240,217,181) if (r+c)%2==0 else (181,136,99)
            pygame.draw.rect(screen, col, (c*SQ, r*SQ, SQ, SQ))
            if sel==(r,c):
                pygame.draw.rect(screen,(255,255,0),(c*SQ,r*SQ,SQ,SQ),4)
            if (r,c) in hints:
                pygame.draw.circle(screen,(50,200,50),(c*SQ+SQ//2,r*SQ+SQ//2),12)
            p = board[r][c]
            if p != '.':
                screen.blit(FONT.render(p,True,(0,0,0)),(c*SQ+8,r*SQ+2))

    if bot_thinking:
        overlay = pygame.Surface((WIDTH,28), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        screen.blit(overlay,(0,WIDTH-28))
        screen.blit(FONT_SM.render("  ♟ Bot thinking (depth 8)…",True,(255,220,50)),(0,WIDTH-26))


def main():
    global current_turn, bot_result_move

    sel, hints  = None, []
    bot_started = False

    while True:
        CLK.tick(30)

        # Start bot thread once on White's turn
        if current_turn=='white' and not bot_thinking and not bot_started and bot_result_move is None:
            t = threading.Thread(target=bot_think_thread, daemon=True)
            t.start()
            bot_started = True

        # Collect finished bot move
        if current_turn=='white' and not bot_thinking and bot_result_move is not None:
            execute_move(*bot_result_move)
            tt.clear()          # position changed; flush TT
            bot_result_move = None
            bot_started     = False
            current_turn    = 'black'

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and current_turn=='black':
                c = event.pos[0]//SQ
                r = event.pos[1]//SQ
                if 0<=r<8 and 0<=c<8:
                    if (r,c) in hints:
                        execute_move(sel[0], sel[1], r, c)
                        tt.clear()
                        current_turn = 'white'
                        sel, hints = None, []
                    elif is_black_piece(board[r][c]):
                        sel = (r,c)
                        hints = [(m[2],m[3]) for m in get_all_valid_moves('black')
                                 if m[0]==r and m[1]==c]
                    else:
                        sel, hints = None, []

        draw_board(sel, hints)
        pygame.display.flip()


if __name__ == "__main__":
    main()
