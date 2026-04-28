import random
import pickle
import sys
import os
from functools import lru_cache

# settings
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

# encourage center control, piece development, good outposts
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
    [0.1,0.1,0.2,0.3,0.3,0.2,0.1,0.1],
    [0.05,0.05,0.1,0.25,0.25,0.1,0.05,0.05],
    [0,  0,  0,  0.2,0.2, 0,  0,  0],
    [0.05,-0.05,-0.1,0,  0,-0.1,-0.05,0.05],
    [0.05,0.1,0.1,-0.2,-0.2,0.1,0.1,0.05],
    [0,  0,  0,  0,  0,  0,  0,  0]
]
KNIGHT_TABLE = [
    [-0.5,-0.4,-0.3,-0.3,-0.3,-0.3,-0.4,-0.5],
    [-0.4,-0.2, 0,   0,   0,   0,  -0.2,-0.4],
    [-0.3, 0,   0.1, 0.15,0.15,0.1, 0,  -0.3],
    [-0.3, 0.05,0.15,0.2, 0.2, 0.15,0.05,-0.3],
    [-0.3, 0,   0.15,0.2, 0.2, 0.15,0,  -0.3],
    [-0.3, 0.05,0.1, 0.15,0.15,0.1, 0.05,-0.3],
    [-0.4,-0.2, 0,   0.05,0.05,0,  -0.2,-0.4],
    [-0.5,-0.4,-0.3,-0.3,-0.3,-0.3,-0.4,-0.5]
]
BISHOP_TABLE = [
    [-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.2],
    [-0.1, 0,   0,   0,   0,   0,   0,  -0.1],
    [-0.1, 0,   0.05,0.1, 0.1, 0.05,0,  -0.1],
    [-0.1, 0.05,0.05,0.1, 0.1, 0.05,0.05,-0.1],
    [-0.1, 0,   0.1, 0.1, 0.1, 0.1, 0,  -0.1],
    [-0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,-0.1],
    [-0.1, 0.05,0,   0,   0,   0,  0.05,-0.1],
    [-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.2]
]
ROOK_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0  ],
    [0.05,0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [-0.05,0,  0,   0,   0,   0,   0,  -0.05],
    [0,   0,   0,   0.05,0.05,0,   0,   0  ]
]
QUEEN_TABLE = [
    [-0.2,-0.1,-0.1,-0.05,-0.05,-0.1,-0.1,-0.2],
    [-0.1, 0,   0,   0,    0,    0,   0,  -0.1],
    [-0.1, 0,   0.05,0.05, 0.05, 0.05,0,  -0.1],
    [-0.05,0,   0.05,0.05, 0.05, 0.05,0,  -0.05],
    [0,    0,   0.05,0.05, 0.05, 0.05,0,  -0.05],
    [-0.1, 0.05,0.05,0.05, 0.05, 0.05,0,  -0.1],
    [-0.1, 0,   0.05,0,    0,    0,   0,  -0.1],
    [-0.2,-0.1,-0.1,-0.05,-0.05,-0.1,-0.1,-0.2]
]

# king safety
KING_TABLE_MID = [
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.3,-0.4,-0.4,-0.5,-0.5,-0.4,-0.4,-0.3],
    [-0.2,-0.3,-0.3,-0.4,-0.4,-0.3,-0.3,-0.2],
    [-0.1,-0.2,-0.2,-0.2,-0.2,-0.2,-0.2,-0.1],
    [0.2,  0.2, 0,   0,   0,   0,  0.2,  0.2],
    [0.2,  0.3, 0.1, 0,   0,  0.1, 0.3,  0.2]
]
KING_TABLE_END = [
    [-0.5,-0.4,-0.3,-0.2,-0.2,-0.3,-0.4,-0.5],
    [-0.3,-0.2,-0.1, 0,   0,  -0.1,-0.2,-0.3],
    [-0.3,-0.1, 0.2, 0.3, 0.3, 0.2,-0.1,-0.3],
    [-0.3,-0.1, 0.3, 0.4, 0.4, 0.3,-0.1,-0.3],
    [-0.3,-0.1, 0.3, 0.4, 0.4, 0.3,-0.1,-0.3],
    [-0.3,-0.1, 0.2, 0.3, 0.3, 0.2,-0.1,-0.3],
    [-0.3,-0.3, 0,   0,   0,   0,  -0.3,-0.3],
    [-0.5,-0.3,-0.3,-0.3,-0.3,-0.3,-0.3,-0.5]
]

# ── Pre-computed lookup tables for speed ─────────────────────────────────────
# Convert piece tables to tuples for lru_cache compatibility
_PAWN_TABLE_T   = tuple(tuple(r) for r in PAWN_TABLE)
_KNIGHT_TABLE_T = tuple(tuple(r) for r in KNIGHT_TABLE)
_BISHOP_TABLE_T = tuple(tuple(r) for r in BISHOP_TABLE)
_ROOK_TABLE_T   = tuple(tuple(r) for r in ROOK_TABLE)
_QUEEN_TABLE_T  = tuple(tuple(r) for r in QUEEN_TABLE)
_KING_MID_T     = tuple(tuple(r) for r in KING_TABLE_MID)
_KING_END_T     = tuple(tuple(r) for r in KING_TABLE_END)

# Knight move offsets (pre-computed)
_KNIGHT_MOVES = ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
# King move offsets
_KING_MOVES   = ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1))
# Sliding directions
_ROOK_DIRS    = ((0,1),(0,-1),(1,0),(-1,0))
_BISHOP_DIRS  = ((1,1),(1,-1),(-1,1),(-1,-1))
_QUEEN_DIRS   = _ROOK_DIRS + _BISHOP_DIRS

# ── Opening Book (square notation: "e2e4" style) ─────────────────────────────
# Keys are tuples of moves played so far; values are lists of candidate replies.
# Covers: Open/Closed/Semi-Open games, major gambits, sidelines for both colors.

