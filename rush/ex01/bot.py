import random
import pickle

# settings
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
WHITE_PIECES = {'♙', '♖', '♘', '♗', '♕', '♔'}
BLACK_PIECES = {'♟', '♜', '♞', '♝', '♛', '♚'}
PIECE_VALUES = {
    '♙': 1, '♘': 3, '♗': 3, '♖': 5, '♕': 9, '♔': 100,
    '♟': -1, '♞': -3, '♝': -3, '♜': -5, '♛': -9, '♚': -100
}

# encourage center csontrol, piece development, good outposts
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

# king safetys
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

OPENING_BOOK = {
    # WHITE OPENINGS

    (): [
        (6, 4, 4, 4),   # 1. e4
        (6, 3, 4, 3),   # 1. d4
        (6, 2, 4, 2),   # 1. c4
        (7, 6, 5, 5),   # 1. Nf3
    ],

    # 1.e4 e5 → 2.Nf3
    ((6,4,4,4),(1,4,3,4),): [(7,6,5,5)],
    # 1.e4 e5 2.Nf3 Nc6 → 3.Bb5 (Ruy Lopez)
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),): [(7,5,5,3)],
    # 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 → 4.Ba4
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),(7,5,5,3),(1,0,2,0),): [(5,3,4,0)],
    # 1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 → 4.O-O
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),(7,5,5,3),(0,6,2,5),): [(7,4,7,6)],
    # 1.e4 e5 2.Nf3 Nf6 (Petroff) → 3.Nxe5
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,6,2,5),): [(5,5,3,4)],

    # 1.e4 c5 (Sicilian) → 2.Nf3
    ((6,4,4,4),(1,2,3,2),): [(7,6,5,5)],
    # 1.e4 c5 2.Nf3 d6 → 3.d4
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),(1,3,2,3),): [(6,3,4,3)],
    # 1.e4 c5 2.Nf3 Nc6 → 3.d4
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),(0,1,2,2),): [(6,3,4,3)],
    # 1.e4 c5 2.Nf3 e6 → 3.d4
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),(1,4,2,4),): [(6,3,4,3)],
    # Sicilian 3.d4 cxd4 → 4.Nxd4
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),(1,3,2,3),(6,3,4,3),(3,2,4,3),): [(5,5,4,3)],

    # 1.e4 e6 (French) → 2.d4
    ((6,4,4,4),(1,4,2,4),): [(6,3,4,3)],
    # 1.e4 e6 2.d4 d5 → 3.Nc3
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),(1,3,3,3),): [(7,1,5,2)],
    # 1.e4 e6 2.d4 d5 3.Nc3 Nf6 → 4.Bg5
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),(1,3,3,3),(7,1,5,2),(0,6,2,5),): [(7,5,4,5)],

    # 1.e4 c6 (Caro-Kann) → 2.d4
    ((6,4,4,4),(1,2,2,2),): [(6,3,4,3)],
    # 1.e4 c6 2.d4 d5 → 3.Nc3
    ((6,4,4,4),(1,2,2,2),(6,3,4,3),(1,3,3,3),): [(7,1,5,2)],
    # 1.e4 c6 2.d4 d5 3.Nc3 dxe4 → 4.Nxe4
    ((6,4,4,4),(1,2,2,2),(6,3,4,3),(1,3,3,3),(7,1,5,2),(3,3,4,4),): [(5,2,4,4)],

    # 1.e4 d5 (Scandinavian) → 2.exd5
    ((6,4,4,4),(1,3,3,3),): [(4,4,3,3)],
    # 1.e4 d5 2.exd5 Qxd5 → 3.Nc3
    ((6,4,4,4),(1,3,3,3),(4,4,3,3),(0,3,3,3),): [(7,1,5,2)],

    # 1.e4 g6 (Modern/Pirc) → 2.d4
    ((6,4,4,4),(1,6,2,6),): [(6,3,4,3)],
    # 1.e4 g6 2.d4 Bg7 → 3.Nc3
    ((6,4,4,4),(1,6,2,6),(6,3,4,3),(0,5,1,6),): [(7,1,5,2)],

    # 1.d4 d5 → 2.c4 (Queen's Gambit)
    ((6,3,4,3),(1,3,3,3),): [(6,2,4,2)],
    # 1.d4 d5 2.c4 e6 → 3.Nc3 (QGD)
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(1,4,2,4),): [(7,1,5,2)],
    # 1.d4 d5 2.c4 c6 → 3.Nf3 (Slav)
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(1,2,2,2),): [(7,6,5,5)],
    # 1.d4 d5 2.c4 dxc4 → 3.e3 (QGA)
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(3,3,4,2),): [(6,4,5,4)],
    # 1.d4 Nf6 → 2.c4
    ((6,3,4,3),(0,6,2,5),): [(6,2,4,2)],
    # 1.d4 Nf6 2.c4 e6 → 3.Nc3 (Nimzo/QGD)
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,4,2,4),): [(7,1,5,2)],
    # 1.d4 Nf6 2.c4 g6 → 3.Nc3 (King's Indian)
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,6,2,6),): [(7,1,5,2)],
    # 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 → 4.e4
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,6,2,6),(7,1,5,2),(0,5,1,6),): [(6,4,4,4)],
    # 1.d4 f5 (Dutch) → 2.c4
    ((6,3,4,3),(1,5,3,5),): [(6,2,4,2)],
    # 1.d4 e6 → 2.c4
    ((6,3,4,3),(1,4,2,4),): [(6,2,4,2)],

    # 1.Nf3 d5 → 2.c4
    ((7,6,5,5),(1,3,3,3),): [(6,2,4,2)],
    # 1.Nf3 e5 → 2.e4
    ((7,6,5,5),(1,4,3,4),): [(6,4,4,4)],
    # 1.Nf3 Nf6 → 2.c4
    ((7,6,5,5),(0,6,2,5),): [(6,2,4,2)],

    # 1.c4 e5 → 2.Nf3
    ((6,2,4,2),(1,4,3,4),): [(7,6,5,5)],
    # 1.c4 Nf6 → 2.Nf3
    ((6,2,4,2),(0,6,2,5),): [(7,6,5,5)],
    # 1.c4 c5 → 2.Nf3
    ((6,2,4,2),(1,2,3,2),): [(7,6,5,5)],

    # BLACK OPENINGS

    # ── Replies to 1.e4 ─────────────────────────────────────────────────────
    # 1.e4 → 1...e5 or 1...c5 or 1...e6 or 1...c6
    ((6,4,4,4),): [
        (1,4,3,4),   # 1...e5  (Open Game)
        (1,2,3,2),   # 1...c5  (Sicilian)
        (1,4,2,4),   # 1...e6  (French)
        (1,2,2,2),   # 1...c6  (Caro-Kann)
    ],

    # ── vs 1.e4 e5 lines ────────────────────────────────────────────────────
    # 1.e4 e5 2.Nf3 → 2...Nc6
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),): [(0,1,2,2)],
    # 1.e4 e5 2.Nf3 Nc6 3.Bb5 (Ruy Lopez) → 3...a6
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),(7,5,5,3),): [(1,0,2,0)],
    # 1.e4 e5 2.Nf3 Nc6 3.Bc4 (Italian) → 3...Bc5
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),(7,5,4,2),): [(0,5,2,3)],
    # 1.e4 e5 2.Nf3 Nc6 3.d4 (Scotch) → 3...exd4
    ((6,4,4,4),(1,4,3,4),(7,6,5,5),(0,1,2,2),(6,3,4,3),): [(3,4,4,3)],
    # 1.e4 e5 2.Nc3 → 2...Nf6 (Vienna)
    ((6,4,4,4),(1,4,3,4),(7,1,5,2),): [(0,6,2,5)],
    # 1.e4 e5 2.Bc4 → 2...Nf6 (Bishop's Opening)
    ((6,4,4,4),(1,4,3,4),(7,5,4,2),): [(0,6,2,5)],
    # 1.e4 e5 2.f4 (King's Gambit) → 2...exf4 (accepted)
    ((6,4,4,4),(1,4,3,4),(6,5,4,5),): [(3,4,4,5)],

    # ── vs Sicilian (1.e4 c5) ───────────────────────────────────────────────
    # 1.e4 c5 2.Nf3 → 2...d6 (Dragon/Najdorf setup)
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),): [(1,3,2,3)],
    # 1.e4 c5 2.Nf3 d6 3.d4 cxd4 → 4...Nf6
    ((6,4,4,4),(1,2,3,2),(7,6,5,5),(1,3,2,3),(6,3,4,3),(3,2,4,3),(5,5,4,3),): [(0,6,2,5)],
    # 1.e4 c5 2.Nc3 → 2...Nc6
    ((6,4,4,4),(1,2,3,2),(7,1,5,2),): [(0,1,2,2)],
    # 1.e4 c5 2.c3 (Alapin) → 2...d5
    ((6,4,4,4),(1,2,3,2),(6,2,5,2),): [(1,3,3,3)],

    # ── vs French (1.e4 e6) ─────────────────────────────────────────────────
    # 1.e4 e6 2.d4 → 2...d5
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),): [(1,3,3,3)],
    # 1.e4 e6 2.d4 d5 3.Nc3 → 3...Nf6
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),(1,3,3,3),(7,1,5,2),): [(0,6,2,5)],
    # 1.e4 e6 2.d4 d5 3.Nc3 Nf6 4.Bg5 → 4...Be7 (Classical French)
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),(1,3,3,3),(7,1,5,2),(0,6,2,5),(7,5,4,5),): [(0,5,1,6)],
    # 1.e4 e6 2.d4 d5 3.e5 (Advance) → 3...c5
    ((6,4,4,4),(1,4,2,4),(6,3,4,3),(1,3,3,3),(4,4,3,4),): [(1,2,3,2)],

    # ── vs Caro-Kann (1.e4 c6) ──────────────────────────────────────────────
    # 1.e4 c6 2.d4 → 2...d5
    ((6,4,4,4),(1,2,2,2),(6,3,4,3),): [(1,3,3,3)],
    # 1.e4 c6 2.d4 d5 3.Nc3 → 3...dxe4
    ((6,4,4,4),(1,2,2,2),(6,3,4,3),(1,3,3,3),(7,1,5,2),): [(3,3,4,4)],
    # 1.e4 c6 2.d4 d5 3.e5 (Advance) → 3...Bf5
    ((6,4,4,4),(1,2,2,2),(6,3,4,3),(1,3,3,3),(4,4,3,4),): [(0,5,2,5)],

    # ── Replies to 1.d4 ─────────────────────────────────────────────────────
    # 1.d4 → 1...Nf6 or 1...d5 or 1...f5 (Dutch)
    ((6,3,4,3),): [
        (0,6,2,5),   # 1...Nf6  (Indian systems)
        (1,3,3,3),   # 1...d5   (Queen's Gambit responses)
        (1,5,3,5),   # 1...f5   (Dutch)
    ],

    # ── vs Queen's Gambit (1.d4 d5 2.c4) ───────────────────────────────────
    # 1.d4 d5 2.c4 → 2...e6 (QGD)
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),): [(1,4,2,4)],
    # 1.d4 d5 2.c4 e6 3.Nc3 → 3...Nf6
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(1,4,2,4),(7,1,5,2),): [(0,6,2,5)],
    # 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 → 4...Be7
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(1,4,2,4),(7,1,5,2),(0,6,2,5),(7,5,4,5),): [(0,5,1,6)],
    # 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.e3 → 4...c5 (Tartakower)
    ((6,3,4,3),(1,3,3,3),(6,2,4,2),(1,4,2,4),(7,1,5,2),(0,6,2,5),(6,4,5,4),): [(1,2,3,2)],

    # ── vs King's Indian / Grünfeld (1.d4 Nf6 2.c4) ─────────────────────────
    # 1.d4 Nf6 2.c4 → 2...g6 (King's Indian)
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),): [(1,6,2,6)],
    # 1.d4 Nf6 2.c4 g6 3.Nc3 → 3...Bg7
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,6,2,6),(7,1,5,2),): [(0,5,1,6)],
    # 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 → 4...d6
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,6,2,6),(7,1,5,2),(0,5,1,6),(6,4,4,4),): [(1,3,2,3)],
    # 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 → 5...0-0 (castle)
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,6,2,6),(7,1,5,2),(0,5,1,6),(6,4,4,4),(1,3,2,3),(7,6,5,5),): [(0,4,0,6)],

    # ── vs Nimzo-Indian (1.d4 Nf6 2.c4 e6 3.Nc3) ────────────────────────────
    # 1.d4 Nf6 2.c4 e6 3.Nc3 → 3...Bb4 (Nimzo-Indian)
    ((6,3,4,3),(0,6,2,5),(6,2,4,2),(1,4,2,4),(7,1,5,2),): [(0,5,3,1)],

    # ── vs Dutch (1.d4 f5) ──────────────────────────────────────────────────
    # 1.d4 f5 2.c4 → 2...Nf6
    ((6,3,4,3),(1,5,3,5),(6,2,4,2),): [(0,6,2,5)],
    # 1.d4 f5 2.c4 Nf6 3.Nc3 → 3...e6
    ((6,3,4,3),(1,5,3,5),(6,2,4,2),(0,6,2,5),(7,1,5,2),): [(1,4,2,4)],

    # ── Replies to 1.c4 (English) ───────────────────────────────────────────
    # 1.c4 → 1...e5
    ((6,2,4,2),): [(1,4,3,4)],
    # 1.c4 e5 2.Nf3 → 2...Nc6
    ((6,2,4,2),(1,4,3,4),(7,6,5,5),): [(0,1,2,2)],
    # 1.c4 e5 2.Nc3 → 2...Nf6
    ((6,2,4,2),(1,4,3,4),(7,1,5,2),): [(0,6,2,5)],
    # 1.c4 Nf6 2.Nf3 → 2...e6
    ((6,2,4,2),(0,6,2,5),(7,6,5,5),): [(1,4,2,4)],
    # 1.c4 c5 (Symmetrical) 2.Nf3 → 2...Nf6
    ((6,2,4,2),(1,2,3,2),(7,6,5,5),): [(0,6,2,5)],

    # ── Replies to 1.Nf3 (Réti) ─────────────────────────────────────────────
    # 1.Nf3 → 1...d5
    ((7,6,5,5),): [(1,3,3,3)],
    # 1.Nf3 d5 2.c4 → 2...e6
    ((7,6,5,5),(1,3,3,3),(6,2,4,2),): [(1,4,2,4)],
    # 1.Nf3 d5 2.g3 → 2...Nf6
    ((7,6,5,5),(1,3,3,3),(6,6,5,6),): [(0,6,2,5)],
    # 1.Nf3 Nf6 2.c4 → 2...e6
    ((7,6,5,5),(0,6,2,5),(6,2,4,2),): [(1,4,2,4)],

    # ── Replies to other first moves ─────────────────────────────────────────
    # 1.g3 → 1...d5
    ((6,6,5,6),): [(1,3,3,3)],
    # 1.b3 → 1...e5
    ((6,1,5,1),): [(1,4,3,4)],
    # 1.f4 (Bird's) → 1...d5
    ((6,5,4,5),): [(1,3,3,3)],
    # 1.Nc3 → 1...d5
    ((7,1,5,2),): [(1,3,3,3)],
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

