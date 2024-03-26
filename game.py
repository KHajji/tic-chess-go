import os
from enum import Enum
import re


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
        x_mapping = {0: "a", 1: "b", 2: "c"}
        y_mapping = {0: "3", 1: "2", 2: "1"}
        promotion_mapping = {
            Piece.WHITE_ROOK: "R",
            Piece.WHITE_KNIGHT: "K",
            Piece.WHITE_BISHOP: "B",
            Piece.BLACK_ROOK: "R",
            Piece.BLACK_KNIGHT: "K",
            Piece.BLACK_BISHOP: "B",
        }

        s = x_mapping.get(self.start_x, "") + y_mapping.get(self.start_y, "")
        if self.end_x is not None and self.end_y is not None:
            s += "-" + x_mapping.get(self.end_x, "") + y_mapping.get(self.end_y, "")

        if self.promotion:
            s += promotion_mapping.get(self.promotion, "")

        return s

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        if isinstance(other, Move):
            return (
                self.start_x == other.start_x
                and self.start_y == other.start_y
                and self.piece == other.piece
                and self.end_x == other.end_x
                and self.end_y == other.end_y
                and self.promotion == other.promotion
            )
        return False


class Game:
    max_x = 3
    max_y = 3
    board: list[list[Piece]]
    turn: bool = True

    def __init__(self):
        self.board = [
            [Piece.EMPTY for x in range(self.max_x)] for y in range(self.max_y)
        ]

    def __repr__(self):
        s = (
            f"  a b c\n"
            f"3 {self.board[0][0].unicode_character()} {self.board[0][1].unicode_character()} {self.board[0][2].unicode_character()} 3\n"
            f"2 {self.board[1][0].unicode_character()} {self.board[1][1].unicode_character()} {self.board[1][2].unicode_character()} 2\n"
            f"1 {self.board[2][0].unicode_character()} {self.board[2][1].unicode_character()} {self.board[2][2].unicode_character()} 1\n"
            f"  a b c\n"
            f"{'White' if self.turn else 'Black'} to move"
        )
        if self.in_check():
            s += "\nYou are in check!"

        return s

    def allowed_moves(self) -> list[Move]:
        allowed_moves: list[Move] = []

        # Piece movement
        for x in range(self.max_x):
            for y in reversed(range(self.max_y)):
                piece = self.board[y][x]
                if piece.is_black() and self.turn:
                    continue
                if piece.is_white() and not self.turn:
                    continue

                if piece == Piece.EMPTY and (
                    (y != 0 and self.turn) or (y != 2 and not self.turn)
                ):  # Pawn placements
                    placement_pawn = Piece.WHITE_PAWN if self.turn else Piece.BLACK_PAWN
                    allowed_moves.append(
                        Move(start_x=x, start_y=y, piece=placement_pawn)
                    )

                if piece in [Piece.WHITE_PAWN, Piece.BLACK_PAWN]:
                    allowed_moves.extend(self.pawn_movements(x, y))
                if piece in [Piece.WHITE_KNIGHT, Piece.BLACK_KNIGHT]:
                    allowed_moves.extend(self.knight_movements(x, y))
                if piece in [Piece.WHITE_BISHOP, Piece.BLACK_BISHOP]:
                    allowed_moves.extend(self.bischop_movement(x, y))
                if piece in [Piece.WHITE_ROOK, Piece.BLACK_ROOK]:
                    allowed_moves.extend(self.rook_movement(x, y))

        # Filter out moves that would put you in check
        allowed_moves = [
            move for move in allowed_moves if not self.would_put_in_check(move)
        ]
        return allowed_moves

    def pawn_movements(self, x: int, y: int) -> list[Move]:
        allowed_moves: list[Move] = []
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
        return allowed_moves

    def knight_movements(self, x: int, y: int) -> list[Move]:
        allowed_moves: list[Move] = []
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
        return allowed_moves

    def bischop_movement(self, x: int, y: int) -> list[Move]:
        allowed_moves: list[Move] = []
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
        return allowed_moves

    def rook_movement(self, x: int, y: int) -> list[Move]:
        allowed_moves: list[Move] = []
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
        return allowed_moves

    def promote(self, move: Move) -> list[Move]:
        allowed_moves: list[Move] = [move]
        # You can only promote to a piece if it is not already on the board
        pieces = [
            Piece.WHITE_ROOK,
            Piece.WHITE_KNIGHT,
            Piece.WHITE_BISHOP,
        ]
        if not self.turn:
            pieces = [
                Piece.BLACK_ROOK,
                Piece.BLACK_KNIGHT,
                Piece.BLACK_BISHOP,
            ]

        for piece in pieces:
            if not any(piece in row for row in self.board):
                allowed_moves.append(
                    Move(
                        move.start_x, move.start_y, piece, move.end_x, move.end_y, piece
                    )
                )
        return allowed_moves

    def execute_move(self, move: Move) -> None:
        # Execute placement moves
        if move.end_x is None or move.end_y is None:
            self.board[move.start_y][move.start_x] = move.piece
            self.turn = not self.turn
            return
        # Execute movement moves
        self.board[move.end_y][move.end_x] = move.piece
        self.board[move.start_y][move.start_x] = Piece.EMPTY
        self.turn = not self.turn

    def would_put_in_check(self, move: Move) -> bool:
        # Simulate the move
        old_board = [row.copy() for row in self.board]
        old_turn = self.turn
        self.execute_move(move)
        # Check if the move would put you in check and revert turn
        self.turn = not self.turn
        in_check = self.in_check()
        # Revert the move
        self.board = old_board
        self.turn = old_turn
        return in_check

    def in_check(self) -> bool:
        # You are in check if the opponent has three pieces in a row
        def piece_of_opponent(piece: Piece) -> bool:
            return (piece.is_white() and not self.turn) or (
                piece.is_black() and self.turn
            )

        # check rows
        for row in self.board:
            if all(piece_of_opponent(piece) for piece in row):
                return True

        # check columns
        for c in range(3):
            column = [self.board[0][c], self.board[1][c], self.board[2][c]]
            if all(piece_of_opponent(piece) for piece in column):
                return True
        # check diagonals
        if all(piece_of_opponent(self.board[i][i]) for i in range(3)):
            return True
        if all(piece_of_opponent(self.board[i][2 - i]) for i in range(3)):
            return True

        return False

    def check_mate(self) -> bool:
        return self.in_check() and not self.allowed_moves()

    def stalemate(self) -> bool:
        return not self.in_check() and not self.allowed_moves()


def main():
    game = Game()  # Assuming Game is your main class
    while True:
        os.system("clear")
        print(game)  # Print the current state of the board
        allowed_moves = game.allowed_moves()
        if not allowed_moves:
            if game.check_mate():
                winner = "Black" if game.turn else "White"
                print(f"Checkmate, {winner} wins!")
            elif game.stalemate():
                print("Stalemate!")
            break
        print("Allowed moves:")
        for i, move in enumerate(allowed_moves):
            print(f"{i}: {move}")
        try:
            move_index = int(input("Enter the index of your move: "))
            if 0 <= move_index < len(allowed_moves):
                game.execute_move(allowed_moves[move_index])
            else:
                print("Invalid move index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


if __name__ == "__main__":
    main()