OPENING_BOOK = {

    # ══════════════════════════════════════════════════
    # WHITE FIRST MOVES
    # ══════════════════════════════════════════════════
    (): ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"],

    # ══════════════════════════════════════════════════
    # 1.e4 OPENINGS
    # ══════════════════════════════════════════════════

    # --- e4 e5 main lines ---
    ("e2e4",): ["e7e5", "c7c5", "e7e6", "c7c6", "d7d5", "g8f6", "d7d6", "g7g6"],

    # Ruy Lopez / Spanish
    ("e2e4","e7e5"):                             ["g1f3"],
    ("e2e4","e7e5","g1f3"):                      ["b8c6"],
    ("e2e4","e7e5","g1f3","b8c6"):               ["f1b5"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5"):        ["a7a6","g8f6","f8c5","d7d6","b7b5"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6"): ["b5a4","b5c6"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6","b5a4"): ["g8f6","d7d6"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6","b5a4","g8f6"): ["e1g1"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","a7a6","b5a4","g8f6","e1g1"): ["f8e7","f6e4"],
    # Berlin Defence
    ("e2e4","e7e5","g1f3","b8c6","f1b5","g8f6"): ["e1g1","d2d4"],
    ("e2e4","e7e5","g1f3","b8c6","f1b5","g8f6","e1g1"): ["f6e4"],

    # Italian Game
    ("e2e4","e7e5","g1f3","b8c6","f1c4"):        ["f8c5","g8f6","f7f5"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5"): ["c2c3","b2b4","d2d3"],
    # Evans Gambit
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5","b2b4"): ["c5b4"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5","b2b4","c5b4"): ["c2c3"],
    # Two Knights
    ("e2e4","e7e5","g1f3","b8c6","f1c4","g8f6"): ["d2d4","f3g5"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","g8f6","d2d4"): ["e5d4"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","g8f6","f3g5"): ["d7d5"],

    # Scotch Game
    ("e2e4","e7e5","g1f3","b8c6","d2d4"): ["e5d4"],
    ("e2e4","e7e5","g1f3","b8c6","d2d4","e5d4"): ["f3d4"],
    ("e2e4","e7e5","g1f3","b8c6","d2d4","e5d4","f3d4"): ["f8c5","g8f6","d8h4"],
    # Scotch Gambit
    ("e2e4","e7e5","g1f3","b8c6","d2d4","e5d4","f1c4"): ["f8c5","g8f6"],

    # King's Gambit
    ("e2e4","e7e5","f2f4"):            ["e5f4","f8c5","d7d5"],
    ("e2e4","e7e5","f2f4","e5f4"):     ["g1f3","f1c4"],
    ("e2e4","e7e5","f2f4","e5f4","g1f3"): ["g7g5","d7d5","g8f6"],
    ("e2e4","e7e5","f2f4","e5f4","f1c4"): ["d8h4","g8f6","g7g5"],
    # King's Gambit Declined
    ("e2e4","e7e5","f2f4","f8c5"):     ["g1f3"],
    ("e2e4","e7e5","f2f4","d7d5"):     ["e4d5","g1f3"],

    # Vienna Game
    ("e2e4","e7e5","b1c3"):            ["g8f6","b8c6","f8c5"],
    ("e2e4","e7e5","b1c3","g8f6"):     ["f2f4","g1f3"],
    # Vienna Gambit
    ("e2e4","e7e5","b1c3","g8f6","f2f4"): ["d7d5","e5f4"],

    # Giuoco Piano
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5","c2c3"): ["g8f6","d7d6","d8e7"],
    ("e2e4","e7e5","g1f3","b8c6","f1c4","f8c5","c2c3","g8f6"): ["d2d4"],

    # Petrov's Defence (Russian)
    ("e2e4","e7e5","g1f3","g8f6"):     ["f3e5","b1c3","d2d4"],
    ("e2e4","e7e5","g1f3","g8f6","f3e5"): ["d7d6","b8c6"],
    ("e2e4","e7e5","g1f3","g8f6","f3e5","d7d6"): ["e5f3","e5d3"],

    # Philidor Defence
    ("e2e4","e7e5","g1f3","d7d6"):     ["d2d4","f1c4","b1c3"],
    ("e2e4","e7e5","g1f3","d7d6","d2d4"): ["b8d7","g8f6","e5d4"],

    # Centre Game / Danish Gambit
    ("e2e4","e7e5","d2d4"):            ["e5d4"],
    ("e2e4","e7e5","d2d4","e5d4"):     ["d1d4","c2c3"],
    ("e2e4","e7e5","d2d4","e5d4","c2c3"): ["d4c3","d7d5","g8f6"],
    ("e2e4","e7e5","d2d4","e5d4","c2c3","d4c3"): ["b1c3","f1c4"],

    # ── Sicilian Defence ──────────────────────────────
    ("e2e4","c7c5"):                   ["g1f3","b1c3","c2c3"],
    ("e2e4","c7c5","g1f3"):            ["b8c6","d7d6","e7e6","g7g6","a7a6"],
    # Sicilian Najdorf
    ("e2e4","c7c5","g1f3","d7d6"):     ["d2d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4"): ["c5d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4"): ["f3d4"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4"): ["g8f6"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6"): ["b1c3"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6","b1c3"): ["a7a6"],
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6","b1c3","a7a6"): ["f1e2","c1g5","f2f3","f2f4"],
    # Sicilian Dragon
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6","b1c3","g7g6"): ["c1e3","f2f3","f1e2"],
    ("e2e4","c7c5","g1f3","g7g6"):     ["d2d4","c2c3"],
    # Sicilian Scheveningen
    ("e2e4","c7c5","g1f3","d7d6","d2d4","c5d4","f3d4","g8f6","b1c3","e7e6"): ["f1e2","g2g4","f2f4"],
    # Sicilian Classical
    ("e2e4","c7c5","g1f3","b8c6"):     ["d2d4","f1b5","b1c3"],
    ("e2e4","c7c5","g1f3","b8c6","d2d4"): ["c5d4"],
    ("e2e4","c7c5","g1f3","b8c6","d2d4","c5d4"): ["f3d4"],
    ("e2e4","c7c5","g1f3","b8c6","d2d4","c5d4","f3d4"): ["g8f6","d7d6","e7e6"],
    # Alapin Sicilian
    ("e2e4","c7c5","c2c3"):            ["d7d5","g8f6","b8c6","e7e6"],
    ("e2e4","c7c5","c2c3","d7d5"):     ["e4d5","e4e5"],
    ("e2e4","c7c5","c2c3","g8f6"):     ["e4e5","d2d4"],
    # Grand Prix Attack
    ("e2e4","c7c5","b1c3"):            ["b8c6","d7d6","e7e6","a7a6"],
    ("e2e4","c7c5","b1c3","b8c6"):     ["f2f4","g1f3","f1b5"],
    # Smith-Morra Gambit
    ("e2e4","c7c5","d2d4","c5d4"):     ["c2c3"],
    ("e2e4","c7c5","d2d4","c5d4","c2c3"): ["d4c3","d7d5","g8f6"],
    ("e2e4","c7c5","d2d4","c5d4","c2c3","d4c3"): ["b1c3"],

    # ── French Defence ────────────────────────────────
    ("e2e4","e7e6"):                   ["d2d4","b1c3"],
    ("e2e4","e7e6","d2d4"):            ["d7d5"],
    ("e2e4","e7e6","d2d4","d7d5"):     ["b1c3","b1d2","e4e5","e4d5"],
    # Winawer Variation
    ("e2e4","e7e6","d2d4","d7d5","b1c3"): ["f8b4","g8f6","d5e4"],
    ("e2e4","e7e6","d2d4","d7d5","b1c3","f8b4"): ["e4e5","a2a3","e1g1"],
    ("e2e4","e7e6","d2d4","d7d5","b1c3","f8b4","e4e5"): ["c7c5","g8e7"],
    # Classical Variation
    ("e2e4","e7e6","d2d4","d7d5","b1c3","g8f6"): ["c1g5","e4e5","e4d5"],
    ("e2e4","e7e6","d2d4","d7d5","b1c3","g8f6","c1g5"): ["f8e7","d5e4","h7h6"],
    # Tarrasch
    ("e2e4","e7e6","d2d4","d7d5","b1d2"): ["g8f6","c7c5","f8e7"],
    ("e2e4","e7e6","d2d4","d7d5","b1d2","c7c5"): ["g1f3","e4d5"],
    # Advance Variation
    ("e2e4","e7e6","d2d4","d7d5","e4e5"): ["c7c5","g8e7","f8d6"],
    ("e2e4","e7e6","d2d4","d7d5","e4e5","c7c5"): ["c2c3","g1f3","f2f4"],
    # Exchange Variation
    ("e2e4","e7e6","d2d4","d7d5","e4d5"): ["e6d5"],
    ("e2e4","e7e6","d2d4","d7d5","e4d5","e6d5"): ["g1f3","f1d3","b1c3"],

    # ── Caro-Kann Defence ─────────────────────────────
    ("e2e4","c7c6"):                   ["d2d4","b1c3"],
    ("e2e4","c7c6","d2d4"):            ["d7d5"],
    ("e2e4","c7c6","d2d4","d7d5"):     ["b1c3","b1d2","e4e5","e4d5","e4d5"],
    # Classical
    ("e2e4","c7c6","d2d4","d7d5","b1c3"): ["d5e4","g8f6","e7e6"],
    ("e2e4","c7c6","d2d4","d7d5","b1c3","d5e4"): ["c3e4"],
    ("e2e4","c7c6","d2d4","d7d5","b1c3","d5e4","c3e4"): ["c8f5","g8f6","b8d7"],
    # Advance
    ("e2e4","c7c6","d2d4","d7d5","e4e5"): ["c8f5","g7g6","e7e6"],
    ("e2e4","c7c6","d2d4","d7d5","e4e5","c8f5"): ["g1f3","b1c3","c2c3"],
    # Exchange
    ("e2e4","c7c6","d2d4","d7d5","e4d5"): ["c6d5"],
    ("e2e4","c7c6","d2d4","d7d5","e4d5","c6d5"): ["c2c4","g1f3","f1d3"],
    # Panov Attack
    ("e2e4","c7c6","d2d4","d7d5","e4d5","c6d5","c2c4"): ["g8f6","e7e6"],

    # ── Pirc Defence ──────────────────────────────────
    ("e2e4","d7d6"):                   ["d2d4","b1c3"],
    ("e2e4","d7d6","d2d4"):            ["g8f6","g7g6"],
    ("e2e4","d7d6","d2d4","g8f6"):     ["b1c3"],
    ("e2e4","d7d6","d2d4","g8f6","b1c3"): ["g7g6","e7e5","c7c6"],
    ("e2e4","d7d6","d2d4","g8f6","b1c3","g7g6"): ["f2f4","f1e2","c1g5","c1e3"],

    # ── Alekhine Defence ──────────────────────────────
    ("e2e4","g8f6"):                   ["e4e5"],
    ("e2e4","g8f6","e4e5"):            ["f6d5"],
    ("e2e4","g8f6","e4e5","f6d5"):     ["d2d4","c2c4"],
    ("e2e4","g8f6","e4e5","f6d5","d2d4"): ["d7d6","e7e6","g7g6","c7c5"],
    ("e2e4","g8f6","e4e5","f6d5","c2c4"): ["d5b4","d5f4","d5b6"],

    # ── Scandinavian (Centre Counter) ─────────────────
    ("e2e4","d7d5"):                   ["e4d5"],
    ("e2e4","d7d5","e4d5"):            ["d8d5","g8f6"],
    ("e2e4","d7d5","e4d5","d8d5"):     ["b1c3"],
    ("e2e4","d7d5","e4d5","d8d5","b1c3"): ["d5a5","d5d6","d5e6"],
    ("e2e4","d7d5","e4d5","g8f6"):     ["d2d4","b1c3","c2c4"],
    ("e2e4","d7d5","e4d5","g8f6","d2d4"): ["f6d5","g7g6","c7c6"],

    # ── King's Indian Attack (e4 setup) ───────────────
    ("e2e4","e7e6","g1f3"):            ["d7d5","c7c5"],
    ("e2e4","e7e6","g1f3","d7d5"):     ["g2g3","e4e5","b1c3"],

    # ══════════════════════════════════════════════════
    # 1.d4 OPENINGS
    # ══════════════════════════════════════════════════

    ("d2d4",): ["d7d5","g8f6","f7f5","e7e6","c7c5","g7g6","b8c6","d7d6"],

    # ── Queen's Gambit ────────────────────────────────
    ("d2d4","d7d5"):                   ["c2c4","g1f3","c2c3"],
    ("d2d4","d7d5","c2c4"):            ["e7e6","c7c6","d5c4","b8c6","e7e5","g8f6"],
    # QGD
    ("d2d4","d7d5","c2c4","e7e6"):     ["b1c3","g1f3"],
    ("d2d4","d7d5","c2c4","e7e6","b1c3"): ["g8f6","c7c6","f8e7"],
    ("d2d4","d7d5","c2c4","e7e6","b1c3","g8f6"): ["c1g5","g1f3","e2e3"],
    ("d2d4","d7d5","c2c4","e7e6","b1c3","g8f6","c1g5"): ["f8e7","b8d7","h7h6","c7c6"],
    # QGA
    ("d2d4","d7d5","c2c4","d5c4"):     ["e2e4","g1f3","b1c3"],
    ("d2d4","d7d5","c2c4","d5c4","e2e4"): ["e7e5","g8f6","c7c5"],
    ("d2d4","d7d5","c2c4","d5c4","g1f3"): ["g8f6","e7e6","c7c5"],
    # Slav Defence
    ("d2d4","d7d5","c2c4","c7c6"):     ["g1f3","b1c3","e2e3"],
    ("d2d4","d7d5","c2c4","c7c6","g1f3"): ["g8f6","e7e6","d5c4"],
    ("d2d4","d7d5","c2c4","c7c6","g1f3","g8f6"): ["b1c3","e2e3"],
    ("d2d4","d7d5","c2c4","c7c6","g1f3","g8f6","b1c3"): ["e7e6","d5c4","c8f5","a7a6"],
    # Semi-Slav
    ("d2d4","d7d5","c2c4","c7c6","g1f3","g8f6","b1c3","e7e6"): ["c1g5","e2e3","d1c2"],
    # Czech/Meran
    ("d2d4","d7d5","c2c4","c7c6","g1f3","g8f6","b1c3","e7e6","e2e3"): ["b8d7","a7a6"],
    # Exchange Slav
    ("d2d4","d7d5","c2c4","c7c6","c4d5"): ["c6d5"],

    # ── King's Indian Defence ─────────────────────────
    ("d2d4","g8f6"):                   ["c2c4","g1f3","b1c3"],
    ("d2d4","g8f6","c2c4"):            ["g7g6","e7e6","c7c5","d7d6"],
    ("d2d4","g8f6","c2c4","g7g6"):     ["b1c3","g1f3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3"): ["f8g7"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7"): ["e2e4","g1f3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4"): ["d7d6","e8g8","d7d5"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6"): ["g1f3","f2f3","f1e2"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","g1f3"): ["e8g8"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","g1f3","e8g8"): ["f1e2","c1e3","d1c2"],
    # Classical KID
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","g1f3","e8g8","f1e2"): ["e7e5","b8d7","c7c5"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","g1f3","e8g8","f1e2","e7e5"): ["d4d5","e1g1","d4e5"],
    # Four Pawns Attack
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","f2f4"): ["e8g8","e7e5","c7c5"],
    # Saemisch
    ("d2d4","g8f6","c2c4","g7g6","b1c3","f8g7","e2e4","d7d6","f2f3"): ["e8g8","b8c6","c7c5"],

    # ── Grünfeld Defence ──────────────────────────────
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5"):  ["c4d5","e2e4","g1f3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5"): ["f6d5"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5","f6d5"): ["e2e4","g1f3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5","f6d5","e2e4"): ["d5c3","d5b6"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5","f6d5","e2e4","d5c3"): ["b2c3"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5","f6d5","e2e4","d5c3","b2c3"): ["f8g7"],
    ("d2d4","g8f6","c2c4","g7g6","b1c3","d7d5","c4d5","f6d5","e2e4","d5c3","b2c3","f8g7"): ["f1c4","g1f3","h2h4"],

    # ── Nimzo-Indian Defence ──────────────────────────
    ("d2d4","g8f6","c2c4","e7e6"):     ["b1c3","g1f3"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3"): ["f8b4"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4"): ["e2e3","d1c2","a2a3","g1f3","f2f3"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4","e2e3"): ["e8g8","d7d5","c7c5","b7b6"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4","d1c2"): ["e8g8","d7d5","c7c5","b8c6"],
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4","a2a3"): ["b4c3","b4a5"],
    # Saemisch Nimzo
    ("d2d4","g8f6","c2c4","e7e6","b1c3","f8b4","f2f3"): ["d7d5","c7c5","b7b6"],

    # ── Queen's Indian Defence ────────────────────────
    ("d2d4","g8f6","c2c4","e7e6","g1f3"): ["b7b6","d7d5","f8b4","c7c5"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","b7b6"): ["b1c3","g2g3","e2e3"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","b7b6","b1c3"): ["c8b7","f8b4","f8e7"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","b7b6","g2g3"): ["c8b7","f8e7","c7c5"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","b7b6","g2g3","c8b7"): ["f1g2","b1c3"],

    # ── Catalan Opening ───────────────────────────────
    ("d2d4","g8f6","c2c4","e7e6","g1f3","d7d5","g2g3"): ["f8e7","d5c4","c7c6","b8d7"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","d7d5","g2g3","f8e7"): ["f1g2","e1g1"],
    ("d2d4","g8f6","c2c4","e7e6","g1f3","d7d5","g2g3","d5c4"): ["f1g2"],

    # ── Benoni Defence ────────────────────────────────
    ("d2d4","g8f6","c2c4","c7c5"):     ["d4d5","g1f3","e2e3"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5"): ["e7e6","d7d6","g7g6"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","e7e6"): ["b1c3","g1f3"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","e7e6","b1c3"): ["e6d5","d7d6"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","e7e6","b1c3","e6d5"): ["c4d5","e2e4"],
    # Modern Benoni
    ("d2d4","g8f6","c2c4","c7c5","d4d5","e7e6","b1c3","e6d5","c4d5"): ["d7d6","g7g6"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","e7e6","b1c3","e6d5","c4d5","g7g6"): ["e2e4","g1f3","f2f4"],
    # Benko Gambit
    ("d2d4","g8f6","c2c4","c7c5","d4d5","b7b5"): ["c4b5","d5d6","b5b6"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","b7b5","c4b5"): ["a7a6"],
    ("d2d4","g8f6","c2c4","c7c5","d4d5","b7b5","c4b5","a7a6"): ["b5a6","b5c6","d5d6"],

    # ── Dutch Defence ─────────────────────────────────
    ("d2d4","f7f5"):                   ["g2g3","c2c4","g1f3","b1c3"],
    ("d2d4","f7f5","c2c4"):            ["g8f6","e7e6","d7d6","g7g6"],
    ("d2d4","f7f5","c2c4","g8f6"):     ["g2g3","b1c3","g1f3"],
    ("d2d4","f7f5","c2c4","g8f6","g2g3"): ["e7e6","g7g6","d7d6"],
    # Stonewall Dutch
    ("d2d4","f7f5","c2c4","g8f6","g2g3","e7e6"): ["f1g2","b1c3"],
    ("d2d4","f7f5","c2c4","g8f6","g2g3","e7e6","f1g2"): ["d7d5","f8e7","b8c6","c7c6"],
    # Leningrad Dutch
    ("d2d4","f7f5","c2c4","g8f6","g2g3","g7g6"): ["f1g2","b1c3"],
    ("d2d4","f7f5","c2c4","g8f6","g2g3","g7g6","f1g2"): ["f8g7"],

    # ── Trompowsky Attack ─────────────────────────────
    ("d2d4","g8f6","c1g5"):            ["g8e4","d7d5","c7c5","e7e6"],
    ("d2d4","g8f6","c1g5","g8e4"):     ["g5f4","g5e3","h2h4"],
    ("d2d4","g8f6","c1g5","d7d5"):     ["e2e3","b1c3","g1f3"],

    # ── London System ─────────────────────────────────
    ("d2d4","d7d5","g1f3"):            ["g8f6","e7e6","c7c5","c8f5","b8c6"],
    ("d2d4","d7d5","g1f3","g8f6"):     ["c1f4","e2e3","c2c4"],
    ("d2d4","d7d5","g1f3","g8f6","c1f4"): ["e7e6","c7c5","c8f5","b8c6"],
    ("d2d4","d7d5","g1f3","g8f6","c1f4","e7e6"): ["e2e3","b1d2","c2c3"],
    ("d2d4","g8f6","g1f3"):            ["e7e6","g7g6","d7d5","c7c5"],
    ("d2d4","g8f6","g1f3","e7e6"):     ["c1f4","e2e3","c2c4","g2g3"],
    ("d2d4","g8f6","g1f3","d7d5"):     ["c1f4","e2e3","c2c4"],

    # ── Torre Attack ──────────────────────────────────
    ("d2d4","g8f6","g1f3","e7e6","c1g5"): ["h7h6","c7c5","d7d5","b8c6"],
    ("d2d4","g8f6","g1f3","g7g6","c1g5"): ["f8g7","d7d5","c7c5"],

    # ── Colle System ──────────────────────────────────
    ("d2d4","d7d5","g1f3","g8f6","e2e3"): ["e7e6","c8f5","c7c5","b8c6"],
    ("d2d4","d7d5","g1f3","g8f6","e2e3","e7e6"): ["f1d3","b1d2","c2c3"],
    ("d2d4","d7d5","g1f3","g8f6","e2e3","e7e6","f1d3"): ["c7c5","b8c6","f8d6"],

    # ── Blackmar-Diemer Gambit ─────────────────────────
    ("d2d4","d7d5","e2e4"):            ["d5e4","e7e6","c7c6"],
    ("d2d4","d7d5","e2e4","d5e4"):     ["b1c3","f2f3"],
    ("d2d4","d7d5","e2e4","d5e4","b1c3"): ["g8f6","e7e5","e4f3"],
    ("d2d4","d7d5","e2e4","d5e4","b1c3","g8f6"): ["f2f3"],
    ("d2d4","d7d5","e2e4","d5e4","b1c3","g8f6","f2f3"): ["e4f3","c8f5","e7e6"],

    # ══════════════════════════════════════════════════
    # 1.c4 ENGLISH OPENING
    # ══════════════════════════════════════════════════

    ("c2c4",): ["e7e5","c7c5","g8f6","e7e6","d7d5","g7g6","f7f5"],
    ("c2c4","e7e5"):                   ["b1c3","g1f3","g2g3"],
    ("c2c4","e7e5","b1c3"):            ["g8f6","b8c6","f8c5","d7d6"],
    ("c2c4","e7e5","b1c3","g8f6"):     ["g1f3","g2g3"],
    ("c2c4","e7e5","b1c3","g8f6","g2g3"): ["d7d5","b8c6","f8b4"],
    ("c2c4","e7e5","b1c3","b8c6"):     ["g2g3","g1f3","e2e3"],
    ("c2c4","c7c5"):                   ["b1c3","g1f3","g2g3"],
    ("c2c4","c7c5","b1c3"):            ["b8c6","g8f6","g7g6"],
    ("c2c4","g8f6"):                   ["b1c3","g1f3","g2g3","d2d4"],
    ("c2c4","g8f6","g1f3"):            ["e7e6","g7g6","c7c5","d7d5","b7b6"],
    ("c2c4","g8f6","b1c3"):            ["e7e6","g7g6","c7c5","d7d5"],
    ("c2c4","e7e6"):                   ["b1c3","g1f3","g2g3"],
    ("c2c4","d7d5"):                   ["b1c3","g1f3","c4d5"],
    ("c2c4","d7d5","b1c3"):            ["g8f6","e7e6","c7c6","d5c4"],
    ("c2c4","d7d5","c4d5"):            ["g8f6","d8d5","e7e6"],
    # Symmetrical English
    ("c2c4","c7c5","g1f3"):            ["b8c6","g8f6","g7g6"],
    ("c2c4","c7c5","g1f3","g8f6"):     ["b1c3","d2d4","g2g3"],

    # ══════════════════════════════════════════════════
    # 1.Nf3 RETI OPENING
    # ══════════════════════════════════════════════════

    ("g1f3",): ["d7d5","g8f6","c7c5","e7e6","g7g6","f7f5","b8c6"],
    ("g1f3","d7d5"):                   ["c2c4","g2g3","d2d4","b2b3"],
    ("g1f3","d7d5","c2c4"):            ["d5c4","e7e6","c7c6","g8f6","c7c5"],
    ("g1f3","d7d5","c2c4","g8f6"):     ["b1c3","g2g3","d2d4"],
    ("g1f3","d7d5","g2g3"):            ["g8f6","c7c5","e7e6","c8f5"],
    ("g1f3","d7d5","g2g3","g8f6"):     ["f1g2","c2c4","d2d4"],
    ("g1f3","g8f6"):                   ["c2c4","g2g3","d2d4","b2b3"],
    ("g1f3","c7c5"):                   ["c2c4","g2g3","b2b3","e2e4"],
    ("g1f3","g7g6"):                   ["c2c4","d2d4","g2g3"],

    # ══════════════════════════════════════════════════
    # 1.b3 LARSEN'S OPENING
    # ══════════════════════════════════════════════════
    ("b2b3",): ["e7e5","d7d5","g8f6","c7c5","e7e6"],
    ("b2b3","e7e5"):                   ["c1b2","g1f3","e2e3"],
    ("b2b3","e7e5","c1b2"):            ["b8c6","g8f6","d7d6"],
    ("b2b3","d7d5"):                   ["c1b2","g1f3","e2e3"],

    # ══════════════════════════════════════════════════
    # 1.f4 BIRD'S OPENING
    # ══════════════════════════════════════════════════
    ("f2f4",): ["d7d5","g8f6","e7e5","c7c5","e7e6","g7g6"],
    ("f2f4","d7d5"):                   ["g1f3","e2e3","b2b3"],
    ("f2f4","e7e5"):                   ["f4e5"],  # From's Gambit
    ("f2f4","e7e5","f4e5"):            ["d7d6"],
    ("f2f4","e7e5","f4e5","d7d6"):     ["e5d6"],
    ("f2f4","g8f6"):                   ["g1f3","e2e3","b2b3"],

    # ══════════════════════════════════════════════════
    # 1.Nc3 VAN GEET / DUNST
    # ══════════════════════════════════════════════════
    ("b1c3",): ["d7d5","e7e5","g8f6","c7c5","e7e6","g7g6"],
    ("b1c3","d7d5"):                   ["e2e4","d2d4","g1f3"],
    ("b1c3","e7e5"):                   ["e2e4","g1f3","d2d4"],
    ("b1c3","g8f6"):                   ["e2e4","d2d4","g1f3"],

    # ══════════════════════════════════════════════════
    # ADDITIONAL GAMBITS & SIDELINES
    # ══════════════════════════════════════════════════

    # Budapest Gambit
    ("d2d4","g8f6","c2c4","e7e5"):     ["d4e5","d4d5"],
    ("d2d4","g8f6","c2c4","e7e5","d4e5"): ["f6g4","f6e4"],
    ("d2d4","g8f6","c2c4","e7e5","d4e5","f6g4"): ["g1f3","e2e4","c1f4"],

    # Albin Counter-Gambit
    ("d2d4","d7d5","c2c4","e7e5"):     ["d4e5","e5d5"],
    ("d2d4","d7d5","c2c4","e7e5","d4e5"): ["d5d4"],
    ("d2d4","d7d5","c2c4","e7e5","d4e5","d5d4"): ["g1f3","e2e3","b1a3"],

    # Staunton Gambit (vs Dutch)
    ("d2d4","f7f5","e2e4"):            ["f5e4"],
    ("d2d4","f7f5","e2e4","f5e4"):     ["b1c3","d1e2"],

    # Chigorin Defence
    ("d2d4","d7d5","c2c4","b8c6"):     ["g1f3","b1c3","e2e3"],
    ("d2d4","d7d5","c2c4","b8c6","b1c3"): ["e7e5","d5c4","g8f6"],

    # Nimzowitsch Defence (1.e4 Nc6)
    ("e2e4","b8c6"):                   ["d2d4","g1f3","b1c3"],
    ("e2e4","b8c6","d2d4"):            ["e7e5","d7d5","g8f6"],
    ("e2e4","b8c6","g1f3"):            ["d7d6","e7e5","g8f6"],

    # Owen's Defence (1.e4 b6)
    ("e2e4","b7b6"):                   ["d2d4","b1c3","g1f3"],
    ("e2e4","b7b6","d2d4"):            ["c8b7","e7e6","d7d5"],

    # St. George / Baker Defence (1.e4 a6)
    ("e2e4","a7a6"):                   ["d2d4","g1f3","b1c3"],
    ("e2e4","a7a6","d2d4"):            ["b7b5","e7e6","d7d5"],

    # Modern Defence (1.e4 g6)
    ("e2e4","g7g6"):                   ["d2d4","b1c3","g1f3"],
    ("e2e4","g7g6","d2d4"):            ["f8g7","d7d6"],
    ("e2e4","g7g6","d2d4","f8g7"):     ["b1c3","g1f3"],
    ("e2e4","g7g6","d2d4","f8g7","b1c3"): ["d7d6","c7c5","b8c6"],

    # Nimzowitsch-Larsen Attack
    ("b2b3","e7e5","c1b2","b8c6"):     ["e2e3","g1f3","c2c4"],
    ("b2b3","d7d5","c1b2","g8f6"):     ["e2e3","g1f3","f2f4"],

    # Sokolsky / Orangutan (1.b4)
    ("b2b4",): ["e7e5","d7d5","g8f6","c7c5","e7e6"],
    ("b2b4","e7e5"):                   ["c1b2","b4b5","a2a3"],
    ("b2b4","e7e5","c1b2"):            ["f8b4","g8f6","d7d6"],
    ("b2b4","d7d5"):                   ["c1b2","e2e3","b4b5"],
    ("b2b4","c7c5"):                   ["b4c5","b4b5"],

    # Grob Opening (1.g4)
    ("g2g4",): ["d7d5","e7e5","c7c5","g8f6"],
    ("g2g4","d7d5"):                   ["g1f3","c1g5","e2e3","f1g2"],
    ("g2g4","e7e5"):                   ["g1f3","f1g2","d2d3","h2h3"],

    # Polish Defence / Orangutan response
    ("d2d4","b7b5"):                   ["e2e4","g1f3","c2c4"],
    ("d2d4","b7b5","e2e4"):            ["c1b2","b4b7","b8a6"],

    # Reversed Sicilian / King's English continuation
    ("c2c4","e7e5","g1f3","b8c6","b1c3","g8f6","g2g3","d7d5"): ["c4d5","e2e4","d2d4"],

    # Symmetrical English — Four Knights
    ("c2c4","c7c5","b1c3","b8c6","g1f3","g8f6"): ["d2d4","g2g3","e2e3"],
    ("c2c4","c7c5","b1c3","b8c6","g1f3","g8f6","g2g3"): ["g7g6","d7d5","e7e6"],

    # Reti — King's Indian Attack setup
    ("g1f3","d7d5","g2g3","g8f6","f1g2"): ["e7e6","c7c6","c7c5","g7g6"],
    ("g1f3","d7d5","g2g3","g8f6","f1g2","e7e6"): ["e1g1","d2d3","d2d4"],

    # Reti — Catalan-like
    ("g1f3","g8f6","c2c4","e7e6","g2g3"): ["d7d5","b7b6","f8b4","c7c5"],
    ("g1f3","g8f6","c2c4","e7e6","g2g3","d7d5"): ["f1g2","e1g1","d2d4"],
}


def lookup_opening(move_history, bot_color='white'):
    key = tuple(move_history)
    whose_turn = 'white' if len(key) % 2 == 0 else 'black'
    if whose_turn != bot_color:
        return None
    candidates = OPENING_BOOK.get(key)
    if candidates:
        return random.choice(candidates)
    return None


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

learned_values = {}
_transposition_table = {}

def clear_transposition_table():
    global _transposition_table
    _transposition_table = {}

def load_brain():
    global learned_values
    try:
        with open("bot_brain.pkl", 'rb') as f:
            learned_values = pickle.load(f)
    except:
        learned_values = {}

def save_brain():
    with open("bot_brain.pkl", 'wb') as f:
        pickle.dump(learned_values, f)

def get_state_key(board):
    return "".join(["".join(row) for row in board])

# ── Optimized move generator ──────────────────────────────────────────────────
def get_all_moves(board, turn):
    moves = []
    is_white = (turn == 'white')
    enemy_pieces = BLACK_PIECES if is_white else WHITE_PIECES
    friendly_pieces = WHITE_PIECES if is_white else BLACK_PIECES

    for r in range(8):
        row = board[r]
        for c in range(8):
            p = row[c]
            if p == '.':
                continue
            if is_white and p not in WHITE_PIECES:
                continue
            if not is_white and p not in BLACK_PIECES:
                continue

            if p in ('♘', '♞'):
                for dr, dc in _KNIGHT_MOVES:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r, c, nr, nc))

            elif p in ('♔', '♚'):
                for dr, dc in _KING_MOVES:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r, c, nr, nc))

            elif p == '♙':
                if r > 0:
                    if board[r-1][c] == '.':
                        moves.append((r, c, r-1, c))
                        if r == 6 and board[r-2][c] == '.':
                            moves.append((r, c, r-2, c))
                    for dc in (-1, 1):
                        nc = c + dc
                        if 0 <= nc < 8 and board[r-1][nc] in BLACK_PIECES:
                            moves.append((r, c, r-1, nc))

            elif p == '♟':
                if r < 7:
                    if board[r+1][c] == '.':
                        moves.append((r, c, r+1, c))
                        if r == 1 and board[r+2][c] == '.':
                            moves.append((r, c, r+2, c))
                    for dc in (-1, 1):
                        nc = c + dc
                        if 0 <= nc < 8 and board[r+1][nc] in WHITE_PIECES:
                            moves.append((r, c, r+1, nc))

            else:
                # Sliding pieces — pick direction sets
                if p in ('♖', '♜'):
                    dirs = _ROOK_DIRS
                elif p in ('♗', '♝'):
                    dirs = _BISHOP_DIRS
                else:  # Queen
                    dirs = _QUEEN_DIRS

                for dr, dc in dirs:
                    nr, nc = r+dr, c+dc
                    while 0 <= nr < 8 and 0 <= nc < 8:
                        target = board[nr][nc]
                        if target == '.':
                            moves.append((r, c, nr, nc))
                        elif target in enemy_pieces:
                            moves.append((r, c, nr, nc))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc
    return moves


