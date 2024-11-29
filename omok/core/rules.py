class Rules:



    DIRECTIONS = {
        'W-E': (0, 1),
        'NW-SE': (1, 1),
        'N-S': (1, 0),
        'NE-SW': (1, -1)
    }

    @staticmethod
    def is_defeat(board, i, j):

        for direction in Rules.DIRECTIONS.values():
            if Rules.count(board, i, j, direction) == 5:
                return True
        return False

    @staticmethod
    def is_three(board, i, j):
        # height = len(board)
        # width = len(board[0])
        # three_count = 0
        #
        # for direction in Rules.DIRECTIONS.values():
        #     if Rules.count_three(board, i, j, direction):
        #         three_count += 1
        #     if three_count > 1:
        #         return True

        return False

    @staticmethod
    def count(board, i, j, direction):

        total = 1
        height = len(board)
        width = len(board[0])

        for weight in [-1, 1]:
            for index in range(1, 6):
                _i = i + weight * index * direction[0]
                _j = j + weight * index * direction[1]
                if _i < 0 or _j < 0 or _i >= height or _j >= width:
                    break
                if board[i][j] == board[_i][_j]:
                    total += 1
                else:
                    break

        return total


    @staticmethod
    def is_game_over(board):

        height = len(board)
        width = len(board[0])

        for i in range(height):
            for j in range(width):
                if board[i][j] != '-' and Rules.is_defeat(board, i, j):
                    return True

        for row in board:
            if '-' in row:
                return False

        return True

    @staticmethod
    def get_winner(board):
        height = len(board)
        width = len(board[0])

        for i in range(height):
            for j in range(width):
                if board[i][j] != '-' and Rules.is_defeat(board, i, j):
                    return board[i][j]

        return None