"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""

from __future__ import annotations
import chess
from chess.engine import PlayResult, Limit
import random
from functools import partial
import copy
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


MID_GAME_CHESS_PIECE_VALUES = {
    chess.PAWN: 82,
    chess.KNIGHT: 337,
    chess.BISHOP: 365,
    chess.ROOK: 477,
    chess.QUEEN: 1025,
    chess.KING: 99999
}
END_GAME_CHESS_PIECE_VALUES = {
    chess.PAWN: 94,
    chess.KNIGHT: 281,
    chess.BISHOP: 297,
    chess.ROOK: 512,
    chess.QUEEN: 936,
    chess.KING: 99999
}
MID_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK = [0, 0, 0, 0, 0, 0, 0, 0,
                                           98, 134,  61,  95,  68, 126, 34, -11,
                                           -6,   7,  26,  31,  65,  56, 25, -20,
                                           -14,  13,   6,  21,  23,  12, 17, -23,
                                           -27,  -2,  -5,  12,  17,   6, 10, -25,
                                           -26,  -4,  -4, -10,   3,   3, 33, -12,
                                           -35,  -1, -20, -23, -15,  24, 38, -22,
                                           0,   0,   0,   0,   0,   0,  0,   0]

MID_GAME_PAWN_PIECE_SQUARE_TABLES_WHITE = MID_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK[::-1]
END_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK = [0,   0,   0,   0,   0,   0,   0,   0,
                                           178, 173, 158, 134, 147, 132, 165, 187,
                                           94, 100,  85,  67,  56,  53,  82,  84,
                                           32,  24,  13,   5,  -2,   4,  17,  17,
                                           13,   9,  -3,  -7,  -7,  -8,   3,  -1,
                                           4,   7,  -6,   1,   0,  -5,  -1,  -8,
                                           13,   8,   8,  10,  13,   0,   2,  -7,
                                           0,   0,   0,   0,   0,   0,   0,   0]
END_GAME_PAWN_PIECE_SQUARE_TABLES_WHITE = END_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK[::-1]
MID_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK = [-167, -89, -34, -49,  61, -97, -15, -107,
                                             -73, -41,  72,  36,  23,  62,   7,  -17,
                                             -47,  60,  37,  65,  84, 129,  73,   44,
                                             -9,  17,  19,  53,  37,  69,  18,   22,
                                             -13,   4,  16,  13,  28,  19,  21,   -8,
                                             -23,  -9,  12,  10,  19,  17,  25,  -16,
                                             -29, -53, -12,  -3,  -1,  18, -14,  -19,
                                             -105, -21, -58, -33, -17, -28, -19,  -23]
MID_GAME_KNIGHT_PIECE_SQUARE_TABLES_WHITE = MID_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK[::-1]
END_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK = [-58, -38, -13, -28, -31, -27, -63, -99,
                                             -25,  -8, -25,  -2,  -9, -25, -24, -52,
                                             -24, -20,  10,   9,  -1,  -9, -19, -41,
                                             -17,   3,  22,  22,  22,  11,   8, -18,
                                             -18,  -6,  16,  25,  16,  17,   4, -18,
                                             -23,  -3,  -1,  15,  10,  -3, -20, -22,
                                             -42, -20, -10,  -5,  -2, -20, -23, -44,
                                             -29, -51, -23, -15, -22, -18, -50, -64]
END_GAME_KNIGHT_PIECE_SQUARE_TABLES_WHITE = END_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK[::-1]

MID_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK = [-29,   4, -82, -37, -25, -42,   7,  -8,
                                             -26,  16, -18, -13,  30,  59,  18, -47,
                                             -16,  37,  43,  40,  35,  50,  37,  -2,
                                             -4,   5,  19,  50,  37,  37,   7,  -2,
                                             -6,  13,  13,  26,  34,  12,  10,   4,
                                             0,  15,  15,  15,  14,  27,  18,  10,
                                             4,  15,  16,   0,   7,  21,  33,   1,
                                             -33,  -3, -14, -21, -13, -12, -39, -21]
MID_GAME_BISHOP_PIECE_SQUARE_TABLES_WHITE = MID_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK[::-1]

END_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK = [-14, -21, -11,  -8, -7,  -9, -17, -24,
                                             -8,  -4,   7, -12, -3, -13,  -4, -14,
                                             2,  -8,   0,  -1, -2,   6,   0,   4,
                                             -3,   9,  12,   9, 14,  10,   3,   2,
                                             -6,   3,  13,  19,  7,  10,  -3,  -9,
                                             -12,  -3,   8,  10, 13,   3,  -7, -15,
                                             -14, -18,  -7,  -1,  4,  -9, -15, -27,
                                             -23,  -9, -23,  -5, -9, -16,  -5, -17]

