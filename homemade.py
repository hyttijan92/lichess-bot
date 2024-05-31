"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""

from __future__ import annotations
import chess
from chess.engine import PlayResult, Limit
import random
from functools import partial

import chess.engine
from lib.engine_wrapper import MinimalEngine
from lib.types import MOVE, HOMEMADE_ARGS_TYPE
import logging
import threading


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


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



class IterativeDeepening(ExampleEngine):

    def timeout_occured(self):
        logger.debug("Timeout occured.")
        self.timeout = True
    
    def computation_time(self, board: chess.Board, time_limit: Limit):
        if board.turn == chess.WHITE and time_limit.white_inc is not None:
            if time_limit.white_inc == 0:
                if time_limit.white_clock > time_limit.black_clock:
                    return min(time_limit.white_clock-time_limit.black_clock, 10.0)
                else:
                    return 1.0
            else:
                return min(time_limit.white_inc, 15.0)
        elif board.turn == chess.BLACK and time_limit.black_inc is not None:
            if time_limit.black_inc == 0:
                if time_limit.black_clock > time_limit.white_clock:
                    return min(time_limit.black_clock-time_limit.white_clock, 10.0)
                else:
                    return 1.0
            else:
                return min(time_limit.black_inc, 15.0)
        else:
            return 10.0

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        self.timeout = False
        MAX_DEPTH = 100
        move = None
        try:
            seconds_to_compute = self.computation_time(board, time_limit)
            logger.debug("Calculating next move for {} seconds".format(seconds_to_compute))
            timer = threading.Timer(seconds_to_compute, self.timeout_occured)
            timer.start()
            for i in range(2, MAX_DEPTH):
                logger.debug("Currently analyzing depth:{}".format(i))
                move = self.decide(board, i)
            timer.cancel()
            return move
        except TimeoutError:
            if move is None:
                logger.debug("Choosing a random move")
                return list(board.legal_moves)[0]
            else:
                return move

    def decide(self, board: chess.Board, depth: int):
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
                    board, depth, alpha, beta, False)
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
                    board, depth, alpha, beta, True)
                if value < min_value or min_move == None:
                    min_value = value
                    min_move = move
                board.pop()
                if min_value < alpha:
                    break
                beta = min(beta, min_value)
            return PlayResult(min_move, None)
                     
    def alphabeta(self, board: chess.Board, depth: int, alpha: int, beta: int, is_player_maximizing: bool) -> int:
        if self.timeout:
            raise TimeoutError
        elif depth == 0 or board.is_game_over():
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

