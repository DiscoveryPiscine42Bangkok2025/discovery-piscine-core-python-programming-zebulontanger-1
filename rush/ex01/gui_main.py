import pygame
import random
import pickle
import sys

# --- PIECE SETS ---
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

# --- POSITIONAL TABLES (White's perspective; flip row for Black) ---
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

# --- BOARD STATE ---
board = [
    ['♜','♞','♝','♛','♚','♝','♞','♜'],
    ['♟','♟','♟','♟','♟','♟','♟','♟'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['♙','♙','♙','♙','♙','♙','♙','♙'],
    ['♖','♘','♗','♕','♔','♗','♘','♖']
]
has_moved = {
    'white_king': False, 'black_king': False,
    'white_rook_a': False, 'white_rook_h': False,
    'black_rook_a': False, 'black_rook_h': False
}
en_passant_target = None
current_turn = 'white'
learned_values = {}


def get_state_key():
    return "".join(["".join(row) for row in board])

def load_knowledge():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
    except:
        learned_values = {}

def is_white_piece(p): return p in WHITE_PIECES
def is_black_piece(p): return p in BLACK_PIECES


# --- POSITIONAL EVALUATION HELPERS ---

def _is_endgame():
    pieces = [p for row in board for p in row if p != '.']
    queens = [p for p in pieces if p in {'♕','♛'}]
    return len(queens) == 0 or len(pieces) <= 12

def _can_attack_sq(fr, fc, tr, tc):
    """Can piece at (fr,fc) capture square (tr,tc)?"""
    p = board[fr][fc]
    if p == '.': return False
    dr, dc = tr - fr, tc - fc
    if p in {'♘','♞'}: return (abs(dr), abs(dc)) in {(2,1),(1,2)}
    if p in {'♔','♚'}: return abs(dr) <= 1 and abs(dc) <= 1
    if p == '♙': return dr == -1 and abs(dc) == 1
    if p == '♟': return dr == 1 and abs(dc) == 1
    if p in {'♖','♜','♕','♛'} and (dr == 0 or dc == 0):
        sr = 0 if dr == 0 else (1 if dr > 0 else -1)
        sc = 0 if dc == 0 else (1 if dc > 0 else -1)
        nr, nc = fr+sr, fc+sc
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += sr; nc += sc
        return True
    if p in {'♗','♝','♕','♛'} and abs(dr) == abs(dc):
        sr = 1 if dr > 0 else -1
        sc = 1 if dc > 0 else -1
        nr, nc = fr+sr, fc+sc
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += sr; nc += sc
        return True
    return False

def get_positional_score():
    """
    Rich heuristic covering:
    1. Material
    2. Piece-square tables (center control, good squares)
    3. King safety (mid-game vs endgame)
    4. Pawn structure (doubled / isolated penalties)
    5. Rook open files
    6. Hanging piece penalty
    """
    score = 0.0
    endgame = _is_endgame()
    white_pawn_files, black_pawn_files = [], []

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue

            score += PIECE_VALUES.get(p, 0)
            is_wp = p in WHITE_PIECES
            tr = r if is_wp else (7 - r)
            sign = 1 if is_wp else -1

            if p in {'♙','♟'}:
                score += sign * PAWN_TABLE[tr][c]
                (white_pawn_files if is_wp else black_pawn_files).append(c)
            elif p in {'♘','♞'}: score += sign * KNIGHT_TABLE[tr][c]
            elif p in {'♗','♝'}: score += sign * BISHOP_TABLE[tr][c]
            elif p in {'♖','♜'}: score += sign * ROOK_TABLE[tr][c]
            elif p in {'♕','♛'}: score += sign * QUEEN_TABLE[tr][c]
            elif p in {'♔','♚'}:
                kt = KING_TABLE_END if endgame else KING_TABLE_MID
                score += sign * kt[tr][c]

    # Pawn structure
    for f in set(white_pawn_files):
        cnt = white_pawn_files.count(f)
        if cnt > 1: score -= 0.3 * (cnt - 1)
        if not any(af in white_pawn_files for af in [f-1, f+1]): score -= 0.2
    for f in set(black_pawn_files):
        cnt = black_pawn_files.count(f)
        if cnt > 1: score += 0.3 * (cnt - 1)
        if not any(af in black_pawn_files for af in [f-1, f+1]): score += 0.2

    # Rook open files
    for c in range(8):
        col = [board[r][c] for r in range(8) if board[r][c] != '.']
        hwp = '♙' in col; hbp = '♟' in col
        for r in range(8):
            p = board[r][c]
            if p == '♖':
                score += 0.3 if not hwp and not hbp else (0.15 if not hwp else 0)
            elif p == '♜':
                score -= 0.3 if not hwp and not hbp else (0.15 if not hbp else 0)

    # Hanging piece penalty
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            is_wp = p in WHITE_PIECES
            atk_pieces = BLACK_PIECES if is_wp else WHITE_PIECES
            for ar in range(8):
                for ac in range(8):
                    if board[ar][ac] in atk_pieces and _can_attack_sq(ar, ac, r, c):
                        penalty = abs(PIECE_VALUES.get(p, 0)) * 0.05
                        score += penalty if not is_wp else -penalty
                        break

    return score


# --- CHESS LOGIC ---

def is_square_attacked(r, c, attacker_color):
    for ar in range(8):
        for ac in range(8):
            p = board[ar][ac]
            if (attacker_color == 'white' and p in WHITE_PIECES) or \
               (attacker_color == 'black' and p in BLACK_PIECES):
                moves = get_piece_pseudo_moves(ar, ac, ignore_en_passant=True)
                for _, _, tr, tc in moves:
                    if tr == r and tc == c: return True
    return False

def get_piece_pseudo_moves(r, c, ignore_en_passant=False):
    p = board[r][c]
    moves = []
    is_white = is_white_piece(p)
    enemy = BLACK_PIECES if is_white else WHITE_PIECES
    friendly = WHITE_PIECES if is_white else BLACK_PIECES

    if p in {'♖','♜','♕','♛','♗','♝'}:
        dirs = []
        if p in {'♖','♜','♕','♛'}: dirs += [(0,1),(0,-1),(1,0),(-1,0)]
        if p in {'♗','♝','♕','♛'}: dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while 0<=nr<8 and 0<=nc<8:
                if board[nr][nc] == '.': moves.append((r,c,nr,nc))
                elif board[nr][nc] in enemy: moves.append((r,c,nr,nc)); break
                else: break
                nr, nc = nr+dr, nc+dc
    elif p in {'♘','♞'}:
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly:
                moves.append((r,c,nr,nc))
    elif p in {'♔','♚'}:
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly:
                moves.append((r,c,nr,nc))
    elif p == '♙':
        if r > 0 and board[r-1][c] == '.':
            moves.append((r,c,r-1,c))
            if r == 6 and board[r-2][c] == '.': moves.append((r,c,r-2,c))
        for dc in [-1,1]:
            if r > 0 and 0 <= c+dc < 8:
                if board[r-1][c+dc] in enemy: moves.append((r,c,r-1,c+dc))
                if not ignore_en_passant and (r-1,c+dc) == en_passant_target:
                    moves.append((r,c,r-1,c+dc))
    elif p == '♟':
        if r < 7 and board[r+1][c] == '.':
            moves.append((r,c,r+1,c))
            if r == 1 and board[r+2][c] == '.': moves.append((r,c,r+2,c))
        for dc in [-1,1]:
            if r < 7 and 0 <= c+dc < 8:
                if board[r+1][c+dc] in enemy: moves.append((r,c,r+1,c+dc))
                if not ignore_en_passant and (r+1,c+dc) == en_passant_target:
                    moves.append((r,c,r+1,c+dc))
    return moves

def get_all_valid_moves(color):
    all_pseudo = []
    for r in range(8):
        for c in range(8):
            if (color=='white' and is_white_piece(board[r][c])) or \
               (color=='black' and is_black_piece(board[r][c])):
                all_pseudo.extend(get_piece_pseudo_moves(r, c))
    valid = []
    enemy_color = 'black' if color == 'white' else 'white'
    for m in all_pseudo:
        sr, sc, er, ec = m
        orig_p, dest_p = board[sr][sc], board[er][ec]
        board[er][ec], board[sr][sc] = orig_p, '.'
        king_p = None
        for r in range(8):
            for c in range(8):
                if board[r][c] == ('♔' if color=='white' else '♚'): king_p = (r,c)
        if king_p and not is_square_attacked(king_p[0], king_p[1], enemy_color):
            valid.append(m)
        board[sr][sc], board[er][ec] = orig_p, dest_p

    # Castling
    if color == 'white' and not has_moved['white_king']:
        if not has_moved['white_rook_h'] and board[7][5]=='.' and board[7][6]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,5,6]): valid.append((7,4,7,6))
        if not has_moved['white_rook_a'] and board[7][1]=='.' and board[7][2]=='.' and board[7][3]=='.' and \
           not any(is_square_attacked(7,x,'black') for x in [4,3,2]): valid.append((7,4,7,2))
    elif color == 'black' and not has_moved['black_king']:
        if not has_moved['black_rook_h'] and board[0][5]=='.' and board[0][6]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,5,6]): valid.append((0,4,0,6))
        if not has_moved['black_rook_a'] and board[0][1]=='.' and board[0][2]=='.' and board[0][3]=='.' and \
           not any(is_square_attacked(0,x,'white') for x in [4,3,2]): valid.append((0,4,0,2))
    return valid