END_GAME_BISHOP_PIECE_SQUARE_TABLES_WHITE = END_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK[::-1]

MID_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK = [32,  42,  32,  51, 63,  9,  31,  43,
                                           27,  32,  58,  62, 80, 67,  26,  44,
                                           -5,  19,  26,  36, 17, 45,  61,  16,
                                           -24, -11,   7,  26, 24, 35,  -8, -20,
                                           -36, -26, -12,  -1,  9, -7,   6, -23,
                                           -45, -25, -16, -17,  3,  0,  -5, -33,
                                           -44, -16, -20,  -9, -1, 11,  -6, -71,
                                           -19, -13,   1,  17, 16,  7, -37, -26]
MID_GAME_ROOK_PIECE_SQUARE_TABLES_WHITE = MID_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK[::-1]

END_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK = [13, 10, 18, 15, 12,  12,   8,   5,
                                           11, 13, 13, 11, -3,   3,   8,   3,
                                           7,  7,  7,  5,  4,  -3,  -5,  -3,
                                           4,  3, 13,  1,  2,   1,  -1,   2,
                                           3,  5,  8,  4, -5,  -6,  -8, -11,
                                           -4,  0, -5, -1, -7, -12,  -8, -16,
                                           -6, -6,  0,  2, -9,  -9, -11,  -3,
                                           -9,  2,  3, -1, -5, -13,   4, -20]
END_GAME_ROOK_PIECE_SQUARE_TABLES_WHITE = END_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK[::-1]

MID_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK = [-28,   0,  29,  12,  59,  44,  43,  45,
                                            -24, -39,  -5,   1, -16,  57,  28,  54,
                                            -13, -17,   7,   8,  29,  56,  47,  57,
                                            -27, -27, -16, -16,  -1,  17,  -2,   1,
                                            -9, -26,  -9, -10,  -2,  -4,   3,  -3,
                                            -14,   2, -11,  -2,  -5,   2,  14,   5,
                                            -35,  -8,  11,   2,   8,  15,  -3,   1,
                                            -1, -18,  -9,  10, -15, -25, -31, -50]
MID_GAME_QUEEN_PIECE_SQUARE_TABLES_WHITE = MID_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK[::-1]
END_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK = [-9,  22,  22,  27,  27,  19,  10,  20,
                                            -17,  20,  32,  41,  58,  25,  30,   0,
                                            -20,   6,   9,  49,  47,  35,  19,   9,
                                            3,  22,  24,  45,  57,  40,  57,  36,
                                            -18,  28,  19,  47,  31,  34,  39,  23,
                                            -16, -27,  15,   6,   9,  17,  10,   5,
                                            -22, -23, -30, -16, -16, -23, -36, -32,
                                            -33, -28, -22, -43,  -5, -32, -20, -41]
END_GAME_QUEEN_PIECE_SQUARE_TABLES_WHITE = END_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK[::-1]
MID_GAME_KING_PIECE_SQUARE_TABLES_BLACK = [-65,  23,  16, -15, -56, -34,   2,  13,
                                           29,  -1, -20,  -7,  -8,  -4, -38, -29,
                                           -9,  24,   2, -16, -20,   6,  22, -22,
                                           -17, -20, -12, -27, -30, -25, -14, -36,
                                           -49,  -1, -27, -39, -46, -44, -33, -51,
                                           -14, -14, -22, -46, -44, -30, -15, -27,
                                           1,   7,  -8, -64, -43, -16,   9,   8,
                                           -15,  36,  12, -54,   8, -28,  24,  14]
MID_GAME_KING_PIECE_SQUARE_TABLES_WHITE = MID_GAME_KING_PIECE_SQUARE_TABLES_BLACK[::-1]
END_GAME_KING_PIECE_SQUARE_TABLES_BLACK = [-74, -35, -18, -18, -11,  15,   4, -17,
                                           -12,  17,  14,  17,  17,  38,  23,  11,
                                           10,  17,  23,  15,  20,  45,  44,  13,
                                           -8,  22,  24,  27,  26,  33,  26,   3,
                                           -18,  -4,  21,  24,  27,  23,   9, -11,
                                           -19,  -3,  11,  21,  23,  16,   7,  -9,
                                           -27, -11,   4,  13,  14,   4,  -5, -17,
                                           -53, -34, -21, -11, -28, -14, -24, -43]
END_GAME_KING_PIECE_SQUARE_TABLES_WHITE = END_GAME_KING_PIECE_SQUARE_TABLES_BLACK[::-1]