def is_endgame(board):
    piece_count = 0
    has_queen = False
    for row in board:
        for p in row:
            if p != '.':
                piece_count += 1
                if p in ('♕', '♛'):
                    has_queen = True
    return (not has_queen) or piece_count <= 12


def get_positional_score(board, endgame=None):
    score = 0.0
    if endgame is None:
        endgame = is_endgame(board)
    white_pawn_files = []
    black_pawn_files = []

    # Collect per-piece scores and pawn file data
    for r in range(8):
        row = board[r]
        for c in range(8):
            p = row[c]
            if p == '.':
                continue

            score += PIECE_VALUES.get(p, 0)

            is_white_p = p in WHITE_PIECES
            tr = r if is_white_p else (7 - r)
            sign = 1 if is_white_p else -1

            if p in ('♙', '♟'):
                score += sign * _PAWN_TABLE_T[tr][c]
                if is_white_p:
                    white_pawn_files.append(c)
                else:
                    black_pawn_files.append(c)
            elif p in ('♘', '♞'):
                score += sign * _KNIGHT_TABLE_T[tr][c]
            elif p in ('♗', '♝'):
                score += sign * _BISHOP_TABLE_T[tr][c]
            elif p in ('♖', '♜'):
                score += sign * _ROOK_TABLE_T[tr][c]
            elif p in ('♕', '♛'):
                score += sign * _QUEEN_TABLE_T[tr][c]
            elif p in ('♔', '♚'):
                king_table = _KING_END_T if endgame else _KING_MID_T
                score += sign * king_table[tr][c]

    # Pawn structure — doubled pawns
    wpf_counts = {}
    for f in white_pawn_files:
        wpf_counts[f] = wpf_counts.get(f, 0) + 1
    bpf_counts = {}
    for f in black_pawn_files:
        bpf_counts[f] = bpf_counts.get(f, 0) + 1

    for f, cnt in wpf_counts.items():
        if cnt > 1:
            score -= 0.3 * (cnt - 1)
        if (f-1) not in wpf_counts and (f+1) not in wpf_counts:
            score -= 0.2

    for f, cnt in bpf_counts.items():
        if cnt > 1:
            score += 0.3 * (cnt - 1)
        if (f-1) not in bpf_counts and (f+1) not in bpf_counts:
            score += 0.2

    # Rook open file bonus — build column pawn sets once
    white_pawn_file_set = set(white_pawn_files)
    black_pawn_file_set = set(black_pawn_files)

    for c in range(8):
        has_wp = c in white_pawn_file_set
        has_bp = c in black_pawn_file_set
        for r in range(8):
            p = board[r][c]
            if p == '♖':
                if not has_wp and not has_bp:
                    score += 0.3
                elif not has_wp:
                    score += 0.15
            elif p == '♜':
                if not has_wp and not has_bp:
                    score -= 0.3
                elif not has_bp:
                    score -= 0.15

    # Hanging piece penalty — build attacker sets once per color, O(n²) not O(n⁴)
    # For each square, record which enemy pieces attack it
    white_attacks = set()  # squares attacked by white
    black_attacks = set()  # squares attacked by black

    for ar in range(8):
        for ac in range(8):
            ap = board[ar][ac]
            if ap == '.':
                continue
            # Generate attacked squares for this piece
            if ap in ('♘', '♞'):
                for dr, dc in _KNIGHT_MOVES:
                    nr, nc = ar + dr, ac + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        (white_attacks if ap in WHITE_PIECES else black_attacks).add((nr, nc))
            elif ap in ('♔', '♚'):
                for dr, dc in _KING_MOVES:
                    nr, nc = ar + dr, ac + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        (white_attacks if ap in WHITE_PIECES else black_attacks).add((nr, nc))
            elif ap == '♙':
                for dc in (-1, 1):
                    nr, nc = ar - 1, ac + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        white_attacks.add((nr, nc))
            elif ap == '♟':
                for dc in (-1, 1):
                    nr, nc = ar + 1, ac + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        black_attacks.add((nr, nc))
            else:
                # Sliding pieces
                if ap in ('♖', '♜'):
                    dirs = _ROOK_DIRS
                elif ap in ('♗', '♝'):
                    dirs = _BISHOP_DIRS
                else:
                    dirs = _QUEEN_DIRS
                target_set = white_attacks if ap in WHITE_PIECES else black_attacks
                for dr, dc in dirs:
                    nr, nc = ar + dr, ac + dc
                    while 0 <= nr < 8 and 0 <= nc < 8:
                        target_set.add((nr, nc))
                        if board[nr][nc] != '.':
                            break
                        nr += dr
                        nc += dc

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.' or p not in PIECE_VALUES:
                continue
            pv = abs(PIECE_VALUES[p])
            if pv == 0:
                continue
            penalty = pv * 0.05
            if p in WHITE_PIECES and (r, c) in black_attacks:
                score -= penalty
            elif p in BLACK_PIECES and (r, c) in white_attacks:
                score += penalty

    return score


