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

def opponent_playable(hand, played): 
	playable = []

	for i in range(len(hand)): 

		if played[hand[i].color] == (hand[i].value-1): 
			playable.append(i)

	return playable




# rightmost discarded? opponent has? multiplicity?
# if it's less than or equal to a played card, it's discardable 
def check_discardable(hand, played): 
	discardable = [] # boolean array of discardable indices

	for i in range(len(hand)):
		card = hand[i]

		if card.know_col == True and card.know_val == True: 
			if played[card.color] >= card.value: 
				discardable.append(i)

	return discardable

def random_hint(hand): 
	col_hinted = []
	val_hinted = []

	for card in hand: 
		if card.know_val == True: 
			val_hinted.append((card.value - 1))
		if card.know_col == True: 
			col_hinted.append(card.color)

	col_not_hinted = set(range(NUM_COLORS)) - set(col_hinted)
	val_not_hinted = set(range(NUM_VALUES)) - set(val_hinted)

	temp = random.randint(0, 1)
	if temp == 0: 
		return "color", random.choice(list(col_not_hinted))
	elif temp == 1: 
		return "value", random.choice(list(val_not_hinted))

def hint_playable(hand, played): 

	hintable = []
	playable = opponent_playable(hand, played)

	# iterate through playable cards. if they already have full 
	# information, don't hint them. if they don't have full information
	# hint either color or value. 
	if playable != []: 
		for i in playable: 
			card = hand[i]
			if card.know_val == True and card.know_col == False: 
				hintable.append(("color", card.color))
			elif card.know_val == False and card.know_col == True: 
				hintable.append(("value", (card.value-1)))
			elif card.know_val == False and card.know_col == False: 
				hintable.append(("value", (card.value-1)))
				hintable.append(("color", card.color))

		
		if len(hintable) > 0: 
			# elements and counts as tuples in decreasing order
			hint_mult = Counter(hintable).most_common()

			# choose hint which gives most information 
			# hints with same count are ordered arbitrarily
			# rethink hint scheme?
			return hint_mult[0][0]

		else: 
			return random_hint(hand)

	# don't re-hint
	# choose move which gives most information? 
	elif playable == []: 
		return random_hint(hand)

def clueless_discard(hand): 
	no_hint = []
	one_hint = []

	for i in range(len(hand)): 
		card = hand[i]

		if card.know_val == True and card.know_col == False: 
			one_hint.append(i)
		elif card.know_val == False and card.know_col == True: 
			one_hint.append(i)
		elif card.know_val == False and card.know_col == False: 
			# no_hint.append(i)
			one_hint.append(i)

	# if no_hint != []: 
	# 	return random.choice(no_hint)
	# elif no_hint != []: 
	# 	return one_hint[0]

	# oldest partial information card
	return one_hint[0]

	# discard random card 
	# return random.choice(one_hint)


# multiple playable cards?

#===============================================================================
# Playing the Outer-State Strategy
#===============================================================================
if __name__ == '__main__':
	
	temp_weights = np.empty([ACTION_NUM, NUM_COLORS * NUM_VALUES * NUM_HAND * NUM_PLAYERS + 7])
	temp_weights.fill(0.01)
	# temp_weights[(NUM_HAND*2):, :] = 0.2 # higher weights for hinting

	game_score = []
	hints = []

	for k in range(1000): 
		if (k % 100) = 0: 
			print("GAME: ", k)
		g = game()
		g.weights = temp_weights

		count = 0
		
		while True: 

			# each player makes moves
			for i in range(NUM_PLAYERS): 

				score_old = g.score()
				state_old = g.players[i].new_state

				# (1) IF THERE IS PLAYABLE CARD, PLAY IT 
				# list of playable cards 
				playable = check_playable(g.hands[i], g.played)
				# print("playable: ")

				action = -1
				
				# if multiple playable, play the rightmost one
				if playable != []: 
					# print("played index ", i)
					action = playable[-1] + NUM_HAND
					g.play(i, playable[-1])

				# if there are no playable cards, move on to discards
				# (2) IF THERE IS A DISCARDABLE CARD, DISCARD IT
				else: 
					# list of discardable cards 
					discardable = check_discardable(g.hands[i], g.played)
					# print(discardable)

					# if multiple discardable, discard oldest (leftmost)
					if discardable != []: 
						# print("discarded ", i)
						action = discardable[0]
						g.discard(i, discardable[0])

				# if there are no discardable cards, move on to hinting
				# if there are hint tokens remaining
				# (3) IF THE OPPONENT HAS A PLAYABLE CARD, HINT IT 
				# (4) IF THE OP DOESN'T HAVE A PLAY. CARD, RANDOM HINT
				# THAT HASNT BEEN GIVEN YET
					elif discardable == [] and g.hints > 0: 
						(which, value) = hint_playable(g.hands[NUM_OTHERS-i], g.played)
						if which == "color": 
							action = NUM_HAND * 2 + value
						elif which == "value": 
							action = NUM_HAND * 2 + NUM_COLORS + value

						g.hint(i, (NUM_OTHERS-i), which, value)
						
				
				# if there are no hints, discard
				# (5) discard oldest (leftmost) unhinted card
					elif discardable == [] and g.hints == 0: 
						index = clueless_discard(g.hands[i])
						# print("clueless discarded ", i)
						action = index
						g.discard(i, index)
						

				if action == -1: 
					print(action)

				score_new = g.score()
				norm_weight = g.weights[action] / np.sum(g.weights[action])
				delta = (score_new - score_old) + gamma*np.dot(norm_weight, g.players[i].new_state) - np.dot(norm_weight, state_old)
				weight_new = g.weights[action] + nu * delta * state_old
				g.weights[action] = weight_new

				
				if g.lost() == True: 
					break 
				
			if g.lost() == True: 
				game_score.append(g.score())
				temp_weights = g.weights
				break 

	# print("Scores: ", game_score)
	cp.dump(temp_weights, open('./outerstate_weights.p', 'wb'))
	print("weights", g.weights)

	print("Score Mean: ", sum(game_score) / len(game_score))
	print("Score Variance: ", np.var(game_score))

	plt.figure()
	plt.title("training scores")
	plt.plot(game_score)

	# plt.show()

	test_scores = []

	# test by playing 100 games with the weights
	for k in range(100): 
		
		g = game()
		g.weights = temp_weights

		print("TEST GAME: ", k)

		while True: 

			for i in range(NUM_PLAYERS): 
			
				probs = np.empty(ACTION_NUM)

				for j in range(ACTION_NUM): 
					probs[j] = np.dot(g.weights[j], state_old)

				if g.hints == 0: 
					probs[NUM_HAND*2:] = 0

				best = softmax_policy(probs)

				# do action 
				check_action(best, i)

				if g.lost() == True: 
					break 
			
			if g.lost() == True: 
				test_scores.append(g.score())
				break 

	
	print("weights", g.weights)
	print("Score Mean: ", sum(test_scores) / len(test_scores))
	print("Score Variance: ", np.var(test_scores))

	plt.figure()
	plt.title("testing scores")
	plt.plot(test_scores)

	plt.show()




