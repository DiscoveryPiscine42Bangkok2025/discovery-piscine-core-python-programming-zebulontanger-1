import random
import pickle

total_games = 1000
save_interval = 10

PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}

try:
    with open("bot_brain.pkl", 'rb') as f:
        learned_values = pickle.load(f)
except:
    learned_values = {}

print("Brain loaded. Positions known:", len(learned_values))

for game_num in range(total_games):
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
    current_turn = 'white'
    bot_is_white = random.choice([True, False])
    game_history = []

    for move_count in range(150):
        all_moves = []
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if (current_turn == 'white' and piece in WHITE_PIECES) or \
                   (current_turn == 'black' and piece in BLACK_PIECES):
                    
                    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 8 and 0 <= nc < 8:
                            target = board[nr][nc]
                            if target == '.' or \
                               (current_turn == 'white' and target in BLACK_PIECES) or \
                               (current_turn == 'black' and target in WHITE_PIECES):
                                all_moves.append((r, c, nr, nc))

        if not all_moves:
            break

        is_bot_acting = (current_turn == 'white' and bot_is_white) or \
                        (current_turn == 'black' and not bot_is_white)

        if is_bot_acting and random.random() > 0.3:
            best_move = all_moves[0]
            best_score = -9999 if current_turn == 'white' else 9999
            
            for m in all_moves:
                orig_p, dest_p = board[m[0]][m[1]], board[m[2]][m[3]]
                board[m[2]][m[3]], board[m[0]][m[1]] = orig_p, '.'
                
                current_score = sum(PIECE_VALUES.get(board[row][col], 0) for row in range(8) for col in range(8))
                state_key = "".join("".join(row) for row in board)
                current_score += learned_values.get(state_key, 0)

                if (current_turn == 'white' and current_score > best_score) or \
                   (current_turn == 'black' and current_score < best_score):
                    best_score, best_move = current_score, m
                
                board[m[0]][m[1]], board[m[2]][m[3]] = orig_p, dest_p
            move = best_move
        else:
            move = random.choice(all_moves)

        sr, sc, er, ec = move
        board[er][ec], board[sr][sc] = board[sr][sc], '.'
        
        game_history.append("".join("".join(row) for row in board))
        
        current_turn = 'black' if current_turn == 'white' else 'white'

    final_eval = sum(PIECE_VALUES.get(board[row][col], 0) for row in range(8) for col in range(8))
    for state in game_history:
        if state in learned_values:
            learned_values[state] = (learned_values[state] + final_eval) / 2
        else:
            learned_values[state] = final_eval

    if (game_num + 1) % save_interval == 0:
        print(f"Game {game_num + 1}/{total_games} finished. Positions known: {len(learned_values)}")

with open("bot_brain.pkl", 'wb') as f:
    pickle.dump(learned_values, f)

print("Training session finished. Brain saved.")