def _can_attack(board, fr, fc, tr, tc):
    """Quick check: can piece at (fr,fc) capture square (tr,tc)?"""
    p = board[fr][fc]
    if p == '.':
        return False
    dr = tr - fr
    dc = tc - fc

    if p in ('♘', '♞'):
        return (abs(dr), abs(dc)) in {(2,1),(1,2)}

    if p in ('♔', '♚'):
        return abs(dr) <= 1 and abs(dc) <= 1

    if p == '♙':
        return dr == -1 and abs(dc) == 1

    if p == '♟':
        return dr == 1 and abs(dc) == 1

    # Rooks / queens (orthogonal)
    if p in ('♖', '♜', '♕', '♛') and (dr == 0 or dc == 0):
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.':
                return False
            nr += step_r
            nc += step_c
        return True

    # Bishops / queens (diagonal)
    if p in ('♗', '♝', '♕', '♛') and abs(dr) == abs(dc):
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.':
                return False
            nr += step_r
            nc += step_c
        return True

    return False


def evaluate_board(board, state_key=None):
    if not state_key:
        state_key = get_state_key(board)
    endgame = is_endgame(board)
    positional = get_positional_score(board, endgame)
    knowledge = learned_values.get(state_key, 0)
    return positional + knowledge


# ── Alpha-beta minimax for stronger play ──────────────────────────────────────
def _minimax(board, depth, alpha, beta, maximizing):
    """Alpha-beta pruned minimax with transposition table. Returns score."""
    flat = get_state_key(board)
    if '♔' not in flat:
        return -500.0
    if '♚' not in flat:
        return 500.0

    if depth == 0:
        return evaluate_board(board, flat)

    # Transposition table lookup
    tt_key = (flat, depth, maximizing)
    tt_entry = _transposition_table.get(tt_key)
    if tt_entry is not None:
        flag, val = tt_entry
        if flag == 'exact':
            return val
        if flag == 'lower' and val >= beta:
            return val
        if flag == 'upper' and val <= alpha:
            return val

    turn = 'white' if maximizing else 'black'
    moves = get_all_moves(board, turn)

    if not moves:
        return evaluate_board(board, flat)

    # Move ordering: captures first (MVV-LVA style)
    def _priority(m):
        return abs(PIECE_VALUES.get(board[m[2]][m[3]], 0))

    moves.sort(key=_priority, reverse=True)

    orig_alpha = alpha
    if maximizing:
        best = -9999.0
        for sr, sc, er, ec in moves:
            orig, dest = board[sr][sc], board[er][ec]
            board[er][ec] = orig
            board[sr][sc] = '.'
            val = _minimax(board, depth - 1, alpha, beta, False)
            board[sr][sc] = orig
            board[er][ec] = dest
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        flag = 'exact' if best > orig_alpha else 'upper'
        _transposition_table[tt_key] = (flag, best)
        return best
    else:
        best = 9999.0
        orig_beta = beta
        for sr, sc, er, ec in moves:
            orig, dest = board[sr][sc], board[er][ec]
            board[er][ec] = orig
            board[sr][sc] = '.'
            val = _minimax(board, depth - 1, alpha, beta, True)
            board[sr][sc] = orig
            board[er][ec] = dest
            if val < best:
                best = val
            if best < beta:
                beta = best
            if alpha >= beta:
                break
        flag = 'exact' if best < orig_beta else 'lower'
        _transposition_table[tt_key] = (flag, best)
        return best


