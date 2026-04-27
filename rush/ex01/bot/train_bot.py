import chess_game
import random

# welcome to my unfinished project
# what i'm trying to make here is a reinforced learning chess bot :)

def train(num_games=2500):
    print(f"--- Starting Hybrid Training: {num_games} Games ---")
    chess_game.load_knowledge()
    
    for i in range(num_games):
        game_history = []
        
        chess_game.board = [
            ['♜','♞','♝','♛','♚','♝','♞','♜'], ['♟','♟','♟','♟','♟','♟','♟','♟'],
            ['.','.','.','.','.','.','.','.'], ['.','.','.','.','.','.','.','.'],
            ['.','.','.','.','.','.','.','.'], ['.','.','.','.','.','.','.','.'],
            ['♙','♙','♙','♙','♙','♙','♙','♙'], ['♖','♘','♗','♕','♔','♗','♘','♖']
        ]
        chess_game.current_turn = 'white'
        chess_game.move_history = []
        chess_game.moved_pieces = set()
        
        # 70% Balanced (Random Opponent), 30% Self-Play (Bot vs Bot)
        is_self_play = random.random() < 0.3
        bot_is_white = random.choice([True, False])
        
        for move_count in range(200):
            moves = chess_game.get_all_valid_moves(chess_game.current_turn)
            if not moves:
                res = 0.5
                if chess_game.in_check('white'): res = 0
                elif chess_game.in_check('black'): res = 1
                chess_game.update_learning(game_history, res)
                break
            
            is_bot_acting = False
            if is_self_play:
                is_bot_acting = True # Both sides are smart
            else:
                is_bot_acting = (chess_game.current_turn == 'white' and bot_is_white) or \
                                (chess_game.current_turn == 'black' and not bot_is_white)

            if is_bot_acting
                # exploration rate: 0.4
                if random.random() < 0.4:
                    move = random.choice(moves)
                else:
                    _, move = chess_game.minimax(1, -1000, 1000, chess_game.current_turn == 'black')
            else:
                # Random opponent logic
                move = random.choice(moves)

            if move:
                chess_game.execute_move(move[0], move[1], move[2], move[3])
                game_history.append(chess_game.get_state_key())
                chess_game.current_turn = 'black' if chess_game.current_turn == 'white' else 'white'
            else:
                break

        # progress updating
        if (i + 1) % 50 == 0:
            mode_text = "Self-Play" if is_self_play else "Balanced"
            print(f"Game {i+1}/{num_games} completed ({mode_text}). Positions known: {len(chess_game.learned_values)}")
            chess_game.save_knowledge()

    # Final Save
    chess_game.save_knowledge()
    print(f"Training Complete! Total unique positions: {len(chess_game.learned_values)}")

if __name__ == "__main__":
    # amount of times to run
    train(2500)
