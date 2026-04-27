import chess_game

def main():
    chess_game.load_knowledge()
    while True:
        chess_game.show_board()
        if chess_game.is_checkmate(chess_game.current_turn):
            print("Game Over!")
            break
        move = input(f"{chess_game.current_turn} move (e.g. 6444 for e2e4): ")
        if len(move) == 4:
            sr, sc, er, ec = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            if chess_game.valid_move(sr, sc, er, ec):
                chess_game.board[er][ec], chess_game.board[sr][sc] = chess_game.board[sr][sc], '.'
                chess_game.current_turn = 'black' if chess_game.current_turn == 'white' else 'white'

if __name__ == "__main__":
    main()
