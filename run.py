from omok import omok
import argparse

parser = argparse.ArgumentParser(description="get AI")
parser.add_argument("--black", help="optional", default="MCTS_AI")
# parser.add_argument("--white", help="optional", default="randomwalk")
parser.add_argument("--white", help="optional", default="minmax")
args = parser.parse_args()
AI_black = args.black
AI_white = args.white
print(AI_black)
print(AI_white)
omok.run(AI_black, AI_white)
