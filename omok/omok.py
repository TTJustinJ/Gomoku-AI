from omok.ai.ai import AI
from omok.core.board import Board
from omok.gui.gui import GUI
import omok.time_arrays
import argparse


def run(AI_black, AI_white):
    boardwidth = 15
    boardheight = 15
    board = Board(width=boardwidth, height=boardheight)
    ai = AI(board)
    ai.load(board.WHITE_TURN, AI_white)
    ai.load(board.BLACK_TURN, AI_black)
    ai.start()
    GUI(board)
    ai.stop()
    if AI_white == "minmax":
        print("minmax avg decision time:" + str(omok.time_arrays.calculate_minmax_avg()))
    elif AI_white == "randomwalk":
        print("randomwalk avg decision time:" + str(omok.time_arrays.calculate_randomwalk_avg()))
    elif AI_white == "MCTS_AI":
        print("MCTS_AI avg decision time:" +  str(omok.time_arrays.calculate_MCTS_AI_avg()))
    if AI_black == "minmax":
        print("minmax avg decision time:" + str(omok.time_arrays.calculate_minmax_avg()))
    elif AI_black == "randomwalk":
        print("randomwalk avg decision time:" + str(omok.time_arrays.calculate_randomwalk_avg()))
    elif AI_black == "MCTS_AI":
        print("MCTS_AI avg decision time:" + str(omok.time_arrays.calculate_MCTS_AI_avg()))
    quit(0)
