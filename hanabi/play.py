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

ACTION_NUM = NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES)

nu = 0.1 # learning rate  
gamma = 0.5 # discount factor 
epsilon = 0.5 # softmax greed factor 

#===============================================================================
# Iterative Q-Learning Helper Functions
#===============================================================================

# updating state after hinting
def hint_update(state):
	state[0] -= 1
	reward = 0
	return state, reward

# update state if card at index is discarded
def discard_update(index, hand, known, hints, bombs, beliefs, others):
	disc = hand[index]
	hints += 1
	reward = 0

	# update known 
	if disc.know_val == False or disc.know_col == False: 
		known[disc.color, (disc.value - 1)] += 1

	beliefs = np.delete(beliefs, index, axis=2)
	beliefs[disc.color, (disc.value-1), :] -= 1
	beliefs = np.insert(beliefs, (NUM_HAND-1), (FRESH_BELIEF-known), axis=2)

	state = np.hstack((hints, bombs))
	for i in range(NUM_HAND): 
		temp = beliefs[:, :, i].flatten()
		state = np.hstack((state, (temp / np.sum(temp))))
	state = np.hstack((state, others.flatten()))

	return state, reward 

# update state if card at index is played
def play_update(num_cards, index, hand, played, known, hints, bombs, beliefs, others): 
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
		bombs -= 1

	beliefs = np.delete(beliefs, index, axis=2)
	beliefs[c.color, (c.value-1), :] -= 1
	if num_cards > 0: 
		beliefs = np.insert(beliefs, (NUM_HAND-1), (FRESH_BELIEF-known), axis=2)
	else: 
		beliefs = np.insert(beliefs, (NUM_HAND-1), np.zeros([5, 5, 1]), axis=2)


	state = np.hstack((hints, bombs))
	for i in range(NUM_HAND): 
		temp = beliefs[:, :, i].flatten()
		state = np.hstack((state, (temp / np.sum(temp))))
	state = np.hstack((state, others.flatten()))

	return state, reward

# calculate Q(s, a) for each possible action
def action_probabilities(a, i):
	
	if a >= 0 and a < NUM_HAND: 
		if g.deck.num_cards == 0: 
			state_new = np.zeros(g.weights.shape)
			reward_new = 0
		else: 
			state_new, reward_new = discard_update(a, g.hands[i], 
				g.players[i].known, g.players[i].hints, g.players[i].bombs, 
				g.players[i].beliefs, g.players[i].others)

	elif a >= NUM_HAND and a < (NUM_HAND * 2): 
		state_new, reward_new = play_update(g.deck.num_cards, (a - NUM_HAND), g.hands[i], g.played, 
			g.players[i].known, g.players[i].hints, g.players[i].bombs, 
			g.players[i].beliefs, g.players[i].others)
	else: 
		if g.hints >= 0: 
			state_new, reward_new = hint_update(state_old)
		else: 
			state_new = np.zeros(g.weights.shape)
			reward_new = 0

	return state_new, reward_new

# softmax policy for choosing action
# 1-epsilon probability of returning action with highest Q-value 
# epsilon probability of returning other action based on Q-value
def softmax_policy(probs): 
	greatest = np.argmax(probs)

	if np.sum(probs) == 0: 
		norm_probs = np.zeros(probs.shape)
	else: 
		norm_probs = probs / np.sum(probs)
	
	temp = np.random.rand()
	norm_probs = norm_probs - norm_probs[0]
	soft_greatest = 0

	a = 0
	for i in range(len(probs)): 
		if temp >= a and temp < (norm_probs[i] + a): 
			soft_greatest = i
		else: 
			a += norm_probs[i]

	temp = np.random.rand() 
	if temp < epsilon: 
		return soft_greatest
	else: 
		return greatest 

# do the action specified by a 
def check_action(a, player):
	if a >= 0 and a < NUM_HAND: 
		# print("discard card # " + str(a + 1))
		f.write("discard card # " + str(a + 1) + "\n")
		g.discard(player, a)
		
	elif a >= NUM_HAND and a < (NUM_HAND * 2): 
		# print("play card # " + str(a - NUM_HAND + 1))
		f.write("play card # " + str(a - NUM_HAND + 1) + "\n")
		g.play(player, (a - NUM_HAND))
		
	else: 
		temp = a - NUM_HAND * 2
		for i in range(NUM_OTHERS): 
			if temp >= (i * (NUM_COLORS + NUM_VALUES)) and temp < ((i+1) * (NUM_COLORS + NUM_VALUES)):
				target = i
				if player <= target: 
					target += 1

				index = temp - i * (NUM_COLORS + NUM_VALUES)
				if index < NUM_COLORS: 
					# print("hint " + 'color' + str(index + 1))
					f.write("hint " + 'color' + str(index + 1) + "\n")
					g.hint(player, target, 'color', index)

				else: 
					# print("hint " + 'value' + str(index - NUM_COLORS))
					f.write("hint " + 'value' + str(index - NUM_COLORS + 1) + "\n")
					g.hint(player, target, 'value', (index - NUM_COLORS + 1))
					



