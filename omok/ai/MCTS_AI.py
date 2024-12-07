import math
import random
from copy import deepcopy
from omok.core.board import Board
from omok.core.rules import Rules
import time
import omok.time_arrays

class MCTSNode:
    def __init__(self, board, parent=None, move=None, is_black_turn=True):
        self.board = board
        self.parent = parent
        self.children = []
        self.move = move
        self.visits = 0
        self.wins = 0
        self.is_black_turn = is_black_turn
        self.untried_moves = None  # Will store moves not yet expanded

    def ucb1(self, exploration_param=1.414):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration_param * math.sqrt(math.log(self.parent.visits) / self.visits)

class MCTS_AI:
    MAX_SIMULATIONS = 1000  # Increase if needed
    MAX_TIME = 5  # Limit thinking time in seconds for demonstration, adjust as needed
    SEARCH_AREA = 1

    def __init__(self):
        self.criteria = None
        self.initiate_criteria()

    def initiate_criteria(self):
        if self.criteria is not None:
            return

        self.criteria = dict()
        charset = [Board.EMPTY_SLOT, Board.BLACK_SLOT, Board.WHITE_SLOT]

        for a in charset:
            for b in charset:
                for c in charset:
                    for d in charset:
                        for e in charset:
                            pattern = a + b + c + d + e
                            self.criteria[pattern] = 0.0

        for pattern in self.criteria.keys():
            B_count = pattern.count(Board.BLACK_SLOT)
            W_count = pattern.count(Board.WHITE_SLOT)
            if B_count > 0 and W_count > 0:
                value = 0.0
            elif B_count == 0 and W_count == 0:
                value = 0.0
            else:
                if B_count > 0:
                    value = -1.0
                else:
                    value = 1.0
                count = B_count + W_count  # one of these is 0
                value *= 13 ** (count - 3)
            self.criteria[pattern] = value

    def pad(self, board):
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
        # Pad board and shift empty slots
        padded_board = self.pad(board_instance.board)
        padded_empty_slots = {(x+1, y+1) for (x, y) in board_instance.empty_slots}

        root = MCTSNode(board=padded_board, is_black_turn=(board_instance.status == Board.BLACK_TURN))
        root.untried_moves = self.get_candidate_moves(root.board, padded_empty_slots)

        start_time = time.time()
        simulations = 0

        # If it's the first move of the game, pick center
        if len(board_instance.empty_slots) == len(board_instance.board)*len(board_instance.board[0]):
            center = (len(padded_board) // 2, len(padded_board[0]) // 2)
            decision_time = time.time() - start_time
            print(f"mcts_decision time: {decision_time}")
            omok.time_arrays.add_to_MCTS_AI_array(decision_time)
            omok.time_arrays.print_MCTS_AI_array()
            return map(lambda x: x - 1, center)

        # Run MCTS within a time limit or simulation count
        while time.time() - start_time < MCTS_AI.MAX_TIME and simulations < MCTS_AI.MAX_SIMULATIONS:
            leaf = self.select(root)
            if not Rules.is_game_over(leaf.board):
                # If the node is not terminal, expand one child
                if leaf.untried_moves:
                    child = self.expand(leaf)
                    # Simulate from the newly created child
                    result = self.simulate_game(child.board, child.is_black_turn)
                    self.backpropagate(child, result)
                else:
                    # No moves to expand means terminal or fully expanded
                    # Just simulate from leaf node's current state
                    result = self.simulate_game(leaf.board, leaf.is_black_turn)
                    self.backpropagate(leaf, result)
            else:
                # Terminal node
                result = self.simulate_game(leaf.board, leaf.is_black_turn)
                self.backpropagate(leaf, result)

            simulations += 1

        # Pick the child with the most visits
        if not root.children:
            # No children means no moves
            # Just pick a random from root.untried_moves if available
            if root.untried_moves:
                best_move = random.choice(list(root.untried_moves))
            else:
                # fallback center
                best_move = (len(padded_board)//2, len(padded_board[0])//2)
        else:
            best_child = max(root.children, key=lambda c: c.visits)
            best_move = best_child.move

        decision_time = time.time() - start_time
        print(f"mcts_decision time: {decision_time}")
        omok.time_arrays.add_to_MCTS_AI_array(decision_time)
        omok.time_arrays.print_MCTS_AI_array()

        # Adjust move back to original indexing
        return map(lambda x: x - 1, best_move)

    def select(self, node):
        # Selection: descend until we find a node that is not fully expanded or is a terminal leaf
        while node.children and not node.untried_moves and not Rules.is_game_over(node.board):
            node = max(node.children, key=lambda c: c.ucb1())
        return node

    def expand(self, node):
        # Take one move from untried_moves and create a child
        move = node.untried_moves.pop()
        new_board = deepcopy(node.board)
        new_board[move[0]][move[1]] = Board.BLACK_SLOT if node.is_black_turn else Board.WHITE_SLOT

        child_node = MCTSNode(board=new_board, parent=node, move=move, is_black_turn=not node.is_black_turn)
        # Get moves for the child
        child_empty_slots = self.get_empty_slots(new_board)
        child_node.untried_moves = self.get_candidate_moves(new_board, child_empty_slots)

        node.children.append(child_node)
        return child_node

    def simulate_game(self, board, is_black_turn):
        # Run a random simulation until the game ends
        temp_board = deepcopy(board)
        current_player = is_black_turn
        empty_slots = self.get_empty_slots(temp_board)

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

    def backpropagate(self, node, simulation_result):
        while node:
            node.visits += 1
            node.wins += simulation_result
            node = node.parent

    def get_candidate_moves(self, board, empty_slots):
        moves = set()
        # Search moves around existing stones
        for i in range(1, len(board) - 1):
            for j in range(1, len(board[0]) - 1):
                if board[i][j] in (Board.BLACK_SLOT, Board.WHITE_SLOT):
                    for k in range(-MCTS_AI.SEARCH_AREA, MCTS_AI.SEARCH_AREA + 1):
                        for l in range(-MCTS_AI.SEARCH_AREA, MCTS_AI.SEARCH_AREA + 1):
                            ni, nj = i + k, j + l
                            if (ni, nj) in empty_slots:
                                moves.add((ni, nj))

        if len(moves) == 0 and len(empty_slots) > 0:
            # No moves found, pick center if empty or a random empty slot
            center = (len(board)//2, len(board[0])//2)
            moves.add(center if center in empty_slots else random.choice(list(empty_slots)))

        return moves

    def get_empty_slots(self, board):
        empty_slots = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == Board.EMPTY_SLOT:
                    empty_slots.add((i, j))
        return empty_slots

    def evaluate_board(self, board, is_black_turn):
        value = 0.0
        for i in range(3, len(board) - 3):
            for j in range(3, len(board[0]) - 3):
                value += self.evaluate_point(board, i, j)
        return value if is_black_turn else -value

    def evaluate_point(self, board, i, j):
        value = 0.0
        for direction in Rules.DIRECTIONS.values():
            str_line = ''
            for index in range(-3, 4):
                _i = i + index * direction[0]
                _j = j + index * direction[1]
                str_line += board[_i][_j]
            line_value = self.criteria.get(str_line[1:6], 0.0)
            end = str_line[::6]
            if line_value < 0 and Board.BLACK_SLOT in end:
                line_value = 0
            elif line_value > 0 and Board.WHITE_SLOT in end:
                line_value = 0
            value += line_value
        return value