def execute_move(sr, sc, er, ec):
    global en_passant_target
    piece = board[sr][sc]
    if (piece=='♙' or piece=='♟') and (er,ec)==en_passant_target:
        board[sr][ec] = '.'
    en_passant_target = None
    if piece=='♙' and sr==6 and er==4: en_passant_target=(5,sc)
    if piece=='♟' and sr==1 and er==3: en_passant_target=(2,sc)
    if piece=='♔' and sc==4:
        if ec==6: board[7][5],board[7][7]=board[7][7],'.'
        if ec==2: board[7][3],board[7][0]=board[7][0],'.'
        has_moved['white_king']=True
    elif piece=='♚' and sc==4:
        if ec==6: board[0][5],board[0][7]=board[0][7],'.'
        if ec==2: board[0][3],board[0][0]=board[0][0],'.'
        has_moved['black_king']=True
    if piece=='♖':
        if sr==7 and sc==0: has_moved['white_rook_a']=True
        if sr==7 and sc==7: has_moved['white_rook_h']=True
    elif piece=='♜':
        if sr==0 and sc==0: has_moved['black_rook_a']=True
        if sr==0 and sc==7: has_moved['black_rook_h']=True
    board[er][ec], board[sr][sc] = piece, '.'
    if piece=='♙' and er==0: board[er][ec]='♕'
    if piece=='♟' and er==7: board[er][ec]='♛'


