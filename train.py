# import omok.ai.network_trainer as trainer
# trainer.train(None, 100, 0.1, 0.75, 'network', False)

from omok.ai.rl import RL
from omok.core.board import Board

NUM_EPOCHS = 200000
BATCH_SIZE = 1
LEARNING_RATE = 1
REGULARIZATION = 0.03

BOARD_HEIGHT = 10
BOARD_WIDTH = 10

rl = RL(BOARD_HEIGHT, BOARD_WIDTH, Board.WHITE_TURN)
rl.train(NUM_EPOCHS, BATCH_SIZE, LEARNING_RATE, REGULARIZATION, visualize=True, transfer_minimax=True)