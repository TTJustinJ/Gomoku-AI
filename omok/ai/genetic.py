import random
from copy import deepcopy
from omok.core.board import Board
from omok.core.rules import Rules


class GeneticAI:
    POPULATION_SIZE = 150  # Increased population size
    MAX_GENERATIONS = 150  # Increased number of generations for evolution
    MUTATION_RATE = 0.2  # Start with a higher mutation rate
    SEARCH_AREA = 1
    MAX_RESTARTS = 3  # Maximum number of restarts during optimization

    def __init__(self):
        self.criteria = None
        self.generation = 0  # Track the current generation
        self.initiate_criteria()

    def initiate_criteria(self):
        """
        Sets up criteria for 5-slot row patterns

        This criteria only judges the likeliness of filling up all 5 slots with the same color
        """
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
            B_count = pattern.count(charset[1])
            W_count = pattern.count(charset[2])
            if B_count > 0 and W_count > 0:
                value = 0.0
            elif B_count == 0 and W_count == 0:
                value = 0.0
            else:
                value = 13 ** (B_count + W_count - 3)
                if B_count > 0:
                    value *= -1.0
            self.criteria[pattern] = value

    @staticmethod
    def pad(board):
        board = deepcopy(board)
        pad = Board.EMPTY_SLOT

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
        is_black_turn = (board_instance.status == Board.BLACK_TURN)

        padded_board = GeneticAI.pad(board)
        padded_empty_slots = {(slot[0] + 1, slot[1] + 1) for slot in empty_slots}

        # Scan the board for immediate threats or winning opportunities before generating populations
        best_move = self.scan_board_for_threats_or_wins(padded_board, padded_empty_slots, is_black_turn)
        if best_move:
            return tuple(map(lambda x: x - 1, best_move))

        best_score = float('-inf')

        # Re-evaluate the board state after each opponent move
        for generation in range(GeneticAI.MAX_GENERATIONS):
            self.generation = generation

            # Scan the board for threats or winning moves in every generation to adapt to opponent's moves
            best_move = self.scan_board_for_threats_or_wins(padded_board, padded_empty_slots, is_black_turn)
            if best_move:
                return tuple(map(lambda x: x - 1, best_move))

            population = random.sample(padded_empty_slots, min(len(padded_empty_slots), GeneticAI.POPULATION_SIZE))
            fitness_scores = [self.evaluate_move(padded_board, move, is_black_turn) for move in population]
            if sum(fitness_scores) == 0:
                continue
            selected_population = self.select_population(population, fitness_scores)
            offspring = self.crossover(selected_population)
            population = self.mutation(offspring, padded_empty_slots)

            # Dynamically re-evaluate the best move after each generation
            current_best_move = max(population, key=lambda move: self.evaluate_move(padded_board, move, is_black_turn))
            current_best_score = self.evaluate_move(padded_board, current_best_move, is_black_turn)

            if current_best_score > best_score:
                best_move = current_best_move
                best_score = current_best_score

        if best_move is None or best_move not in padded_empty_slots:
            # Regenerate the best move after each opponent move or if best move is invalid
            return self.fallback_generation_optimization(padded_board, padded_empty_slots, is_black_turn)

        return tuple(map(lambda x: x - 1, best_move))

    def scan_board_for_threats_or_wins(self, board, empty_slots, is_black_turn):
        """Scan the board for immediate winning moves or threats to block."""
        player_slot = Board.BLACK_SLOT if is_black_turn else Board.WHITE_SLOT
        opponent_slot = Board.WHITE_SLOT if is_black_turn else Board.BLACK_SLOT

        # First, check for winning move
        for move in empty_slots:
            x, y = move
            board[x][y] = player_slot
            if Rules.is_game_over(board):
                board[x][y] = Board.EMPTY_SLOT
                return move
            board[x][y] = Board.EMPTY_SLOT

        # Next, check for opponent's winning move to block
        for move in empty_slots:
            x, y = move
            board[x][y] = opponent_slot
            if Rules.is_game_over(board):
                board[x][y] = Board.EMPTY_SLOT
                return move
            board[x][y] = Board.EMPTY_SLOT

        return None

    def fallback_generation_optimization(self, board, empty_slots, is_black_turn):
        """Fallback method using additional generations to find a better move when all fitness scores are zero."""
        population = random.sample(empty_slots, min(len(empty_slots), GeneticAI.POPULATION_SIZE))

        best_move = None
        best_score = float('-inf')

        for _ in range(GeneticAI.MAX_GENERATIONS * 2):  # Double the number of generations for fallback
            fitness_scores = [self.evaluate_move(board, move, is_black_turn) for move in population]
            selected_population = self.select_population(population, fitness_scores)
            offspring = self.crossover(selected_population)
            population = self.mutation(offspring, empty_slots)

            # Dynamically re-evaluate the best move after each generation
            current_best_move = max(population, key=lambda move: self.evaluate_move(board, move, is_black_turn))
            current_best_score = self.evaluate_move(board, current_best_move, is_black_turn)

            if current_best_score > best_score:
                best_move = current_best_move
                best_score = current_best_score

        return tuple(map(lambda x: x - 1, best_move))

    def evaluate_move(self, board, move, is_black_turn):
        """Evaluate the fitness of a move by placing the piece and assessing the board."""
        temp_board = deepcopy(board)
        temp_board[move[0]][move[1]] = Board.BLACK_SLOT if is_black_turn else Board.WHITE_SLOT

        # Fitness function based on proposed weights (modified values)
        number_of_fours = self.count_structures(temp_board, move, 4)
        number_of_threes = self.count_structures(temp_board, move, 3)
        number_of_twos = self.count_structures(temp_board, move, 2)
        opponent_threats_fours = self.count_opponent_structures(temp_board, move, 4)  # Count opponent four threats
        opponent_threats_threes = self.count_opponent_structures(temp_board, move, 3)  # Count opponent three threats
        blocked_opponent_twos = self.count_blocked_opponent_structures(temp_board, move, 2)  # Count blocked opponent two threats
        blocked_opponent_threes = self.count_blocked_opponent_structures(temp_board, move, 3)

        blocked_opponent_fours = self.count_blocked_opponent_structures(temp_board, move, 3)

        # Modified fitness function to heavily prioritize defensive moves
        fitness_score = (
            (3500 * number_of_fours) +
            (150 * number_of_threes) +
            (20 * number_of_twos) -
            (15000 * opponent_threats_fours) -  # Heavily penalize opponent four-in-a-row threats
            (5000 * opponent_threats_threes) +   # Penalize opponent three-in-a-row threats
            (100 * blocked_opponent_twos) +     # Reward blocking opponent two-in-a-row threats
            (5000 * blocked_opponent_threes) +
            (15000 * blocked_opponent_fours)
        )
        return fitness_score

    def count_structures(self, board, move, length):
        """Count the number of structures (lines of given length) involving the move."""
        directions = [
            (1, 0), (0, 1), (1, 1), (1, -1),  # Vertical, Horizontal, Diagonal (both directions)
        ]
        count = 0

        for direction in directions:
            dx, dy = direction
            for d in (-1, 1):
                x, y = move
                line_length = 1

                while True:
                    x += dx * d
                    y += dy * d
                    if 0 <= x < len(board) and 0 <= y < len(board[0]) and board[x][y] == board[move[0]][move[1]]:
                        line_length += 1
                    else:
                        break

                if line_length == length:
                    count += 1

        return count

    def count_opponent_structures(self, board, move, length):
        """Count potential structures for the opponent involving the move."""
        directions = [
            (1, 0), (0, 1), (1, 1), (1, -1),  # Vertical, Horizontal, Diagonal (both directions)
        ]
        count = 0
        opponent_stone = Board.WHITE_SLOT if board[move[0]][move[1]] == Board.BLACK_SLOT else Board.BLACK_SLOT

        for direction in directions:
            dx, dy = direction
            for d in (-1, 1):
                x, y = move
                line_length = 0
                empty_seen = False

                while True:
                    x += dx * d
                    y += dy * d
                    if 0 <= x < len(board) and 0 <= y < len(board[0]):
                        if board[x][y] == opponent_stone:
                            line_length += 1
                        elif board[x][y] == Board.EMPTY_SLOT and not empty_seen:
                            empty_seen = True  # Allow for one empty slot in the sequence
                        else:
                            break
                    else:
                        break

                if line_length >= length:
                    count += 1

        return count

    def count_blocked_opponent_structures(self, board, move, length):
        """Count the number of blocked opponent structures of a given length involving the move."""
        directions = [
            (1, 0), (0, 1), (1, 1), (1, -1),  # Vertical, Horizontal, Diagonal (both directions)
        ]
        count = 0
        opponent_stone = Board.WHITE_SLOT if board[move[0]][move[1]] == Board.BLACK_SLOT else Board.BLACK_SLOT

        for direction in directions:
            dx, dy = direction
            for d in (-1, 1):
                x, y = move
                line_length = 0
                empty_seen = False

                while True:
                    x += dx * d
                    y += dy * d
                    if 0 <= x < len(board) and 0 <= y < len(board[0]):
                        if board[x][y] == opponent_stone:
                            line_length += 1
                        elif board[x][y] == Board.EMPTY_SLOT:
                            empty_seen = True  # Count the empty spot as a potential block
                            break
                        else:
                            break
                    else:
                        break

                if line_length == length:
                    count += 1

        return count

    def select_population(self, population, fitness_scores):
        """Select individuals using tournament selection."""
        tournament_size = min(5, len(population))  # Ensure tournament size does not exceed population size
        selected = []
        for _ in range(len(population)):
            tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
            best_individual = max(tournament, key=lambda x: x[1])
            selected.append(best_individual[0])
        return selected

    def crossover(self, population):
        """Perform crossover using two-point crossover to generate offspring."""
        offspring = []
        for i in range(0, len(population), 2):
            parent1 = population[i]
            parent2 = population[(i + 1) % len(population)]
            point = random.randint(1, len(parent1) - 1)
            child = (parent1[0], parent2[1]) if point == 1 else (parent2[0], parent1[1])
            offspring.append(child)
        return offspring

    def mutation(self, population, possible_moves):
        """Mutate individuals with a dynamic mutation rate."""
        generation_factor = self.generation / GeneticAI.MAX_GENERATIONS  # Assuming self.generation is tracked
        dynamic_mutation_rate = GeneticAI.MUTATION_RATE * (1 - generation_factor)
        mutated_population = []
        for individual in population:
            if random.random() < dynamic_mutation_rate:
                mutated_population.append(random.choice(list(possible_moves)))
            else:
                mutated_population.append(individual)
        return mutated_population

    def get_candidate_moves(self, board, empty_slots):
        moves = set()
        for i in range(1, len(board) - 1):
            for j in range(1, len(board[0]) - 1):
                if not board[i][j] == Board.EMPTY_SLOT:
                    for k in range(-GeneticAI.SEARCH_AREA, GeneticAI.SEARCH_AREA + 1):
                        for l in range(-GeneticAI.SEARCH_AREA, GeneticAI.SEARCH_AREA + 1):
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
