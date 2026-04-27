import pygame
import random
import pickle

WIDTH, HEIGHT = 600, 600
SQ_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
LEARNING_RATE = 0.1

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

board = get_initial_board()
learned_values = {}

def load_brain():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
    except FileNotFoundError:
        learned_values = {}

def save_brain():
    with open("bot_brain.pkl", 'wb') as f:
        pickle.dump(learned_values, f)

def get_state_key(curr_board):
    return "".join(["".join(row) for row in curr_board])

def evaluate_board(curr_board):
    score = sum(PIECE_VALUES.get(curr_board[r][c], 0) for r in range(8) for c in range(8))
    state_key = get_state_key(curr_board)
    score += learned_values.get(state_key, 0)
    return score + random.uniform(-0.05, 0.05)

def get_all_moves(curr_board, turn):
    moves = []
    is_white = (turn == 'white')
    for r in range(8):
        for c in range(8):
            p = curr_board[r][c]
            if p == '.' or (is_white and p not in PIECE_VALUES) or (not is_white and p in PIECE_VALUES):
                continue
            # Simplified valid move generation
            directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    moves.append((r, c, nr, nc))
    return moves

def select_best_move(curr_board, turn, move_count=0):
    moves = get_all_moves(curr_board, turn)
    if not moves: return None

    if move_count == 0:
        if turn == 'white':
            openings = [(6, 4, 4, 4), (6, 3, 4, 3), (6, 2, 4, 2)]
        else:
            openings = [(1, 4, 3, 4), (1, 3, 3, 3), (1, 2, 3, 2)]
        valid_openings = [m for m in moves if m in openings]
        if valid_openings:
            return random.choice(valid_openings)

    scored_moves = []
    for m in moves:
        sr, sc, er, ec = m
        orig_p, dest_p = curr_board[sr][sc], curr_board[er][ec]
        curr_board[er][ec], curr_board[sr][sc] = orig_p, '.'
        move_score = evaluate_board(curr_board)
        scored_moves.append((move_score, m))
        curr_board[sr][sc], curr_board[er][ec] = orig_p, dest_p
        
    scored_moves.sort(key=lambda x: x[0], reverse=(turn == 'white'))
    top_n = min(3, len(scored_moves))
    return random.choice(scored_moves[:top_n])[1]

def refresh_brain():
    global learned_values
    cleaned_brain = {k: v for k, v in learned_values.items() if abs(v) > 0.01}
    for key in cleaned_brain:
        if cleaned_brain[key] > 100: cleaned_brain[key] = 100
        if cleaned_brain[key] < -100: cleaned_brain[key] = -100
    learned_values = cleaned_brain
    save_brain()

def run_training_session(games=100):
    global board
    load_brain()
    print(f"Starting training session: {games} games...")
    for i in range(games):
        board = get_initial_board()
        history = []
        turn = 'white'
        for m_count in range(100):
            move = select_best_move(board, turn, m_count)
            if not move: break
            board[move[2]][move[3]], board[move[0]][move[1]] = board[move[0]][move[1]], '.'
            history.append(get_state_key(board))
            turn = 'black' if turn == 'white' else 'white'
        
        final_eval = evaluate_board(board)
        for state in history:
            old_val = learned_values.get(state, 0)
            learned_values[state] = (old_val * (1 - LEARNING_RATE)) + (final_eval * LEARNING_RATE)
        
        if (i + 1) % 10 == 0:
            print(f"Game {i+1} complete. Brain size: {len(learned_values)}")
            save_brain()
            
    refresh_brain()
    print("Training complete and memory refreshed.")

if __name__ == "__main__":
    run_training_session(100)