class IterativeDeepening(ExampleEngine):

    def timeout_occured(self):
        logger.debug("Timeout occured.")
        self.timeout = True

    def computation_time(self, board: chess.Board, time_limit: Limit):
        if board.turn == chess.WHITE and time_limit.white_inc is not None:
            if time_limit.white_inc == 0:
                if time_limit.white_clock > time_limit.black_clock:
                    return time_limit.white_clock-time_limit.black_clock
                else:
                    return 1.0
            else:
                if time_limit.white_clock > time_limit.black_clock:
                    logger.debug(time_limit.white_clock-time_limit.black_clock)
                    return (time_limit.white_clock-time_limit.black_clock)/4+time_limit.white_inc
                else:
                    return time_limit.white_inc
        elif board.turn == chess.BLACK and time_limit.black_inc is not None:
            if time_limit.black_inc == 0:
                if time_limit.black_clock > time_limit.white_clock:
                    return time_limit.black_clock-time_limit.white_clock
                else:
                    return 1.0
            else:
                if time_limit.black_clock > time_limit.white_clock:
                    return (time_limit.black_clock-time_limit.white_clock)/4 + time_limit.black_inc
                else:
                    return time_limit.black_inc
        else:
            return 20.0

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        self.timeout = False
        MAX_DEPTH = 100
        self.move = None
        original_board = copy.deepcopy(board)
        try:
            seconds_to_compute = self.computation_time(board, time_limit)
            logger.debug("Calculating next move for {} seconds".format(
                seconds_to_compute))
            timer = threading.Timer(seconds_to_compute, self.timeout_occured)
            timer.start()
            for i in range(1, MAX_DEPTH):
                self.counter = 0
                logger.debug("Currently analyzing depth:{}".format(i))
                self.move = self.decide(board, i)
                logger.debug("Analyzed {} positions".format(self.counter))
                self.counter = 0
            timer.cancel()
            return self.move
        except TimeoutError:
            if self.move is None:
                logger.debug("Choosing a random move")
                return PlayResult(list(original_board.legal_moves)[0], None)
            else:
                return self.move

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
            if self.move is not None:
                legal_moves.remove(self.move.move)
                legal_moves.insert(0, self.move.move)
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
            if self.move is not None:
                legal_moves.remove(self.move.move)
                legal_moves.insert(0, self.move.move)
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
        game_phase = 0
        game_phase_inc = [0, 0, 1, 1, 1, 1, 2, 2, 4, 4, 0, 0]
        middle_game_white_score = 0
        end_game_white_score = 0
        middle_game_black_score = 0
        end_game_black_score = 0
        self.counter += 1
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
                game_phase += game_phase_inc[piece.piece_type]
                if piece.color == chess.WHITE:
                    middle_game_white_score += MID_GAME_CHESS_PIECE_VALUES[piece.piece_type]
                    end_game_white_score += END_GAME_CHESS_PIECE_VALUES[piece.piece_type]
                    if (piece.piece_type == chess.PAWN):
                        middle_game_white_score += MID_GAME_PAWN_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_PAWN_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.KNIGHT):
                        middle_game_white_score += MID_GAME_KNIGHT_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_KNIGHT_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.BISHOP):
                        middle_game_white_score += MID_GAME_BISHOP_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_BISHOP_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.ROOK):
                        middle_game_white_score += MID_GAME_ROOK_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_ROOK_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.QUEEN):
                        middle_game_white_score += MID_GAME_QUEEN_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_QUEEN_PIECE_SQUARE_TABLES_WHITE[square]
                    elif (piece.piece_type == chess.KING):
                        middle_game_white_score += MID_GAME_KING_PIECE_SQUARE_TABLES_WHITE[square]
                        end_game_white_score += END_GAME_KING_PIECE_SQUARE_TABLES_WHITE[square]
                else:
                    middle_game_black_score += MID_GAME_CHESS_PIECE_VALUES[piece.piece_type]
                    end_game_black_score += END_GAME_CHESS_PIECE_VALUES[piece.piece_type]
                    if (piece.piece_type == chess.PAWN):
                        middle_game_black_score += MID_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_PAWN_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.KNIGHT):
                        middle_game_black_score += MID_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_KNIGHT_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.BISHOP):
                        middle_game_black_score += MID_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_BISHOP_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.ROOK):
                        middle_game_black_score += MID_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_ROOK_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.QUEEN):
                        middle_game_black_score += MID_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_QUEEN_PIECE_SQUARE_TABLES_BLACK[square]
                    elif (piece.piece_type == chess.KING):
                        middle_game_black_score += MID_GAME_KING_PIECE_SQUARE_TABLES_BLACK[square]
                        end_game_black_score += END_GAME_KING_PIECE_SQUARE_TABLES_BLACK[square]
        middle_game_phase = game_phase
        if middle_game_phase > 24:
            middle_game_phase = 24
        end_game_phase = 24-middle_game_phase
        mid_score = middle_game_white_score-middle_game_black_score
        end_score = end_game_white_score-end_game_black_score
        return mid_score*middle_game_phase + end_score * end_game_phase
