#!/usr/bin/env python3
import chess_game

def parse_coordinate(coord):
    """Converts notation like 'e2' to (row, col) indices like (6, 4)"""
    if len(coord) != 2:
        return None
    col_char = coord[0].lower()
    row_char = coord[1]
    
    if not ('a' <= col_char <= 'h') or not ('1' <= row_char <= '8'):
        return None
        
    col = ord(col_char) - ord('a')
    row = 8 - int(row_char)
    return row, col

def main():
    chess_game.show_rules()
    
    while True:
        chess_game.show_board()
        if chess_game.in_check(chess_game.current_turn):
            print("!!! YOUR KING IS IN CHECK !!!")

        try:
            move_input = input(f"{chess_game.current_turn} to move (e.g., e2 e4): ").split()
            if len(move_input) != 2:
                print("Enter move as two coordinates (e.g., e2 e4)")
                continue

            start_coords = parse_coordinate(move_input[0])
            end_coords = parse_coordinate(move_input[1])

            if not start_coords or not end_coords:
                print("Invalid notation. Use a-h and 1-8.")
                continue

            sr, sc = start_coords
            er, ec = end_coords

            if chess_game.valid_move(sr, sc, er, ec):
                chess_game.board[er][ec] = chess_game.board[sr][sc]
                chess_game.board[sr][sc] = '.'

                if chess_game.board[er][ec].lower() == 'p' and (er == 0 or er == chess_game.board_size - 1):
                    choice = input("Promote to a rook (r) or Bishop (b)? ").lower()
                    if choice not in ['r', 'b']: choice = 'r'
                    chess_game.board[er][ec] = choice if chess_game.current_turn == 'white' else choice.upper()

                if chess_game.check_stalemate():
                    chess_game.show_board()
                    print("Game over: Stalemate.")
                    break

                chess_game.current_turn = 'black' if chess_game.current_turn == 'white' else 'white'
            else:
                print("\n[!] Invalid Move")
        except ValueError:
            print("\n[!] Error processing move.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