#===============================================================================
# Playing the Game
#===============================================================================

# implements q-learning
if __name__ == '__main__':

	temp_weights = np.empty([ACTION_NUM, NUM_COLORS * NUM_VALUES * NUM_HAND * NUM_PLAYERS + 2])
	temp_weights.fill(0.1)
	temp_weights[(NUM_HAND*2):, :] = 0.2 # higher weights for hinting

	scores = []
	for i in range(5): 
		g = game()
		g.weights = temp_weights

		f = open('output.txt', 'w')
		count = 0
		hints = []

		while True: 
			count += 1
			print("ITERATION " + str(count))
			f.write("ITERATION " + str(count) + "\n")

			for i in range(NUM_PLAYERS): 

				print("PLAYER " + str(i))
				f.write("player " + str(i) + "\n")

				for j in range(NUM_HAND): 
					f.write(g.hands[i][j].name + " ")
				f.write("\n")

				print("hints: ", g.hints, "bombs: ", g.bombs)
				print("played: ", g.played)
			
				score_old = g.score()
				state_old = g.players[i].new_state 
				probs = np.empty(action.shape)

				for j in range(ACTION_NUM): 
					probs[j] = np.dot(weights[j], state_old)
				f.write("probabilities: " + repr(probs)  + "\n")

				# best_action = np.argmax(probs)
				best = softmax_policy(probs)

				# do action 
				check_action(best, i)

				score_new = g.score()

				# update weights 
				delta = (score_new - score_old) + gamma*np.dot(g.weights[best], g.players[i].new_state) - np.dot(g.weights, state_old)
				weight_new = g.weights[best] + nu * delta * state_old
				# print("new weight" + repr(weight_new))
				f.write("new weight" + repr(weight_new) + "\n")
				# print(weight_new)

				g.weights[best] = weight_new
				# scores.append(g.score())
				# hints.append(g.hints)
				if g.lost() == True: 
					break 
			
			if g.lost() == True: 
				print(g.weights)
				scores.append(g.score())
				print("number of cards remaining: ", g.deck.num_cards)
				temp_weights = g.weights 
				break 
			
			print("\n")

		

	print("training scores", scores)
	plt.figure(1)
	plt.title("scores")
	plt.plot(scores)

	# plt.figure(2)
	# plt.title("hints")
	# plt.plot(hints)

			# while True: 
			# count += 1
			# print("ITERATION " + str(count))
			# f.write("ITERATION " + str(count) + "\n")

			# for i in range(NUM_PLAYERS): 

			# 	print("PLAYER " + str(i))
			# 	f.write("player " + str(i) + "\n")

			# 	for j in range(NUM_HAND): 
			# 		f.write(g.hands[i][j].name + " ")
			# 	f.write("\n")

			# 	print("hints: ", g.hints, "bombs: ", g.bombs)
			# 	print("played: ", g.played)
			
			# 	score_old = g.score()
			# 	state_old = g.players[i].new_state 
			# 	probs = np.empty(action.shape)

			# 	for j in range(len(action)): 
			# 		state_new, reward_new = action_probabilities(j, i)
			# 		probs[j] = reward_new + gamma * np.dot(g.weights, state_new)
			# 	# print("probabilities: " + repr(probs))
			# 	f.write("probabilities: " + repr(probs)  + "\n")

			# 	# best_action = np.argmax(probs)
			# 	best_action = softmax_policy(probs)

			# 	# do action 
			# 	check_action(best_action, i)

			# 	score_new = g.score()

			# 	# update weights 
			# 	delta = (score_new - score_old) + gamma*np.dot(g.weights, g.players[i].new_state) - np.dot(g.weights, state_old)
			# 	weight_new = g.weights + nu * delta * state_old
			# 	# print("new weight" + repr(weight_new))
			# 	f.write("new weight" + repr(weight_new) + "\n")
			# 	# print(weight_new)

			# 	g.weights = weight_new
			# 	# scores.append(g.score())
			# 	# hints.append(g.hints)
			# 	if g.lost() == True: 
			# 		break 
			
			# if g.lost() == True: 
			# 	print(g.weights)
			# 	scores.append(g.score())
			# 	print("number of cards remaining: ", g.deck.num_cards)
			# 	temp_weights = g.weights 
			# 	break 
			
			# print("\n")

	plt.show()
	f.close()






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



