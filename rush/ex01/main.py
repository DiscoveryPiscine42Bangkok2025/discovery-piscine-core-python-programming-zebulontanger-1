#!/usr/bin/env python3
import re
import chess_game
import time
import threading
import sys

# --- LIVE TIMER LOGIC ---
def background_timer():
    # Keep running as long as the game_active flag in chess_game is True
    while getattr(chess_game, 'game_active', True):
        # Calculate time elapsed and update the active player's clock
        chess_game.update_clocks()
        
        # Convert raw seconds into readable MM:SS strings
        w_t = chess_game.format_time(chess_game.player_times['white'])
        b_t = chess_game.format_time(chess_game.player_times['black'])
        
        # ANSI Escape Codes used in the f-string:
        # \033[s : Save the current cursor position (where you are typing)
        # \033[1;1H : Move the cursor to Row 1, Column 1 (top-left)
        # \033[K : Clear everything on the current line
        # [ TIME ] : Print the updated clocks
        # \033[u : Restore the cursor to its saved position so you can keep typing
        timer_str = f"\033[s\033[1;1H\033[K[ TIME ] White: {w_t}  |  Black: {b_t}\033[u"
        
        # Write the string to the terminal and force it to display immediately
        sys.stdout.write(timer_str)
        sys.stdout.flush()
        
        # Wait 0.2 seconds before the next update to keep CPU usage low
        time.sleep(0.2)

def find_move(notation):
    if notation.upper() == 'O-O': return 'O-O'
    if notation.upper() == 'O-O-O': return 'O-O-O'
    
    pattern = r'^([KQRBN])?([a-h])?([1-8])?(x)?([a-h][1-8])(?:=([QRBN]))?[\\+#]?$'
    match = re.match(pattern, notation, re.IGNORECASE)
    if not match: return None
    
    p_char, src_f, src_r, is_cap, dest, promo = match.groups()
    p_map = {'K': 'k', 'Q': 'q', 'R': 'r', 'B': 'b', 'N': 'n', None: 'p'}
    symbol_map = {
        'white': {'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'},
        'black': {'k':'♔','q':'♕','r':'♖','b':'♗','n':'♘','p':'♙'}
    }
    
    target_symbol = symbol_map[chess_game.current_turn][p_map[p_char.upper() if p_char else None]]
    er, ec = 8 - int(dest[1]), ord(dest[0].lower()) - ord('a')
    
    candidates = []
    for r in range(8):
        for c in range(8):
            if chess_game.board[r][c] == target_symbol:
                if src_f and c != ord(src_f.lower()) - ord('a'): continue
                if src_r and r != 8 - int(src_r): continue
                if chess_game.valid_move(r, c, er, ec): candidates.append((r, c))
    
    if len(candidates) == 1:
        return (candidates[0][0], candidates[0][1], er, ec, promo.upper() if promo else None)
    return None

def format_notation(move_data, is_capture, is_check, is_mate):
    if isinstance(move_data, str): return move_data
    sr, sc, er, ec, promo = move_data
    piece = chess_game.board[er][ec]
    p_map = {'♜':'R','♖':'R','♞':'N','♘':'N','♝':'B','♗':'B','♛':'Q','♕':'Q','♚':'K','♔':'K'}
    
    if piece in ('♟', '♙'):
        notation = f"{chr(ord('a')+sc)}x{chr(ord('a')+ec)}{8-er}" if is_capture else f"{chr(ord('a')+ec)}{8-er}"
        if promo: notation += f"={promo}"
    else:
        piece_char = p_map.get(piece, "")
        capture_sig = "x" if is_capture else ""
        notation = f"{piece_char}{capture_sig}{chr(ord('a')+ec)}{8-er}"
        
    if is_mate: notation += "#"
    elif is_check: notation += "+"
    return notation

def main():
    # 1. Show the rules
    chess_game.show_rules()
    
    # 2. Setup game state
    chess_game.record_position()
    game_history = []
    chess_game.game_active = True
    chess_game.last_update_time = time.time()
    
    # 3. Start timer thread
    timer_thread = threading.Thread(target=background_timer, daemon=True)
    timer_thread.start()

    # 4. Clear screen to prepare for board and timer layout
    print("\033[2J") 

    try:
        while True:
            # Move cursor to Row 2 so Row 1 stays reserved for the Timer
            sys.stdout.write("\033[2;1H") 
            chess_game.show_board()
            
            all_moves = chess_game.get_all_valid_moves()

            if chess_game.player_times[chess_game.current_turn] <= 0:
                print(f"\n{chess_game.current_turn.upper()} ran out of time!")
                break

            if not all_moves:
                if chess_game.in_check(chess_game.current_turn):
                    print("CHECKMATE!")
                else:
                    print("STALEMATE!")
                break
                
            move_input = input(f"\n{chess_game.current_turn.capitalize()} move: ").strip()
            
            # UI Cleanup: Clear input lines after move is submitted
            sys.stdout.write("\033[A\033[K\033[A\033[K") 

            move_data = find_move(move_input)
            if not move_data:
                print("[!] Invalid Move."); time.sleep(1); continue

            is_capture = False
            if not isinstance(move_data, str):
                is_capture = chess_game.board[move_data[2]][move_data[3]] != '.'

            if isinstance(move_data, str): # Castling
                row = 7 if chess_game.current_turn == 'white' else 0
                if move_data == 'O-O':
                    chess_game.board[row][6], chess_game.board[row][4] = chess_game.board[row][4], '.'
                    chess_game.board[row][5], chess_game.board[row][7] = chess_game.board[row][7], '.'
                else:
                    chess_game.board[row][2], chess_game.board[row][4] = chess_game.board[row][4], '.'
                    chess_game.board[row][3], chess_game.board[row][0] = chess_game.board[row][0], '.'
            else: # Normal Move
                sr, sc, er, ec, promo = move_data
                piece = chess_game.board[sr][sc]
                chess_game.board[er][ec], chess_game.board[sr][sc] = piece, '.'
                if piece in ('♟', '♙') and (er == 0 or er == 7):
                    syms = {'white':{'Q':'♛','R':'♜','B':'♝','N':'♞'}, 'black':{'Q':'♕','R':'♖','B':'♗','N':'♘'}}
                    chess_game.board[er][ec] = syms[chess_game.current_turn][promo or 'Q']

            opp_color = 'black' if chess_game.current_turn == 'white' else 'white'
            game_history.append(format_notation(move_data, is_capture, chess_game.in_check(opp_color), chess_game.is_checkmate(opp_color)))
            chess_game.current_turn = opp_color
            chess_game.record_position()

    finally:
        chess_game.game_active = False
        print("\nGame Over.")

if __name__ == "__main__":
    main()
