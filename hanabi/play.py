from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt
import sys 

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
FRESH_BELIEF = np.zeros([NUM_COLORS, NUM_VALUES])
for i in range(NUM_VALUES): 
	FRESH_BELIEF[:, i] = MULT_DIC[i+1] #/ (len(COLORS) * len(VALUES))

action = np.zeros(NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES))

nu = 0.1 # learning rate  
gamma = 0.1 # discount factor 

#===============================================================================
# Iterative Q-Learning Helper Functions
#===============================================================================

# action vector given by (discard, play, hint[colors, values])
# random action by placing 1 in random index of action vector 
def random_action(player): 
	total = NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES)
	action = np.zeros(total)
	i = np.random.randint(total)
	action[i] = 1
	return action

# updating states after a hint 
def hint_update(state):
	state[0] -= 1
	reward = 0
	return state, reward

def discard_update(index, hand, known, hints, bombs, beliefs, others):
	disc = hand[index]
	hints += 1
	reward = 0

	# update known 
	if disc.know_val == False or disc.know_col == False: 
		known[disc.color, (disc.value - 1)] += 1

	beliefs = np.delete(beliefs, index, axis=2)
	beliefs[color, (value-1), :] -= 1
	beliefs = np.insert(beliefs, (NUM_HAND-1), (FRESH_BELIEF-known), axis=2)

	state = np.hstack((hints, bombs))
	for i in range(NUM_HAND): 
		temp = beliefs[:, :, i].flatten()
		state = np.hstack((state, (temp / np.sum(temp))))
	state = np.hstack((state, others.flatten()))

	return state, reward 

def play_update(index, hand, played, known, hints, bombs, beliefs, others): 
	c = hand[index]
	reward = 0

	# check if the card can be played
	success = False
	for i in range(len(played)): 
		if c.color == i and c.value == (played[i]+1): 
			success = True
			reward = c.value

	if c.know_val == False or c.know_col == False: 
		known[c.color, (c.value - 1)] += 1

	if c.value == max(VALUES): 
		hints += 1

	if success == False: 
		self.bombs -= 1

	beliefs = np.delete(beliefs, index, axis=2)
	beliefs[color, (value-1), :] -= 1
	beliefs = np.insert(beliefs, (NUM_HAND-1), (FRESH_BELIEF-known), axis=2)

	state = np.hstack((hints, bombs))
	for i in range(NUM_HAND): 
		temp = beliefs[:, :, i].flatten()
		state = np.hstack((state, (temp / np.sum(temp))))
	state = np.hstack((state, others.flatten()))

	return state, reward

def softmax_policy(probs): 
	norm_probs = probs / np.sum(probs)
	temp = np.random.rand()
	norm_probs = norm_probs - norm_probs[0]

	a = 0
	for i in range(len(probs)): 
		if temp < (norm_probs[i]+a): 
			return i
		else: 
			a += norm_probs[i]


def check_action(self, action, player):
	a = action.index('1')

	if a >= 0 and a < NUM_HAND: 
		self.discard(self, player, a)
	elif a >= NUM_HAND and a < (NUM_HAND * 2): 
		self.play(self, player, (a - NUM_HAND))
	else: 
		temp = a - NUM_HAND * 2
		for i in range(NUM_OTHERS): 
			if temp >= (i * (NUM_COLORS + NUM_VALUES)) and temp < ((i+1) * (NUM_COLORS + NUM_VALUES)):
				target = i
				if player <= target: 
					target += 1

				index = temp - i * (NUM_COLORS + NUM_VALUES)
				if index < NUM_COLORS: 
					self.hint(self, player, target, 'color', index)
				else: 
					self.hint(self, player, target, 'value', (index - NUM_COLORS))

def test_actions(player, state, hints, bombs, beliefs, others, known, 
	o_beliefs, o_others, o_known):

	state_old = state 

	for j in range(len(action)): 
		# new state from hint
		state_new, reward_new = hint_update(old_state)

		# new state from discard 
		state_new, reward_new = discard_update(index, g.hands[i], 
			g.players[i].known, g.players[i].hints, g.players[i].bombs, 
			g.players[i].beliefs, g.players[i].others)

		# new state from play
		state_new, reward_new = play_update(index, g.hands[i], g.played, 
			g.players[i].known, g.players[i].hints, g.players[i].bombs, 
			g.players[i].beliefs, g.players[i].others)

		probs[j] = gamma * np.dot(g.weight, state_new) + reward

	# best_action = np.argmax(probs)
	best_action = softmax_policy(probs)






# check hints, tokens, etc. 

#===============================================================================
# Playing the Game
#===============================================================================

if __name__ == '__main__':

	g = game()
	for i in range(NUM_PLAYERS): 
	
		score_old = g.score()
		state_old = g.players[i].new_state 
		probs = np.empty(action.shape)

		for j in range(len(action)): 

			# new state from hint
			state_new, reward_new = hint_update(old_state)

			# new state from discard 
			state_new, reward_new = discard_update(index, g.hands[i], 
				g.players[i].known, g.players[i].hints, g.players[i].bombs, 
				g.players[i].beliefs, g.players[i].others)

			# new state from play
			state_new, reward_new = play_update(index, g.hands[i], g.played, 
				g.players[i].known, g.players[i].hints, g.players[i].bombs, 
				g.players[i].beliefs, g.players[i].others)

			probs[j] = gamma * np.dot(g.weight, state_new) + reward

		# best_action = np.argmax(probs)
		best_action = softmax_policy(probs)

		# do action 

		# update weights 
		delta = reward + gamma*np.dot(g.weights, g.players[i].new_state) - np.dot(g.weights, state_old)
		weight_new = g.weights + nu * delta * state_old






#===============================================================================
# Testing Functions
#===============================================================================

# g = game()
# g.print_hands()
# # print(g.players[0].beliefs[:, :, 0])
# # print(g.players[1].beliefs[:, :, 0])

# # test that playing works
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


# # test that hinting works 
# g.hint(0, 1, 'value', 0) 
# print("\n")
# for i in range(NUM_HAND): 
# 	print(g.players[1].beliefs[:, :, i])
# print("hints: ", g.players[0].hints, g.players[1].hints)

# # test that discarding works
# g.players[0].beliefs[:, :, 1] = np.zeros([NUM_COLORS, NUM_VALUES])
# g.discard(0, 0) 
# print("\n")

# for i in range(NUM_HAND): 
# 	print(g.players[0].beliefs[:, :, i])
# print("\n")

# for i in range(NUM_HAND): 
# 	print(g.players[1].beliefs[:, :, i])
# print("hints: ", g.players[0].hints, g.players[1].hints)


# # test that hinting works 
# g.hint(0, 1, 'value', 0) 
# print("\n")
# for i in range(NUM_HAND): 
# 	print(g.players[1].beliefs[:, :, i])
# print("hints: ", g.players[0].hints, g.players[1].hints)



