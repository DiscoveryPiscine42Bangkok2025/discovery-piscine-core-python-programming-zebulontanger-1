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
    return moves

def select_best_move(curr_board, turn, depth=1):
    moves = get_all_moves(curr_board, turn)
    if not moves: return None
    
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

def run_training_session(games=10):
    global board
    load_brain()
    for _ in range(games):
        board = get_initial_board()
        history = []
        turn = 'white'
        for _ in range(100):
            move = select_best_move(board, turn)
            if not move: break
            board[move[2]][move[3]], board[move[0]][move[1]] = board[move[0]][move[1]], '.'
            history.append(get_state_key(board))
            turn = 'black' if turn == 'white' else 'white'
        
        final_eval = evaluate_board(board)
        for state in history:
            old_val = learned_values.get(state, 0)
            learned_values[state] = (old_val * (1 - LEARNING_RATE)) + (final_eval * LEARNING_RATE)
    save_brain()

def play_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("segoeuisymbol", 50)
    load_brain()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        for r in range(8):
            for c in range(8):
                color = WHITE if (r + c) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                p = board[r][c]
                if p != '.':
                    img = font.render(p, True, (0,0,0))
                    screen.blit(img, (c*SQ_SIZE + 10, r*SQ_SIZE))
        
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    play_game()