def select_move(board, turn, epsilon):
    moves = get_all_moves(board, turn)
    if not moves:
        return None

    if random.random() < epsilon:
        return random.choice(moves)

    maximizing = (turn == 'white')

    # Move ordering for root: captures first
    def _priority(m):
        return abs(PIECE_VALUES.get(board[m[2]][m[3]], 0))

    moves.sort(key=_priority, reverse=True)

    best_move = None
    best_score = -9999.0 if maximizing else 9999.0
    alpha = -9999.0
    beta = 9999.0

    for sr, sc, er, ec in moves:
        orig, dest = board[sr][sc], board[er][ec]
        board[er][ec] = orig
        board[sr][sc] = '.'
        # depth=1 for training speed; bump to 2-3 for stronger play
        val = _minimax(board, depth=1, alpha=alpha, beta=beta, maximizing=not maximizing)
        board[sr][sc] = orig
        board[er][ec] = dest

        if maximizing:
            if val > best_score:
                best_score = val
                best_move = (sr, sc, er, ec)
            if best_score > alpha:
                alpha = best_score
        else:
            if val < best_score:
                best_score = val
                best_move = (sr, sc, er, ec)
            if best_score < beta:
                beta = best_score

    return best_move


def run_self_play_training(games=100):
    load_brain()
    epsilon = 0.5

    for g in range(games):
        board = get_initial_board()
        clear_transposition_table()
        history = []
        turn = 'white'
        game_over = False
        result_score = 0

        for m_count in range(150):
            move = select_move(board, turn, epsilon)
            if not move:
                result_score = -5
                game_over = True
                break

            board[move[2]][move[3]], board[move[0]][move[1]] = board[move[0]][move[1]], '.'
            state_key = get_state_key(board)
            history.append(state_key)

            flat_board = "".join(["".join(row) for row in board])
            if '♔' not in flat_board:
                result_score = -50
                game_over = True
                break
            if '♚' not in flat_board:
                result_score = 50
                game_over = True
                break

            turn = 'black' if turn == 'white' else 'white'

        if not game_over:
            result_score = -10

        for i, state in enumerate(reversed(history)):
            reward = result_score * (DISCOUNT_FACTOR ** i)
            old_val = learned_values.get(state, 0)
            learned_values[state] = old_val + LEARNING_RATE * (reward - old_val)

        if (g + 1) % 1 == 0:
            print(f"Game {g+1} | Positions in Brain: {len(learned_values)}")
            save_brain()
            epsilon = max(0.1, epsilon * 0.99)

    save_brain()


