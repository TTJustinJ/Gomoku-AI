import random
from copy import deepcopy
from omok.core.board import Board
from omok.core.rules import Rules
import time
import omok.time_arrays


class RandomWalkAI:
    MAX_SIMULATIONS = 20  # random walk limitation
    MAX_RESTARTS = 3  # random restart limitation
    SEARCH_AREA = 1

    @staticmethod
    def pad(board):
        board = deepcopy(board)
        pad = '\0'

        horizontal_padding = [pad] * len(board[0])
        board.insert(0, list(horizontal_padding))
        board.append(list(horizontal_padding))

        for i in range(len(board)):
            board[i].insert(0, pad)
            board[i].append(pad)

        return board

    def decide_next_move(self, board_instance):

        board = board_instance.board
        empty_slots = board_instance.empty_slots
        condition = board_instance.status
        is_black_turn = (condition == Board.BLACK_TURN)

        padded_board = RandomWalkAI.pad(board)
        padded_empty_slots = set()

        for empty_slot in empty_slots:
            padded_empty_slots.add((empty_slot[0] + 1, empty_slot[1] + 1))

        best_move = None
        best_score = float('-inf')
        start_time = time.time()
        for _ in range(RandomWalkAI.MAX_RESTARTS):
            move, score = self.random_walk_with_restart(padded_board, padded_empty_slots, is_black_turn)
            if score > best_score:
                best_move, best_score = move, score
        end_time = time.time()
        decision_time = end_time - start_time
        print("randomwalk_" + str(RandomWalkAI.MAX_SIMULATIONS) +"decision time:" + str(decision_time))
        omok.time_arrays.add_to_randomwalk_array(decision_time)
        omok.time_arrays.print_randomwalk_array()
        return map(lambda x: x - 1, best_move)

    def random_walk_with_restart(self, board, empty_slots, is_black_turn):

        candidates = self.get_candidate_moves(board, empty_slots)
        move_scores = {move: 0 for move in candidates}

        for move in candidates:
            for _ in range(RandomWalkAI.MAX_SIMULATIONS):
                result = self.simulate_game(board, move, is_black_turn)
                if result == 1:
                    move_scores[move] += 1
                elif result == -1:
                    move_scores[move] -= 1

        best_move = max(move_scores, key=move_scores.get)
        best_score = move_scores[best_move]
        return best_move, best_score

    def simulate_game(self, board, move, is_black_turn):

        temp_board = deepcopy(board)
        temp_board[move[0]][move[1]] = Board.BLACK_SLOT if is_black_turn else Board.WHITE_SLOT
        current_player = not is_black_turn
        empty_slots = deepcopy(self.get_candidate_moves(temp_board, self.get_empty_slots(temp_board)))

        while not Rules.is_game_over(temp_board):
            if not empty_slots:
                break
            next_move = random.choice(list(empty_slots))
            temp_board[next_move[0]][next_move[1]] = Board.BLACK_SLOT if current_player else Board.WHITE_SLOT
            empty_slots.remove(next_move)
            current_player = not current_player

        winner = Rules.get_winner(temp_board)
        if winner == Board.BLACK_SLOT:
            return 1 if is_black_turn else -1
        elif winner == Board.WHITE_SLOT:
            return -1 if is_black_turn else 1
        else:
            return 0

    def get_candidate_moves(self, board, empty_slots):

        moves = set()
        for i in range(1, len(board) - 1):
            for j in range(1, len(board[0]) - 1):
                if not board[i][j] == Board.EMPTY_SLOT:
                    for k in range(-RandomWalkAI.SEARCH_AREA, RandomWalkAI.SEARCH_AREA + 1):
                        for l in range(-RandomWalkAI.SEARCH_AREA, RandomWalkAI.SEARCH_AREA + 1):
                            move = (i + k, j + l)
                            if move in empty_slots:
                                moves.add(move)

        if len(moves) == 0:
            moves.add((int(len(board) / 2), int(len(board[0]) / 2)))

        return moves

    def get_empty_slots(self, board):

        empty_slots = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == Board.EMPTY_SLOT:
                    empty_slots.add((i, j))
        return empty_slots