def get_all_moves(board, turn):
    moves = []
    is_white = (turn == 'white')
    enemy_pieces = BLACK_PIECES if is_white else WHITE_PIECES
    friendly_pieces = WHITE_PIECES if is_white else BLACK_PIECES

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.' or (is_white and p not in WHITE_PIECES) or (not is_white and p not in BLACK_PIECES):
                continue

            dirs = []
            if p in {'♖', '♜', '♕', '♛'}: dirs += [(0,1),(0,-1),(1,0),(-1,0)]
            if p in {'♗', '♝', '♕', '♛'}: dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]

            if p in {'♘', '♞'}:
                for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p in {'♔', '♚'}:
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<8 and 0<=nc<8 and board[nr][nc] not in friendly_pieces:
                        moves.append((r,c,nr,nc))
            elif p == '♙':
                if r > 0 and board[r-1][c] == '.': moves.append((r,c,r-1,c))
                if r == 6 and board[r-1][c] == '.' and board[r-2][c] == '.': moves.append((r,c,r-2,c))
                for dc in [-1, 1]:
                    if r > 0 and 0 <= c+dc < 8 and board[r-1][c+dc] in BLACK_PIECES: moves.append((r,c,r-1,c+dc))
            elif p == '♟':
                if r < 7 and board[r+1][c] == '.': moves.append((r,c,r+1,c))
                if r == 1 and board[r+1][c] == '.' and board[r+2][c] == '.': moves.append((r,c,r+2,c))
                for dc in [-1, 1]:
                    if r < 7 and 0 <= c+dc < 8 and board[r+1][c+dc] in WHITE_PIECES: moves.append((r,c,r+1,c+dc))

            for dr, dc in dirs:
                nr, nc = r+dr, c+dc
                while 0<=nr<8 and 0<=nc<8:
                    if board[nr][nc] == '.': moves.append((r,c,nr,nc))
                    elif board[nr][nc] in enemy_pieces:
                        moves.append((r,c,nr,nc))
                        break
                    else: break
                    nr, nc = nr+dr, nc+dc
    return moves


