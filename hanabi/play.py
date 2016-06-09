from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt

from const import (COLORS, VALUES, COLOR_NAMES)
from const import COL_TO_IND
from const import IND_TO_COL
from card import card
from deck import deck 
from player import player
from game import game 

# total number of unique cards 
NUM_COLORS = len(COLORS)
NUM_VALUES = len(list(set(VALUES)))
NUM_HAND = 5
MULT_DIC = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
NUM_OTHERS = 1
NUM_PLAYERS = NUM_OTHERS + 1
nu = 0.01 # discount factor 

#===============================================================================
# Iterative Q-Learning Helper Functions
#===============================================================================

# action vector given by (discard, play, hint[colors, values])
# random action by placing 1 in random index of action vector 
def get_action(player): 
	total = NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES)
	action = np.zeros(total)
	i = np.random.randint(total)
	action[i] = 1
	return action

# play the game according to iterative q-learning 
def start(self): 
	while self.lost == False: 
		for i in range(len(hands)): 
			action = get_action(players[i]) # get action using a player's info

			self.check_action(self, action, i)


#===============================================================================
# Playing the Game
#===============================================================================

if __name__ == '__main__':
	g = game()
	g.print_hands()
	# print(g.players[0].beliefs[:, :, 0])
	# print(g.players[1].beliefs[:, :, 0])

	# test that playing works
	# g.play(0, 0) 
	# print("\n")

	# print("beliefs: ")
	# for i in range(NUM_HAND): 
	# 	print(g.players[0].beliefs[:, :, i])
	# print("others: ")
	# for i in range(NUM_HAND): 
	# 	print(g.players[0].others[:, :, i, 0])
	# print("\n")

	# print("beliefs: ")
	# for i in range(NUM_HAND): 
	# 	print(g.players[1].beliefs[:, :, i])
	# print("others: ")
	# for i in range(NUM_HAND): 
	# 	print(g.players[1].others[:, :, i, 0])
	# print("hints: ", g.players[0].hints, g.players[1].hints)
	# print("bombs: ", g.players[0].bombs, g.players[1].bombs)

	
	# test that hinting works 
	# g.hint(0, 1, 'value', 0) 
	# print("\n")
	# for i in range(NUM_HAND): 
	# 	print(g.players[1].beliefs[:, :, i])
	# print("hints: ", g.players[0].hints, g.players[1].hints)

	# test that discarding works
	# g.players[0].beliefs[:, :, 1] = np.zeros([NUM_COLORS, NUM_VALUES])
	# g.discard(0, 0) 
	# print("\n")

	# for i in range(NUM_HAND): 
	# 	print(g.players[0].beliefs[:, :, i])
	# print("\n")

	# for i in range(NUM_HAND): 
	# 	print(g.players[1].beliefs[:, :, i])
	# print("hints: ", g.players[0].hints, g.players[1].hints)

	
	# test that hinting works 
	# g.hint(0, 1, 'value', 0) 
	# print("\n")
	# for i in range(NUM_HAND): 
	# 	print(g.players[1].beliefs[:, :, i])
	# print("hints: ", g.players[0].hints, g.players[1].hints)



