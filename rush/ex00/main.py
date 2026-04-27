#!/usr/bin/env python3

# ALL POSSIBLE MOVES
# Pawn (P):
# . . . . . . .
# . . . . . . .
# . . X . X . .
# . . . P . . .
# . . . . . . .
# . . . . . . .
# . . . . . . .
# Bishop (B):
# X . . . . . X
# . X . . . X .
# . . X . X . .
# . . . B . . .
# . . X . X . .
# . X . . . X .
# X . . . . . X
# Rook (R):
# . . . X . . .
# . . . X . . .
# . . . X . . .
# X X X R X X X
# . . . X . . .
# . . . X . . .
# . . . X . . .
# Queen (Q)
# X . . X . . X
# . X . X . X .
# . . X X X . .
# X X X Q X X X
# . . X X X . .
# . X . X . X .
# X . . X . . X

from checkmate import checkmate

def main():
    board = """\
....
.K..
..P.
....\
"""
    checkmate(board)

if __name__ == "__main__":
    main()
