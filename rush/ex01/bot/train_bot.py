import chess_game
import random

def train(num_games=2500):
    print("--- Starting Balanced Bot Training ---")
    chess_game.load_knowledge()
    
    for i in range(num_games):
        game_history = []
        
        # --- RESET BOARD ---
        chess_game.board = [
            ['♜','♞','♝','♛','♚','♝','♞','♜'], ['♟','♟','♟','♟','♟','♟','♟','♟'],
            ['.','.','.','.','.','.','.','.'], ['.','.','.','.','.','.','.','.'],
            ['.','.','.','.','.','.','.','.'], ['.','.','.','.','.','.','.','.'],
            ['♙','♙','♙','♙','♙','♙','♙','♙'], ['♖','♘','♗','♕','♔','♗','♘','♖']
        ]
        chess_game.current_turn = 'white'
        chess_game.move_history = []
        chess_game.moved_pieces = set()
        
        # --- ASSIGN ROLES FOR THIS GAME ---
        # 50% chance the Bot is White, 50% chance Bot is Black
        bot_is_white = random.choice([True, False])
        
        for move_count in range(200):
            moves = chess_game.get_all_valid_moves(chess_game.current_turn)
            if not moves:
                # Game end logic
                res = 0.5 # Draw
                if chess_game.in_check('white'): res = 0 # Black wins
                elif chess_game.in_check('black'): res = 1 # White wins
                chess_game.update_learning(game_history, res)
                break
            
            # --- MOVE SELECTION ---
            # Check if it is currently the Bot's turn to be "Smart"
            is_bot_turn = (chess_game.current_turn == 'white' and bot_is_white) or \
                          (chess_game.current_turn == 'black' and not bot_is_white)

            if is_bot_turn:
                # Bot uses learning + Minimax to pick the best move
                # 30% exploration within the bot's turn to discover new variations
                if random.random() < 0.3:
                    move = random.choice(moves)
                else:
                    _, move = chess_game.minimax(1, -1000, 1000, chess_game.current_turn == 'black')
            else:
                # Opponent turn: plays a purely random move to challenge the bot
                move = random.choice(moves)

            if move:
                chess_game.execute_move(move[0], move[1], move[2], move[3])
                game_history.append(chess_game.get_state_key())
                chess_game.current_turn = 'black' if chess_game.current_turn == 'white' else 'white'
            else:
                break

        # Progress Updates and Saving
        if (i + 1) % 10 == 0:
            print(f" > Games: {i + 1}/{num_games} | Brain size: {len(chess_game.learned_values)}")
            chess_game.save_knowledge()

if __name__ == "__main__":
    train()
