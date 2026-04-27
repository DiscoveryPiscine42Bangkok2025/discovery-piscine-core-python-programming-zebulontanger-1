import random
import pickle

# --- SETTINGS ---
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95  # How much the bot values future rewards
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

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
            
            # Movement logic for all pieces
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
                for dc in [-1, 1]:
                    if r > 0 and 0 <= c+dc < 8 and board[r-1][c+dc] in BLACK_PIECES: moves.append((r,c,r-1,c+dc))
            elif p == '♟':
                if r < 7 and board[r+1][c] == '.': moves.append((r,c,r+1,c))
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

def evaluate_board(board, state_key=None):
    if not state_key: state_key = get_state_key(board)
    material = sum(PIECE_VALUES.get(board[r][c], 0) for r in range(8) for c in range(8))
    knowledge = learned_values.get(state_key, 0)
    return material + knowledge

def select_move(board, turn, epsilon):
    moves = get_all_moves(board, turn)
    if not moves: return None

    # EXPLORATION: Play randomly based on epsilon
    if random.random() < epsilon:
        return random.choice(moves)

    # EXPLOITATION: Stick to what was learned
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
    # Epsilon starts high (random) and decays as the bot learns
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
                # DRAW PUNISHMENT: If the game ends in a stalemate/no moves
                result_score = -5 
                game_over = True
                break
            
            # Execute
            board[move[2]][move[3]], board[move[0]][move[1]] = board[move[0]][move[1]], '.'
            state_key = get_state_key(board)
            history.append(state_key)

            # Check if King was captured (Simple win condition)
            flat_board = "".join(["".join(row) for row in board])
            if '♔' not in flat_board:
                result_score = -50 # Black wins
                game_over = True
                break
            if '♚' not in flat_board:
                result_score = 50 # White wins
                game_over = True
                break

            turn = 'black' if turn == 'white' else 'white'

        # If game went to 150 moves without a winner, punish as a draw
        if not game_over:
            result_score = -10

        # BACKPROPAGATION: Learn from the result
        for i, state in enumerate(reversed(history)):
            reward = result_score * (DISCOUNT_FACTOR ** i)
            old_val = learned_values.get(state, 0)
            learned_values[state] = old_val + LEARNING_RATE * (reward - old_val)

        if (g + 1) % 50 == 0:
            print(f"Game {g+1} | Positions in Brain: {len(learned_values)}")
            save_brain()
            epsilon = max(0.1, epsilon * 0.99) # Become less random over time

    save_brain()

if __name__ == "__main__":
    run_self_play_training(2000)
