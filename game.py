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

    def is_knight(self):
        return self in [Piece.WHITE_KNIGHT, Piece.BLACK_KNIGHT]

    def is_bishop(self):
        return self in [Piece.WHITE_BISHOP, Piece.BLACK_BISHOP]


class Move:
    start_x: int
    start_y: int
    end_x: int | None
    end_y: int | None
    piece: Piece
    promotion: Piece | None

    def __init__(
        self,
        start_x: int,
        start_y: int,
        piece: Piece,
        end_x: int | None = None,
        end_y: int | None = None,
        promotion: Piece | None = None,
    ):
        self.start_x = start_x
        self.start_y = start_y
        self.piece = piece
        self.end_x = end_x
        self.end_y = end_y
        self.promotion = promotion

    def to_string(self) -> str:
        s = ""
        match self.start_x:
            case 0:
                s += "a"
            case 1:
                s += "b"
            case 2:
                s += "c"
        match self.start_y:
            case 0:
                s += "3"
            case 1:
                s += "2"
            case 2:
                s += "1"
        match self.end_x:
            case None:
                return s
            case 0:
                s += "-a"
            case 1:
                s += "-b"
            case 2:
                s += "-c"
        match self.end_y:
            case 0:
                s += "3"
            case 1:
                s += "2"
            case 2:
                s += "1"

        if self.promotion:
            if self.promotion.is_rook():
                s += "R"
            elif self.promotion.is_knight():
                s += "K"
            elif self.promotion.is_bishop():
                s += "B"
        return s

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


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
        print(
            f"  a b c\n"
            f"3 {self.board[0][0].unicode_character()} {self.board[0][1].unicode_character()} {self.board[0][2].unicode_character()} 3\n"
            f"2 {self.board[1][0].unicode_character()} {self.board[1][1].unicode_character()} {self.board[1][2].unicode_character()} 2\n"
            f"1 {self.board[2][0].unicode_character()} {self.board[2][1].unicode_character()} {self.board[2][2].unicode_character()} 1\n"
            f"  a b c\n"
        )

    def allowed_moves(self) -> list[Move]:
        allowed_moves: list[Move] = []

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
            allowed_moves.append(Move(start_x=x, start_y=y, piece=Piece.WHITE_PAWN))

        # Piece movement
        for x in range(self.max_x):
            for y in range(self.max_y):
                piece = self.board[y][x]
                if piece.is_black() and self.turn:
                    continue
                if piece.is_white() and not self.turn:
                    continue

                if piece in [Piece.WHITE_PAWN, Piece.BLACK_PAWN]:
                    self.pawn_movements(allowed_moves, x, y)
                if piece in [Piece.WHITE_KNIGHT, Piece.BLACK_KNIGHT]:
                    self.knight_movements(allowed_moves, x, y)
                if piece in [Piece.WHITE_BISHOP, Piece.BLACK_BISHOP]:
                    self.bischop_movement(allowed_moves, x, y)
                if piece in [Piece.WHITE_ROOK, Piece.BLACK_ROOK]:
                    self.rook_movement(allowed_moves, x, y)

        return allowed_moves

    def pawn_movements(self, allowed_moves: list[Move], x: int, y: int) -> None:

        directions = [0, 1, -1]
        for dx in directions:
            dy = -1 if self.turn else 1
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.max_x and 0 <= ny < self.max_y):
                continue

            target_piece = self.board[ny][nx]
            is_empty = target_piece.is_empty()
            is_opposite_color = (target_piece.is_white() and not self.turn) or (
                target_piece.is_black() and self.turn
            )

            if (is_empty and dx == 0) or (is_opposite_color and dx != 0):
                pawn_movement = Move(
                    start_x=x, start_y=y, piece=self.board[y][x], end_x=nx, end_y=ny
                )
                if ny in [0, 2]:
                    allowed_moves.extend(self.promote(pawn_movement))
                else:
                    allowed_moves.append(pawn_movement)

    def knight_movements(self, allowed_moves: list[Move], x: int, y: int) -> None:
        diffs = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
        for dx, dy in diffs:
            nx, ny = x + dx, y + dy
            if nx >= 0 and nx < self.max_x and ny >= 0 and ny < self.max_y:
                target_piece = self.board[ny][nx]
                is_empty = target_piece == Piece.EMPTY
                is_opposite_color = (target_piece.is_white() and not self.turn) or (
                    target_piece.is_black() and self.turn
                )
                if is_empty or is_opposite_color:
                    allowed_moves.append(Move(x, y, self.board[y][x], nx, ny))

    def bischop_movement(self, allowed_moves: list[Move], x: int, y: int) -> None:
        diffs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dx, dy in diffs:
            nx, ny = x + dx, y + dy
            while nx >= 0 and nx < self.max_x and ny >= 0 and ny < self.max_y:
                target_piece = self.board[ny][nx]
                is_empty = target_piece == Piece.EMPTY
                is_opposite_color = (target_piece.is_white() and not self.turn) or (
                    target_piece.is_black() and self.turn
                )
                if is_empty or is_opposite_color:
                    allowed_moves.append(Move(x, y, self.board[y][x], nx, ny))
                if not is_empty:
                    break
                nx, ny = nx + dx, ny + dy

    def rook_movement(self, allowed_moves: list[Move], x: int, y: int) -> None:
        diffs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dx, dy in diffs:
            nx, ny = x + dx, y + dy
            while nx >= 0 and nx < self.max_x and ny >= 0 and ny < self.max_y:
                target_piece = self.board[ny][nx]
                is_empty = target_piece == Piece.EMPTY
                is_opposite_color = (target_piece.is_white() and not self.turn) or (
                    target_piece.is_black() and self.turn
                )
                if is_empty or is_opposite_color:
                    allowed_moves.append(Move(x, y, self.board[y][x], nx, ny))
                if not is_empty:
                    break
                nx, ny = nx + dx, ny + dy

    def promote(self, move: Move) -> list[Move]:
        allowed_moves: list[Move] = [move]
        # You can only promote to a piece if it is not already on the board
        piece_flags = {
            "R": Piece.WHITE_ROOK,
            "K": Piece.WHITE_KNIGHT,
            "B": Piece.WHITE_BISHOP,
        }
        if not self.turn:
            piece_flags = {
                "R": Piece.BLACK_ROOK,
                "K": Piece.BLACK_KNIGHT,
                "B": Piece.BLACK_BISHOP,
            }

        for piece, piece_type in piece_flags.items():
            if not any(piece_type in row for row in self.board):
                allowed_moves.append(
                    Move(move.start_x, move.start_y, piece_type, move.end_x, move.end_y)
                )

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
