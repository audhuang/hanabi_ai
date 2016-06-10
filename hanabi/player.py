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

# total number of unique cards 
NUM_COLORS = len(COLORS)
NUM_VALUES = len(list(set(VALUES)))
NUM_HAND = 5
MULT_DIC = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}

FRESH_BELIEF = np.zeros([NUM_COLORS, NUM_VALUES])
for i in range(NUM_VALUES): 
	FRESH_BELIEF[:, i] = MULT_DIC[i+1] #/ (len(COLORS) * len(VALUES))


class player(object): 

	def __init__(self, known, others, hints, bombs):

		self.known = known
		self.others = others
		self.beliefs = initialize_beliefs(known) # each card has an equal chance of being played 
		self.new_beliefs = self.beliefs 

		self.bombs = bombs
		self.hints = hints 

		self.old_state = self.get_state()
		self.new_state = self.old_state
		# self.newest_state = np.hstack(self.beliefs, self.others, self.hints, self.bombs)



# UPDATE BELIEFS

	def get_state(self): 
		state = np.hstack((self.hints, self.bombs))

		for i in range(NUM_HAND): 
			temp = self.beliefs[:, :, i].flatten()
			state = np.hstack((state, (temp / np.sum(temp))))
		state = np.hstack((state, self.others.flatten()))

		return state 


	# when you discard then draw, remove the card at the index 
	# change your beliefs because of the discarded card 
	# insert a fresh one at the rightmost index with updated beliefs
	def discard_draw_update(self, known, index, color, value, hints, bombs):
		# self.newest_state = np.hstack(self.beliefs, self.others, self.hints, self.bombs)
		print("old known ", self.known)
		self.old_state = self.get_state()

		self.known = known
		print("known ", known)

		self.beliefs = np.delete(self.beliefs, index, axis=2) 
		self.beliefs[color, (value-1), :] -= 1
		self.beliefs = np.insert(self.beliefs, (NUM_HAND-1), (FRESH_BELIEF - known), axis=2)

		self.hints = hints
		self.bombs = bombs

		self.new_state = self.get_state()

	# when someone else draws, subtract one from the card they drew
	def draw_update(self, known, other, color, value, hints, bombs): 
		print("old known ", self.known)
		self.others = other 
		self.known = known
		print("known ", known)

		self.beliefs[color, (value-1), :] -= 1

		self.hints = hints
		self.bombs = bombs

		# self.newest_state = np.hstack(self.beliefs, self.others, self.hints, self.bombs)
		self.new_state = self.get_state()


	# when you hint 
	def me_hint(self, hints): 
		# self.newest_state = np.hstack(self.beliefs, self.others, self.hints, self.bombs)
		self.old_state = self.get_state()

		self.hints = hints 

		self.new_state = self.get_state()

	# when you are neither hinted nor the hinter  
	def other_hint(self, hints): 
		self.hints = hints 
		# self.newest_state = np.hstack(self.beliefs, self.others, self.hints, self.bombs)
		self.new_state = self.get_state()


	# when you get hinted, update your beliefs 
	def hint_update(self, known, indices, which, value, hints, bombs): 
		self.known = known 

		if which == 'color': 
			for i in range(NUM_HAND): 
				if i not in indices: 
					self.beliefs[value, :, i] = 0
				elif i in indices: 
					for j in COLORS: 
						if j != value: 
							self.beliefs[j, :, i] = 0
						# elif j == value: 
						# 	self.beliefs[j, :, i] = self.beliefs[j, :, i] - self.known[j, :]

		elif which == 'value': 
			for i in range(NUM_HAND): 
				if i not in indices: 
					self.beliefs[:, (value), i] = 0
				elif i in indices: 
					for j in range(NUM_VALUES): 
						if j != (value): 
							self.beliefs[:, j, i] = 0
						# elif j == (value-1): 
						# 	self.beliefs[:, j, i] = self.beliefs[:, j, i] - self.known[j, :]

		self.hints = hints
		self.bombs = bombs

		self.new_state = self.get_state()

		# flip own bool? 



#===============================================================================
# Helper Functions
#===============================================================================

def initialize_beliefs(known): 

	beliefs = np.zeros([NUM_COLORS, NUM_VALUES, NUM_HAND])
	for i in range(NUM_VALUES): 
		beliefs[:, i, :] = MULT_DIC[i+1] 
	for i in range(known.shape[0]): 
		for j in range(known.shape[1]): 
			beliefs[i, j, :] -= known[i][j]
	return beliefs



#===============================================================================
# TEST
#===============================================================================
# p = player()
# p.discard_draw_update(3)