def is_endgame(board):
    pieces = [p for row in board for p in row if p != '.']
    queens = [p for p in pieces if p in {'♕','♛'}]
    return len(queens) == 0 or len(pieces) <= 12


def get_positional_score(board):
    score = 0.0
    endgame = is_endgame(board)

    # pawn file structures
    white_pawn_files = []
    black_pawn_files = []

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.':
                continue

            val = PIECE_VALUES.get(p, 0)
            score += val

            is_white_p = p in WHITE_PIECES
            tr = r if is_white_p else (7 - r)
            sign = 1 if is_white_p else -1

            if p in {'♙', '♟'}:
                score += sign * PAWN_TABLE[tr][c]
                if is_white_p: white_pawn_files.append(c)
                else: black_pawn_files.append(c)
            elif p in {'♘', '♞'}:
                score += sign * KNIGHT_TABLE[tr][c]
            elif p in {'♗', '♝'}:
                score += sign * BISHOP_TABLE[tr][c]
            elif p in {'♖', '♜'}:
                score += sign * ROOK_TABLE[tr][c]
            elif p in {'♕', '♛'}:
                score += sign * QUEEN_TABLE[tr][c]
            elif p in {'♔', '♚'}:
                king_table = KING_TABLE_END if endgame else KING_TABLE_MID
                score += sign * king_table[tr][c]

    # pawn structure penalties
    # doubled pawns
    for f in set(white_pawn_files):
        if white_pawn_files.count(f) > 1:
            score -= 0.3 * (white_pawn_files.count(f) - 1)
    for f in set(black_pawn_files):
        if black_pawn_files.count(f) > 1:
            score += 0.3 * (black_pawn_files.count(f) - 1)

    # isolated pawns (no friendly pawn on adjacent files)
    for f in set(white_pawn_files):
        if not any(af in white_pawn_files for af in [f-1, f+1]):
            score -= 0.2
    for f in set(black_pawn_files):
        if not any(af in black_pawn_files for af in [f-1, f+1]):
            score += 0.2

    # rook openfile bonus
    for c in range(8):
        col_pieces = [board[r][c] for r in range(8) if board[r][c] != '.']
        has_white_pawn = '♙' in col_pieces
        has_black_pawn = '♟' in col_pieces
        for r in range(8):
            p = board[r][c]
            if p == '♖':
                if not has_white_pawn and not has_black_pawn:
                    score += 0.3   # fully open file
                elif not has_white_pawn:
                    score += 0.15  # semi open file
            elif p == '♜':
                if not has_white_pawn and not has_black_pawn:
                    score -= 0.3
                elif not has_black_pawn:
                    score -= 0.15

    # hanging piece penalty

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            is_white_p = p in WHITE_PIECES
            attacker_color = 'black' if is_white_p else 'white'
            attacker_pieces = BLACK_PIECES if is_white_p else WHITE_PIECES
            # check if any enemy can capture this square
            for ar in range(8):
                for ac in range(8):
                    ap = board[ar][ac]
                    if ap not in attacker_pieces: continue
                    # can ap capture (r,c)?
                    if _can_attack(board, ar, ac, r, c):
                        pv = abs(PIECE_VALUES.get(p, 0))
                        # penalty scaled by piece value
                        penalty = pv * 0.05
                        score += penalty if not is_white_p else -penalty
                        break  # count each piece as hanging once

    return score


