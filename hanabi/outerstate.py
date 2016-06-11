from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
from collections import Counter
import numpy as np 
import matplotlib.pyplot as plt
import sys 
import cPickle as cp

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
ACTION_NUM = NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES)
FRESH_BELIEF = np.zeros([NUM_COLORS, NUM_VALUES])
for i in range(NUM_VALUES): 
	FRESH_BELIEF[:, i] = MULT_DIC[i+1] #/ (len(COLORS) * len(VALUES))


nu = 0.1 # learning rate  
gamma = 0.5 # discount factor 
epsilon = 0.5 # softmax greed factor 

#===============================================================================
# Outer-State Strategy Helper Functions
#===============================================================================

# rightmost hinted? # hinted value, but don't know color, play anyway?
# can be placed on stack 
def check_playable(hand, played):
	playable = []  # which indices are playable

	for i in range(len(hand)):
		card = hand[i]
		
		if card.know_val == True and card.know_col == True: 
			# the card at the played index is one less than the value
			if played[card.color] == (card.value-1): 
				playable.append(i)
		
		# if we know the value, it's not enough to play the card
		# unless all the played cards have the same value and that
		# value is one less than the card's value
		elif card.know_val == True and card.know_col == False: 
			if played[1:] == played[:-1]: 
				if played[0] == (card.value - 1): 
					playable.append(i)

	return playable

def hint_playable(hand, played): 
	# first get list of playable cards
	playable = check_playable(hand, played)
	hintable = []

	# iterate through playable cards. if they already have full 
	# information, don't hint them. if they don't have full information
	# hint either color or value. 
	for i in playable: 
		card = hand[i]
		if card.know_val == True and card.know_col == False: 
			hintable.append(("color", card.color))
		elif card.know_val == False and card.know_col == True: 
			hintable.append(("value", (card.value-1)))
		elif card.know_val == False and card.know_col == False: 
			hintable.append("value", (card.value-1))
			hintable.append("color", card.color)

	# elements and counts as tuples in decreasing order
	hint_mult = Counter(z).most_common()

	


	# choose hint which gives most information 
	return hintable 





# rightmost discarded? opponent has? multiplicity?
# if it's less than or equal to a played card, it's discardable 
def check_discardable(card, played): 
	discardable = [] # boolean array of discardable indices

	for i in range(len(hand)):
		card = hand[i]

		if card.know_col == True and card.know_val == True: 
			if played[card.color] >= card.value: 
				discardable.append(i)

	return discardable

# multiple playable cards?

#===============================================================================
# Playing the Outer-State Strategy
#===============================================================================
if __name__ == '__main__':
	
	g = game()
	game_score = []
	hints = []
	count = 0 # round in game

	# a single game
	while True: 
		count += 1
		print("ITERATION: ", count)

		# each player makes moves
		for i in NUM_PLAYERS: 

			# (1) IF THERE IS PLAYABLE CARD, PLAY IT 
			# list of playable cards 
			playable = check_playable(g.hands[i], g.played)
			
			# if multiple playable, play the rightmost one
			if playable != []: 
				g.play(i, playable[-1])

			# if there are no playable cards, move on to discards
			# (2) IF THERE IS A DISCARDABLE CARD, DISCARD IT
			else: 
				# list of discardable cards 
				discardable = check_discardable(g.hands[i], g.played)

				# if multiple discardable, discard oldest (leftmost)
				if discardable != []: 
					g.discard(i, discardable[0])

			# if there are no discardable cards, move on to hinting
			# if there are hint tokens remaining
			# (3) IF THE OPPONENT HAS A PLAYABLE CARD, HINT IT 
				elif discardable == [] and g.hints > 0: 
					playable = hint_playable(g.hands[NUM_OTHERS-i], g.played)


			





			game_score.append(g.score())
			
			if g.lost() == True: 
				break 
		if g.lost() == True: 
			break 




