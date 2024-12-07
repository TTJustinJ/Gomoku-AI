from copy import deepcopy
from omok.core.board import Board
from omok.core.rules import Rules
import omok.time_arrays
import time


class MinMax:
    MAX_DEPTH = 2
    SEARCH_RADIUS = 1

    def __init__(self):
        self.criteria = None
        self._setup_criteria()

    @staticmethod
    def _pad_board(original_board):
        """
        Return a padded version of the board, adding a layer of blank padding around all edges.
        """
        padded = deepcopy(original_board)
        pad_char = '\0'

        width = len(padded[0])
        padded.insert(0, [pad_char] * width)
        padded.append([pad_char] * width)

        for i in range(len(padded)):
            padded[i].insert(0, pad_char)
            padded[i].append(pad_char)

        return padded

    def _setup_criteria(self):
        """
        Prepare a dictionary (self.criteria) mapping all 5-slot patterns to an evaluation value.

        Patterns that can lead to a five-in-a-row are given higher absolute values.
        Patterns mixing Black and White are given zero, as they won't form a pure line of five.
        """
        if self.criteria is not None:
            return

        self.criteria = {}
        slots = [Board.EMPTY_SLOT, Board.BLACK_SLOT, Board.WHITE_SLOT]

        # Generate all possible patterns of length 5
        for a in slots:
            for b in slots:
                for c in slots:
                    for d in slots:
                        for e in slots:
                            self.criteria[a + b + c + d + e] = 0.0

        # Assign values to each pattern
        for pattern in self.criteria.keys():
            black_count = pattern.count(Board.BLACK_SLOT)
            white_count = pattern.count(Board.WHITE_SLOT)

            if black_count > 0 and white_count > 0:
                # Mixed colors, no potential for a uniform five-in-a-row
                val = 0.0
            elif black_count == 0 and white_count == 0:
                # All empty
                val = 0.0
            else:
                # Either all black or all white (with empty)
                if black_count > 0:
                    # Negative value for black advantage
                    val = -1.0
                    segment_length = black_count
                else:
                    # Positive value for white advantage
                    val = 1.0
                    segment_length = white_count

                # Exponential factor based on how many stones already in the pattern
                val *= (13 ** (segment_length - 3))

            self.criteria[pattern] = val

    def decide_next_move(self, board_instance):
        """
        Use a limited-depth MinMax search (with alpha-beta pruning logic) to choose the next move.
        """
        board = board_instance.board
        empty_slots = board_instance.empty_slots
        turn_condition = board_instance.status

        padded = self._pad_board(board)
        padded_empty = {(x + 1, y + 1) for (x, y) in empty_slots}

        start = time.time()
        # For the alphabeta: we maintain the original logic, just re-structure code slightly.
        best_choice = self._alphabeta(
            padded,
            padded_empty,
            depth=0,
            search_area=self.SEARCH_RADIUS,
            # Keeping the original logic where 'min' parameter was a large positive number and 'max' was large negative
            alpha=1000000.0,  # previously called 'min'
            beta=-1000000.0,  # previously called 'max'
            for_black=(turn_condition == Board.BLACK_TURN)
        )
        end = time.time()

        elapsed = end - start
        print("minmax decision time:" + str(elapsed))
        omok.time_arrays.add_to_minmax_array(elapsed)
        omok.time_arrays.print_minmax_array()

        # Convert coordinates back to original indexing
        return map(lambda coord: coord - 1, best_choice)

    def _alphabeta(self, board, empty_slots, depth, search_area, alpha, beta, for_black):
        """
        Perform a recursive MinMax-style search:
        - If for_black is True, we are minimizing scores (aiming towards negative).
        - If for_black is False, we are maximizing scores (aiming towards positive).

        At the top level (depth 0), return the best move.
        At deeper levels, return the best achievable score at that state.
        """
        # Termination condition
        if depth == self.MAX_DEPTH:
            return self._evaluate(board)

        candidate_moves = self._get_candidate_moves(board, empty_slots, search_area)
        chosen_move = None

        for move in candidate_moves:
            next_board = deepcopy(board)
            next_board[move[0]][move[1]] = Board.BLACK_SLOT if for_black else Board.WHITE_SLOT

            # Update empty slots for next state
            next_empty = deepcopy(empty_slots)
            next_empty.remove(move)

            # If no further moves, assign a baseline value
            if len(next_empty) == 0:
                value = 0.0
            else:
                value = self._alphabeta(
                    next_board,
                    next_empty,
                    depth + 1,
                    search_area,
                    alpha,
                    beta,
                    not for_black
                )

            if value is None:
                continue

            # If it's Black's turn, we are "minimizing"
            if for_black:
                if value < alpha:
                    alpha = value
                    chosen_move = move
                if alpha <= beta:
                    # Pruning condition
                    break
            else:
                # White's turn, we are "maximizing"
                if value > beta:
                    beta = value
                    chosen_move = move
                if beta >= alpha:
                    # Pruning condition
                    break

        # If we are at the root, we return the chosen move rather than just the value
        return chosen_move if depth == 0 else (alpha if for_black else beta)

    def _get_candidate_moves(self, board, empty_slots, search_area):
        """
        Identify potential moves by looking around existing stones within a certain radius.
        If no candidate found, fallback to placing in the middle.
        """
        possible_moves = set()
        rows = len(board)
        cols = len(board[0])

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if board[i][j] != Board.EMPTY_SLOT:
                    for dx in range(-search_area, search_area + 1):
                        for dy in range(-search_area, search_area + 1):
                            candidate = (i + dx, j + dy)
                            if candidate in empty_slots:
                                possible_moves.add(candidate)

        # If no moves found, choose the center as fallback
        if not possible_moves:
            center = (rows // 2, cols // 2)
            possible_moves.add(center)

        return possible_moves

    def _evaluate(self, board):
        """
        Evaluate the entire board by summing contributions from each relevant point.
        """
        total = 0.0
        max_row = len(board) - 3
        max_col = len(board[0]) - 3

        for x in range(3, max_row):
            for y in range(3, max_col):
                total += self._evaluate_point(board, x, y)

        return total

    def _evaluate_point(self, board, i, j):
        """
        Evaluate a single point by examining lines in all directions and applying the criteria.
        """
        result = 0.0
        for direction in Rules.DIRECTIONS.values():
            segment = ''
            # Build a 7-length segment around the point (i,j)
            for step in range(-3, 4):
                row = i + step * direction[0]
                col = j + step * direction[1]
                segment += board[row][col]

            # Focus on the middle 5 characters
            middle_five = segment[1:6]
            val = self.criteria.get(middle_five, 0.0)

            # Check endpoints
            endpoints = segment[::6]
            if val < 0 and Board.BLACK_SLOT in endpoints:
                val = 0
            elif val > 0 and Board.WHITE_SLOT in endpoints:
                val = 0

            result += val
        return result