def _can_attack(board, fr, fc, tr, tc):

    """Quick check: can piece at (fr,fc) capture square (tr,tc)?"""
    p = board[fr][fc]
    if p == '.': return False
    dr, dc = tr - fr, tc - fc

    if p in {'♘', '♞'}:
        return (abs(dr), abs(dc)) in {(2,1),(1,2)}

    if p in {'♔', '♚'}:
        return abs(dr) <= 1 and abs(dc) <= 1

    if p == '♙':
        return dr == -1 and abs(dc) == 1

    if p == '♟':
        return dr == 1 and abs(dc) == 1

    # Sliding pieces
    if p in {'♖', '♜', '♕', '♛'} and (dr == 0 or dc == 0):
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += step_r; nc += step_c
        return True

    if p in {'♗', '♝', '♕', '♛'} and abs(dr) == abs(dc):
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        nr, nc = fr + step_r, fc + step_c
        while (nr, nc) != (tr, tc):
            if board[nr][nc] != '.': return False
            nr += step_r; nc += step_c
        return True

    return False


def evaluate_board(board, state_key=None):
    if not state_key: state_key = get_state_key(board)
    positional = get_positional_score(board)
    knowledge = learned_values.get(state_key, 0)
    return positional + knowledge


def select_move(board, turn, epsilon):
    moves = get_all_moves(board, turn)
    if not moves: return None

    if random.random() < epsilon:
        return random.choice(moves)

    # move order: check, captures, etc.
    def move_priority(m):
        sr, sc, er, ec = m
        dest = board[er][ec]
        # captures get a bonus proportional to victim value
        capture_bonus = abs(PIECE_VALUES.get(dest, 0)) * 2
        return capture_bonus

    moves.sort(key=move_priority, reverse=True)

    scored_moves = []
    for m in moves:
        sr, sc, er, ec = m
        orig, dest = board[sr][sc], board[er][ec]
        board[er][ec], board[sr][sc] = orig, '.'
        score = evaluate_board(board)
        scored_moves.append((score, m))
        board[sr][sc], board[er][ec] = orig, dest

    scored_moves.sort(key=lambda x: x[0], reverse=(turn == 'white'))
    return scored_moves[0][1]


def run_self_play_training(games=100):
    load_brain()
    epsilon = 0.5

    for g in range(games):
        board = get_initial_board()
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

        if (g + 1) % 50 == 0:
            print(f"Game {g+1} | Positions in Brain: {len(learned_values)}")
            save_brain()
            epsilon = max(0.1, epsilon * 0.99)

    save_brain()

if __name__ == "__main__":
    run_self_play_training(2000)
