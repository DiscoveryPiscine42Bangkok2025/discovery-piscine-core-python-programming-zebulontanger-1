import pygame
import chess_game
import sys

pygame.init()
chess_game.load_knowledge()

WIDTH, HEIGHT = 600, 600
SQ_SIZE = WIDTH // 8
FONT = pygame.font.SysFont("segoeuisymbol", 50)
RESULT_FONT = pygame.font.SysFont("arial", 40, bold=True)

def draw_board(screen, selected, valid_moves):
    for r in range(8):
        for c in range(8):
            color = (240, 217, 181) if (r + c) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if selected == (r, c):
                pygame.draw.rect(screen, (255, 255, 0), (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 5)
            if (r, c) in valid_moves:
                pygame.draw.circle(screen, (100, 200, 100), (c * SQ_SIZE + SQ_SIZE//2, r * SQ_SIZE + SQ_SIZE//2), 10)
            p = chess_game.board[r][c]
            if p != '.':
                text = FONT.render(p, True, (0, 0, 0))
                screen.blit(text, (c * SQ_SIZE + 10, r * SQ_SIZE))

def check_for_game_end(history):
    moves = chess_game.get_all_valid_moves(chess_game.current_turn)
    if not moves:
        res = 0.5 
        message = "Draw!"
        if chess_game.in_check('white'): 
            res = 0 # Black wins
            message = "You Win (Black)!"
        elif chess_game.in_check('black'): 
            res = 1 # White wins
            message = "Bot Wins (White)!"
        
        chess_game.update_learning(history, res)
        chess_game.save_knowledge()
        print(f"Game Over: {message}. Knowledge Saved.")
        return True, message
    return False, ""

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("FIDE Chess Bot - Playing as Black")
    selected_sq, valid_moves_set = None, set()
    game_over = False
    game_message = ""
    game_history = [] 

    while True:
        if not game_over and chess_game.current_turn == 'white':

            _, move = chess_game.minimax(2, -1000, 1000, False)
            if move:
                chess_game.execute_move(move[0], move[1], move[2], move[3])
                game_history.append(chess_game.get_state_key())
                chess_game.current_turn = 'black'
                game_over, game_message = check_for_game_end(game_history)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if chess_game.current_turn == 'black':
                    c, r = event.pos[0] // SQ_SIZE, event.pos[1] // SQ_SIZE
                    
                    if (r, c) in valid_moves_set:
                        chess_game.execute_move(selected_sq[0], selected_sq[1], r, c)
                        game_history.append(chess_game.get_state_key())
                        chess_game.current_turn = 'white'
                        game_over, game_message = check_for_game_end(game_history)
                        selected_sq, valid_moves_set = None, set()
                    
                    elif chess_game.is_black_piece(chess_game.board[r][c]):
                        selected_sq = (r, c)
                        valid_moves_set = {(m[2], m[3]) for m in chess_game.get_all_valid_moves('black') if m[0] == r and m[1] == c}
                    else:
                        selected_sq, valid_moves_set = None, set()

        # Drawing logic
        draw_board(screen, selected_sq, valid_moves_set)
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            screen.blit(overlay, (0, 0))
            txt = RESULT_FONT.render(game_message, True, (200, 0, 0))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
