from omok.ai.ai import AI
from omok.core.board import Board
from omok.gui.gui import GUI

def run():
    boardwidth = 15
    boardheight = 15
    board = Board(width=boardwidth, height=boardheight)
    ai = AI(board)
    ai.load(board.WHITE_TURN, 'randomwalk')
    ai.load(board.BLACK_TURN, 'minmax')
    ai.start()
    GUI(board)
    ai.stop()
    quit(0)