# ══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE PLAY
# ══════════════════════════════════════════════════════════════════════════════

def print_board(board):
    print("\n  a b c d e f g h")
    print("  ─────────────────")
    for r in range(8):
        rank = 8 - r
        row_str = " ".join(board[r])
        print(f"{rank}│ {row_str} │{rank}")
    print("  ─────────────────")
    print("  a b c d e f g h\n")


def parse_move(move_str):
    """Parse algebraic notation like 'e2e4' or 'e2 e4'."""
    move_str = move_str.strip().replace(" ", "").lower()
    if len(move_str) != 4:
        return None
    try:
        fc = ord(move_str[0]) - ord('a')
        fr = 8 - int(move_str[1])
        tc = ord(move_str[2]) - ord('a')
        tr = 8 - int(move_str[3])
        if all(0 <= x < 8 for x in (fr, fc, tr, tc)):
            return (fr, fc, tr, tc)
    except ValueError:
        pass
    return None


def format_move(move):
    """Format a move tuple as algebraic notation."""
    fr, fc, tr, tc = move
    return f"{chr(ord('a')+fc)}{8-fr}{chr(ord('a')+tc)}{8-tr}"


def play_game():
    """Interactive game: human vs bot."""
    load_brain()
    print("\n" + "═"*50)
    print("   ♟  CHESS BOT  ♙")
    print("═"*50)
    print("Enter moves in format: e2e4 (from-to)")
    print("Commands: 'quit' to exit, 'train N' to train N games")
    print()

    while True:
        color_choice = input("Play as [w]hite or [b]lack? ").strip().lower()
        if color_choice in ('w', 'white', 'b', 'black'):
            human_color = 'white' if color_choice in ('w', 'white') else 'black'
            bot_color = 'black' if human_color == 'white' else 'white'
            break
        print("Please enter 'w' or 'b'.")

    print(f"\nYou play as {human_color.upper()}. Bot plays as {bot_color.upper()}.")

    diff = input("Bot difficulty: [1] Easy  [2] Medium  [3] Hard  (default 2): ").strip()
    depth_map = {'1': 1, '2': 2, '3': 3}
    search_depth = depth_map.get(diff, 2)
    epsilon = {'1': 0.3, '2': 0.05, '3': 0.0}.get(diff, 0.05)
    print(f"Difficulty set. Search depth: {search_depth}\n")

    board = get_initial_board()
    move_history = []
    turn = 'white'

    while True:
        print_board(board)
        flat = get_state_key(board)

        # Check game over
        if '♔' not in flat:
            print("♔ White king captured! BLACK WINS!")
            break
        if '♚' not in flat:
            print("♚ Black king captured! WHITE WINS!")
            break

        moves = get_all_moves(board, turn)
        if not moves:
            print(f"No moves for {turn}. Stalemate!")
            break

        print(f"{'─'*40}")
        print(f"  Turn: {turn.upper()}")

        if turn == human_color:
            # Human move
            while True:
                raw = input("  Your move (e.g. e2e4): ").strip()
                if raw.lower() == 'quit':
                    print("Thanks for playing!")
                    return
                if raw.lower().startswith('train'):
                    parts = raw.split()
                    n = int(parts[1]) if len(parts) > 1 else 50
                    print(f"Training {n} games...")
                    run_self_play_training(n)
                    print("Training done!")
                    continue

                parsed = parse_move(raw)
                if parsed is None:
                    print("  Invalid format. Use e.g. 'e2e4'")
                    continue
                if parsed not in moves:
                    print("  Illegal move. Try again.")
                    continue

                fr, fc, tr, tc = parsed
                board[tr][tc] = board[fr][fc]
                board[fr][fc] = '.'
                move_history.append(parsed)
                print(f"  You played: {format_move(parsed)}")
                break
        else:
            # Bot move — check opening book first
            book_move = lookup_opening(move_history, bot_color)
            if book_move and book_move in moves:
                chosen = book_move
                print(f"  Bot plays (book): {format_move(chosen)}")
            else:
                # Use minimax with configurable depth
                maximizing = (turn == 'white')
                best_move = None
                best_score = -9999.0 if maximizing else 9999.0
                alpha, beta = -9999.0, 9999.0

                def _priority(m):
                    return abs(PIECE_VALUES.get(board[m[2]][m[3]], 0))

                sorted_moves = sorted(moves, key=_priority, reverse=True)

                if random.random() < epsilon:
                    chosen = random.choice(moves)
                else:
                    for sr, sc, er, ec in sorted_moves:
                        orig, dest = board[sr][sc], board[er][ec]
                        board[er][ec] = orig
                        board[sr][sc] = '.'
                        val = _minimax(board, search_depth, alpha, beta, not maximizing)
                        board[sr][sc] = orig
                        board[er][ec] = dest
                        if maximizing:
                            if val > best_score:
                                best_score = val
                                best_move = (sr, sc, er, ec)
                            alpha = max(alpha, best_score)
                        else:
                            if val < best_score:
                                best_score = val
                                best_move = (sr, sc, er, ec)
                            beta = min(beta, best_score)
                    chosen = best_move or random.choice(moves)
                print(f"  Bot plays: {format_move(chosen)}")

            fr, fc, tr, tc = chosen
            board[tr][tc] = board[fr][fc]
            board[fr][fc] = '.'
            move_history.append(chosen)

        turn = 'black' if turn == 'white' else 'white'

    print("\nGame over. Thanks for playing!")


def main():
    print("\n" + "═"*50)
    print("   ♟  CHESS BOT  ♙")
    print("═"*50)
    print("1. Play vs Bot")
    print("2. Train Bot (self-play)")
    print("3. Quick train then play")
    print()

    choice = input("Choose [1/2/3]: ").strip()

    if choice == '1':
        play_game()
    elif choice == '2':
        n = input("How many training games? (default 500): ").strip()
        n = int(n) if n.isdigit() else 500
        print(f"Starting {n} self-play training games...")
        run_self_play_training(n)
        print("Training complete!")
    elif choice == '3':
        n = input("Quick train games before playing? (default 100): ").strip()
        n = int(n) if n.isdigit() else 100
        print(f"Training {n} games first...")
        run_self_play_training(n)
        print("Done! Starting game...\n")
        play_game()
    else:
        print("Invalid choice. Starting game directly.")
        play_game()


if __name__ == "__main__":
    main()
