#!/usr/bin/env python3
import chess_game

def parse_coordinate(coord):
    if len(coord) != 2:
        return None
    col_char = coord[0].lower()
    row_char = coord[1]
    
    if not ('a' <= col_char <= 'h') or not ('1' <= row_char <= '8'):
        return None
        
    column = ord(col_char) - ord('a')
    row = 8 - int(row_char)
    return row, column

def main():
    chess_game.show_rules()
    chess_game.record_position()

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
                piece = chess_game.board[sr][sc]
                target = chess_game.board[er][ec]

                if piece.lower() == 'k' and abs(ec - sc) == 2:
                    if ec == 6: #
                        chess_game.board[sr][5] = chess_game.board[sr][7]
                        chess_game.board[sr][7] = '.'
                    elif ec == 2:
                        chess_game.board[sr][3] = chess_game.board[sr][0]
                        chess_game.board[sr][0] = '.'

                if piece == 'k': chess_game.has_moved['white_king'] = True
                elif piece == 'K': chess_game.has_moved['black_king'] = True
                elif piece == 'r':
                    if sr == 7 and sc == 0: chess_game.has_moved['white_rook_a'] = True
                    if sr == 7 and sc == 7: chess_game.has_moved['white_rook_h'] = True
                elif piece == 'R':
                    if sr == 0 and sc == 0: chess_game.has_moved['black_rook_a'] = True
                    if sr == 0 and sc == 7: chess_game.has_moved['black_rook_h'] = True
                
                if target == 'r':
                    if er == 7 and ec == 0: chess_game.has_moved['white_rook_a'] = True
                    if er == 7 and ec == 7: chess_game.has_moved['white_rook_h'] = True
                elif target == 'R':
                    if er == 0 and ec == 0: chess_game.has_moved['black_rook_a'] = True
                    if er == 0 and ec == 7: chess_game.has_moved['black_rook_h'] = True

                chess_game.board[er][ec] = piece
                chess_game.board[sr][sc] = '.'

                if chess_game.board[er][ec].lower() == 'p' and (er == 0 or er == 7):
                    choice = input("Promote to a rook (r) or bishop (b)? ").lower()
                    if choice not in ['r', 'b']:
                        choice = 'r'
                    chess_game.board[er][ec] = choice.lower() if chess_game.current_turn == 'white' else choice.upper()

                chess_game.current_turn = 'black' if chess_game.current_turn == 'white' else 'white'
                chess_game.record_position()

                if chess_game.check_repeat():
                    chess_game.show_board()
                    print("Draw: Threefold Repetition")
                    break

                if chess_game.check_stalemate():
                    chess_game.show_board()
                    print("Draw: Stalemate.")
                    break
            else:
                print("\n[!] Invalid Move")
        except ValueError:
            print("\n[!] Error processing move.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
