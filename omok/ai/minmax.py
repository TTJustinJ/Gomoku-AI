from copy import deepcopy
from omok.core.board import Board
from omok.core.rules import Rules

class MinMax:
    MAX_DEPTH = 2
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

    def __init__(self):
        self.criteria = None
        self.initiate_criteria()
    
    def initiate_criteria(self):
        """
        Sets up criteria for 5-slot row patterns

        This criteria only judges the likeliness of filling up all 5 slots with the same color

        ex. BBEBB = Very likely to be filled, so high score
            BWEEB = Will never be filled since B and W are mixed, so 0 score
        
        Hence, it must be checked what color surrounds the 5-slot pattern before using it.

        Criteria is stored as class variable, in dictionary structure of criteria[pattern] = value
        """
        if self.criteria != None:
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
            B_count = pattern.count(charset[1])
            W_count = pattern.count(charset[2])
            if B_count > 0 and W_count > 0:
                value = 0.0
            elif B_count == 0 and W_count == 0:
                value = 0.0
            else:
                if B_count > 0:
                    value = -1.0
                else:
                    value = 1.0
                count = B_count + W_count # one of these is 0
                value *= 13**(count - 3)
            self.criteria[pattern] = value

    def decide_next_move(self, board_instance):
        board = board_instance.board
        empty_slots = board_instance.empty_slots
        condition = board_instance.status
        
        padded_board = MinMax.pad(board)
        padded_empty_slots = set()

        for empty_slot in empty_slots:
            padded_empty_slots.add((empty_slot[0] + 1, empty_slot[1] + 1))

        next_move = self.alphabeta(padded_board, padded_empty_slots, 
                                    0, MinMax.SEARCH_AREA, 1000000.0, -1000000.0, 
                                    condition == Board.BLACK_TURN)
        return map(lambda x: x - 1, next_move)

    # Black will try to minimize towards -1, and white maximize towards 1
    def alphabeta(self, board, empty_slots, depth, search_area, min, max, for_black):
        if depth == MinMax.MAX_DEPTH:
            return self.evaluate_board(board)
        for move in self.next_moves(board, empty_slots, search_area):
            next_board = deepcopy(board)
            next_board[move[0]][move[1]] = Board.BLACK_SLOT if (for_black) else Board.WHITE_SLOT
            next_empty_slots = deepcopy(empty_slots)
            next_empty_slots.remove(move)

            value = 0.0 if (len(next_empty_slots) == 0) else\
                        self.alphabeta(next_board, next_empty_slots, 
                                        depth + 1, search_area, 
                                        min, max, not for_black)
            if value == None:
                continue
            if for_black:
                if min > value:
                    best_move = move
                    min = value
                if min <= max:
                    break
            else:
                if max < value:
                    best_move = move
                    max = value
                if max >= min:
                    break

        if depth == 0:
            return best_move
        else:
            return min if (for_black) else max

    def next_moves(self, board, empty_slots, search_area):
        """Generates possible next moves in given area"""
        moves = set()
        for i in range(1, len(board) - 1):
            for j in range(1, len(board[0]) - 1):
                if not board[i][j] == Board.EMPTY_SLOT:
                    for k in range(-search_area, search_area + 1):
                        for l in range(-search_area, search_area + 1):
                            move = (i + k, j + l)
                            if move in empty_slots:
                                moves.add(move)

        if len(moves) == 0:
            moves.add((int(len(board) / 2), int(len(board[0]) / 2)))
        
        return moves

    def evaluate_board(self, board):
        value = 0.0
        for i in range(3, len(board) - 3):
            for j in range(3, len(board[0]) - 3):
                value += self.evaluate_point(board, i, j)
        return value
        
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