# --- GUI ---
pygame.init()
load_knowledge()
WIDTH, SQ_SIZE = 600, 600 // 8
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Chess: You (Black) vs Bot (White)")
FONT = pygame.font.SysFont("segoeuisymbol", 50)

def draw_board(selected_sq, valid_moves):
    for r in range(8):
        for c in range(8):
            color = (240,217,181) if (r+c)%2==0 else (181,136,99)
            pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if selected_sq == (r,c):
                pygame.draw.rect(screen, (255,255,0), (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
            if (r,c) in valid_moves:
                pygame.draw.circle(screen, (0,255,0), (c*SQ_SIZE+SQ_SIZE//2, r*SQ_SIZE+SQ_SIZE//2), 10)
            piece = board[r][c]
            if piece != '.':
                screen.blit(FONT.render(piece, True, (0,0,0)), (c*SQ_SIZE+10, r*SQ_SIZE))

def bot_move():
    moves = get_all_valid_moves('white')
    if not moves: return False

    epsilon = 0.2
    if random.random() < epsilon:
        best_move = random.choice(moves)
    else:
        # --- Sort candidates: captures & checks first (Checklist item 3 & 8) ---
        def move_priority(m):
            dest = board[m[2]][m[3]]
            return abs(PIECE_VALUES.get(dest, 0)) * 2  # captures score higher

        moves.sort(key=move_priority, reverse=True)

        best_score, best_move = -99999, random.choice(moves)
        for m in moves:
            orig, dest = board[m[0]][m[1]], board[m[2]][m[3]]
            board[m[2]][m[3]], board[m[0]][m[1]] = orig, '.'

            # Rich positional score + learned experience
            score = get_positional_score()
            score += learned_values.get(get_state_key(), 0)

            if score > best_score:
                best_score, best_move = score, m
            board[m[0]][m[1]], board[m[2]][m[3]] = orig, dest

    execute_move(*best_move)
    return True

def main():
    global current_turn
    sel_sq, val_moves = None, []
    while True:
        if current_turn == 'white':
            pygame.time.delay(500)
            if not bot_move(): print("Game Over!")
            current_turn = 'black'
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and current_turn == 'black':
                c, r = event.pos[0]//SQ_SIZE, event.pos[1]//SQ_SIZE
                if (r,c) in val_moves:
                    execute_move(sel_sq[0], sel_sq[1], r, c)
                    current_turn = 'white'
                    sel_sq, val_moves = None, []
                elif is_black_piece(board[r][c]):
                    sel_sq = (r,c)
                    val_moves = [(m[2],m[3]) for m in get_all_valid_moves('black') if m[0]==r and m[1]==c]
        draw_board(sel_sq, val_moves)
        pygame.display.flip()

if __name__ == "__main__": main()
