import array
from enum import Enum


class Piece(Enum):
    EMPTY = 0
    WHITE_PAWN = 1
    WHITE_ROOK = 2
    WHITE_KNIGHT = 3
    WHITE_BISHOP = 4
    BLACK_PAWN = 5
    BLACK_ROOK = 6
    BLACK_KNIGHT = 7
    BLACK_BISHOP = 8

    def unicode_character(self):
        match self:
            case Piece.EMPTY:
                return " "
            case Piece.WHITE_PAWN:
                return "♙"
            case Piece.WHITE_ROOK:
                return "♖"
            case Piece.WHITE_KNIGHT:
                return "♘"
            case Piece.WHITE_BISHOP:
                return "♗"
            case Piece.BLACK_PAWN:
                return "♟"
            case Piece.BLACK_ROOK:
                return "♜"
            case Piece.BLACK_KNIGHT:
                return "♞"
            case Piece.BLACK_BISHOP:
                return "♝"

    def is_white(self):
        return self in [
            Piece.WHITE_PAWN,
            Piece.WHITE_ROOK,
            Piece.WHITE_KNIGHT,
            Piece.WHITE_BISHOP,
        ]

    def is_black(self):
        return self in [
            Piece.BLACK_PAWN,
            Piece.BLACK_ROOK,
            Piece.BLACK_KNIGHT,
            Piece.BLACK_BISHOP,
        ]

    def is_empty(self):
        return self == Piece.EMPTY

    def is_pawn(self):
        return self in [Piece.WHITE_PAWN, Piece.BLACK_PAWN]

    def is_rook(self):
        return self in [Piece.WHITE_ROOK, Piece.BLACK_ROOK]


# move notation:
# Place pawn on x,y -> xy
# Move piece from x,y to x,y -> xy-xy
# Promote pawn to piece at x,y -> xy-xyK, xy-xyR, xy-xyB


class Board:
    max_x = 3
    max_y = 3
    board: list[list[Piece]]
    turn: bool = True

    def __init__(self):
        self.board = [
            [Piece.EMPTY for x in range(self.max_x)] for y in range(self.max_y)
        ]

    def print_board(self):
        for y in range(self.max_y):
            for x in range(self.max_x):
                print(self.board[y][x].unicode_character(), end="")
            print()

    def allowed_moves(self) -> list[str]:
        allowed_moves: list[str] = []

        # Pawn placements
        empty_spots = [
            (x, y)
            for x in range(self.max_x)
            for y in range(self.max_y)
            if self.board[y][x] == Piece.EMPTY
        ]
        empty_spots_on_your_side = [
            (x, y)
            for x, y in empty_spots
            if (y != 0 and self.turn) or (y != 2 and not self.turn)
        ]
        for x, y in empty_spots_on_your_side:
            allowed_moves.append(f"{x}{y}")

        # Piece movement
        for x in range(self.max_x):
            for y in range(self.max_y):
                piece = self.board[x][y]
                if piece.is_black() and self.turn:
                    continue
                if piece.is_white() and not self.turn:
                    continue

                if piece in [Piece.WHITE_PAWN, Piece.BLACK_PAWN]:
                    self.pawn_movements(allowed_moves, x, y)
                if piece in [Piece.WHITE_KNIGHT, Piece.BLACK_KNIGHT]:
                    self.knight_movements(allowed_moves, x, y)

        return allowed_moves

    def pawn_movements(self, allowed_moves, x, y):
        directions = [0, 1, -1]
        for dx in directions:
            dy = -1 if self.turn else 1
            nx, ny = x + dx, y + dy

            target_piece = self.board[ny][nx]
            is_empty = target_piece == Piece.EMPTY
            is_opposite_color = (target_piece.is_white() and not self.turn) or (
                target_piece.is_black() and self.turn
            )

            if (is_empty and dx == 0) or (is_opposite_color and dx != 0):
                pawn_movement = f"{x}{y}-{nx}{ny}"
                if (ny == 0 and self.turn) or (ny == 2 and not self.turn):
                    allowed_moves.extend(self.promote(pawn_movement))
                else:
                    allowed_moves.append(pawn_movement)

    def knight_movements(self, allowed_moves, x, y):
        # knight move diff coordinates:
        diffs = [(1,2), (2,1), (-1,2), (-2,1), (1,-2), (2,-1), (-1,-2), (-2,-1)]
        for dx, dy in diffs:
            nx, ny = x + dx, y + dy
            if nx >= 0 and nx < self.max_x and ny >= 0 and ny < self.max_y:
                target_piece = self.board[ny][nx]
                is_empty = target_piece == Piece.EMPTY
                is_opposite_color = (target_piece.is_white() and not self.turn) or (
                    target_piece.is_black() and self.turn
                )
                if is_empty or is_opposite_color:
                    allowed_moves.append(f"{x}{y}-{nx}{ny}")

    def promote(self, move: str) -> list[str]:
        allowed_moves: list[str] = [move]
        piece_flags = {"R": False, "K": False, "B": False}

        for r in self.board:
            for pos in r:
                if pos == Piece.WHITE_ROOK or pos == Piece.BLACK_ROOK:
                    piece_flags["R"] = True
                elif pos == Piece.WHITE_KNIGHT or pos == Piece.BLACK_KNIGHT:
                    piece_flags["K"] = True
                elif pos == Piece.WHITE_BISHOP or pos == Piece.BLACK_BISHOP:
                    piece_flags["B"] = True

        for piece, encountered in piece_flags.items():
            if not encountered:
                allowed_moves.append(move + piece)

        return allowed_moves


if __name__ == "__main__":
    board = Board()
    board.board[0][0] = Piece.BLACK_PAWN
    board.board[0][1] = Piece.BLACK_ROOK
    board.board[0][2] = Piece.BLACK_KNIGHT
    board.board[1][0] = Piece.WHITE_PAWN
    board.board[1][1] = Piece.WHITE_ROOK
    board.board[2][2] = Piece.WHITE_KNIGHT
    board.print_board()
    print(board.allowed_moves())
