from threading import Thread
from time import sleep
from omok.ai.minmax import MinMax
# from omok.ai.network import Network
# from omok.ai.rl import RL
from omok.core.board import Board

class AI:
    """Omok AI Runner"""
    def __init__(self, board):
        self.board = board
        self.threads = []
        self.exit_flag = False
        self.board.print('Omok AI initiated')

    def load(self, status_condition, ai_type):
        if len(self.threads) >= 2:
            self.board.print('No more AI threads can be created')
        elif status_condition != Board.BLACK_TURN and status_condition != Board.WHITE_TURN:
            self.board.print('Invalid status condition for AI')
        elif len(self.threads) == 1 and status_condition == self.threads[0][1]:
            self.board.print('Cannot create duplicate AI threads with the same status condition')
        elif ai_type != 'minmax' and ai_type != 'network' and ai_type != 'rl':
            self.board.print('Invalid AI type; must be either "minmax" or "network" or "rl"')
        else:
            self.threads.append((Thread(target=lambda : self.play(status_condition, ai_type)), status_condition))
            self.board.print('Omok AI loaded with condition ' + str(status_condition))
    
    def start(self):
        self.exit_flag = False
        for thread in self.threads:
            thread[0].start()
        self.board.print('Omok AI started')

    def stop(self):
        self.exit_flag = True
        for thread in self.threads:
            thread[0].join()
        self.board.print('Omok AI stopped')

    def play(self, status_condition, ai_type):
        if ai_type == 'minmax':
            algorithm = MinMax()
        # elif ai_type == 'network':
        #     algorithm = Network('omok/ai/models_network/standard.npy')
        # else:
        #     algorithm = RL(self.board.height, self.board.width, status_condition)
        sleep(2.0) # To prevent it from starting before GUI loads up
        while not self.exit_flag:
            if self.board.status == status_condition:
                self.board.lock.acquire()
                (i, j) = algorithm.decide_next_move(self.board)
                self.board.lock.release()
                self.board.print('AI({}) - '.format(ai_type), end='')
                self.board.place(i, j)
            else:
                sleep(0.1)