"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""

from __future__ import annotations
import chess
from chess.engine import PlayResult, Limit
import random
from functools import partial

from lib.engine_wrapper import MinimalEngine
from lib.types import MOVE, HOMEMADE_ARGS_TYPE
import logging


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


# Bot names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)
CHESS_PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 99999
}

PAWN_PIECE_SQUARE_TABLES_BLACK = [0,  0,  0,  0,  0,  0,  0,  0,
                                  50, 50, 50, 50, 50, 50, 50, 50,
                                  10, 10, 20, 30, 30, 20, 10, 10,
                                  5,  5, 10, 25, 25, 10,  5,  5,
                                  0,  0,  0, 20, 20,  0,  0,  0,
                                  5, -5, -10,  0,  0, -10, -5,  5,
                                  5, 10, 10, -20, -20, 10, 10,  5,
                                  0,  0,  0,  0,  0,  0,  0,  0]
PAWN_PIECE_SQUARE_TABLES_WHITE = PAWN_PIECE_SQUARE_TABLES_BLACK[::-1]
KNIGHT_PIECE_SQUARE_TABLES_BLACK = [-50, -40, -30, -30, -30, -30, -40, -50,
                                    -40, -20,  0,  0,  0,  0, -20, -40,
                                    -30,  0, 10, 15, 15, 10,  0, -30,
                                    -30,  5, 15, 20, 20, 15,  5, -30,
                                    -30,  0, 15, 20, 20, 15,  0, -30,
                                    -30,  5, 10, 15, 15, 10,  5, -30,
                                    -40, -20,  0,  5,  5,  0, -20, -40,
                                    -50, -40, -30, -30, -30, -30, -40, -50]
KNIGHT_PIECE_SQUARE_TABLES_WHITE = KNIGHT_PIECE_SQUARE_TABLES_BLACK[::-1]
BISHOP_PIECE_SQUARE_TABLES_BLACK = [-20, -10, -10, -10, -10, -10, -10, -20,
                                    -10,  0,  0,  0,  0,  0,  0, -10,
                                    -10,  0,  5, 10, 10,  5,  0, -10,
                                    -10,  5,  5, 10, 10,  5,  5, -10,
                                    -10,  0, 10, 10, 10, 10,  0, -10,
                                    -10, 10, 10, 10, 10, 10, 10, -10,
                                    -10,  5,  0,  0,  0,  0,  5, -10,
                                    -20, -10, -10, -10, -10, -10, -10, -20]

BISHOP_PIECE_SQUARE_TABLES_WHITE = BISHOP_PIECE_SQUARE_TABLES_BLACK[::-1]
ROOK_PIECE_SQUARE_TABLES_BLACK = [0,  0,  0,  0,  0,  0,  0,  0,
                                  5, 10, 10, 10, 10, 10, 10,  5,
                                  -5,  0,  0,  0,  0,  0,  0, -5,
                                  -5,  0,  0,  0,  0,  0,  0, -5,
                                  -5,  0,  0,  0,  0,  0,  0, -5,
                                  -5,  0,  0,  0,  0,  0,  0, -5,
                                  -5,  0,  0,  0,  0,  0,  0, -5,
                                  0,  0,  0,  5,  5,  0,  0,  0]
ROOK_PIECE_SQUARE_TABLES_WHITE = ROOK_PIECE_SQUARE_TABLES_BLACK[::-1]

class AlphaBeta(MinimalEngine):

    
    def search(self, board: chess.Board, time_limit: chess.engine.Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        
        alpha = -99999999
        beta = 99999999
        legal_moves = list(board.legal_moves)
        sort_initial_moves_partial = partial(self.sort_initial_moves, board)
        random.shuffle(legal_moves)
        if board.turn == chess.WHITE:
            max_value = -99999999
            max_move = None
            legal_moves.sort(reverse=False, key=sort_initial_moves_partial)
            for move in legal_moves:
                board.push(move)
                value = self.alphabeta(
                    board, 3, alpha, beta, False)
                if value > max_value or max_move == None:
                    max_value = value
                    max_move = move
                board.pop()
                if max_value > beta:
                    break
                alpha = max(alpha, max_value)
            return PlayResult(max_move, None) 
        else:
            min_value = 99999999
            min_move = None
            legal_moves.sort(reverse=False, key=sort_initial_moves_partial)
            for move in legal_moves:
                board.push(move)
                value = self.alphabeta(
                    board, 3, alpha, beta, True)
                if value < min_value or min_move == None:
                    min_value = value
                    min_move = move
                board.pop()
                if min_value < alpha:
                    break
                beta = min(beta, min_value)
            return PlayResult(min_move, None)                
    def alphabeta(self, board: chess.Board, depth: int, alpha: int, beta: int, is_player_maximizing: bool) -> int:
        if depth == 0 or board.is_game_over():
            if is_player_maximizing:
                return self.heuristic(board)-depth
            else:
                return self.heuristic(board)+depth
        elif is_player_maximizing:
            max_value = -99999999
            for move in board.legal_moves:
                board.push(move)
                max_value = max(max_value, self.alphabeta(
                    board, depth-1, alpha, beta, False))
                board.pop()
                if max_value > beta:
                    break
                alpha = max(alpha, max_value)
            return max_value
        else:
            min_value = 99999999
            for move in board.legal_moves:
                board.push(move)
                min_value = min(min_value, self.alphabeta(
                    board, depth-1, alpha, beta, True))
                board.pop()
                if min_value < alpha:
                    break
                beta = min(beta, min_value)
            return min_value


    def sort_initial_moves(self, board: chess.Board, move: chess.Move) -> int:
        board.push(move)
        result = self.heuristic(board)
        board.pop()
        return result

    def heuristic(self, board: chess.Board) -> int:
        white_score = 0
        black_score = 0
        if board.is_checkmate():
            if board.outcome().winner == chess.WHITE:
                return 9999999
            else:
                return -9999999
        elif board.is_stalemate() or board.is_insufficient_material():
            return 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == chess.WHITE:
                    white_score += CHESS_PIECE_VALUES[piece.piece_type]
                    if (piece.piece_type == chess.PAWN):
                        white_score += PAWN_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.KNIGHT):
                        white_score += KNIGHT_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.BISHOP):
                        white_score += BISHOP_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.ROOK):
                        white_score += ROOK_PIECE_SQUARE_TABLES_WHITE[square]
                else:
                    black_score += CHESS_PIECE_VALUES[piece.piece_type]
                    if (piece.piece_type == chess.PAWN):
                        black_score += PAWN_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.KNIGHT):
                        black_score += KNIGHT_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.BISHOP):
                        black_score += BISHOP_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.ROOK):
                        black_score += ROOK_PIECE_SQUARE_TABLES_BLACK[square]

        return white_score-black_score
