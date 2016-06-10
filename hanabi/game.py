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

# total number of unique cards 
NUM_COLORS = len(COLORS)
NUM_VALUES = len(list(set(VALUES)))
NUM_HAND = 5
MULT_DIC = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
NUM_OTHERS = 1
NUM_PLAYERS = NUM_OTHERS + 1
ACTION_NUM = NUM_HAND * 2 + NUM_OTHERS * (NUM_COLORS + NUM_VALUES)

## REWARD???
## COLORS AS INDICES INSTEAD?

class game(object): 

	def __init__(self): 
		# initial board state stuff 
		self.hints = 8
		self.bombs = 3
		self.played = [0] * len(COLORS)
		self.played_features = np.zeros([NUM_COLORS, NUM_VALUES])

		# set up deck
		self.deck = deck()

		# set up discard pile
		self.discarded = []
		self.discarded_features = np.zeros([NUM_COLORS, NUM_VALUES])

		# set up each of the players' hands
		self.hands = []
		for i in range(NUM_PLAYERS): 
			self.hands.append(self.deck.deal())

		# set up player states
		self.players = []
		for i in range(NUM_PLAYERS): 
			# cards you see in others' hands
			known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
			# create player with unfucked beliefs 
			self.players.append(player(known, self.get_others_hands(i), self.hints, self.bombs, self.played))

		# weight array used for both players 
		self.weights = np.empty([ACTION_NUM, NUM_COLORS * NUM_VALUES * NUM_HAND * NUM_PLAYERS + 2])
		self.weights.fill(0.1)


	# arrays representing number of each color and number of each values for each of others' hands 
	# # OTHER PLAYERS x # COLORS | # OTHER PLAYERS x # VALUES
	def get_known_in_hand(self, index): 
		known_in_hands = np.zeros([NUM_COLORS, NUM_VALUES])
		
		for hand in range(NUM_PLAYERS): 
			# track known cards in others' hands 
			if hand != index: 
				for card in self.hands[hand]: 
					known_in_hands[card.color, (card.value-1)] += 1
			# track known cards in your own hand
			if hand == index: 
				for card in self.hands[hand]: 
					if card.know_val == True and card.know_col == True: 
						known_in_hands[card.color, (card.value-1)] += 1
		
		return known_in_hands

	# arrays representing other players' hands: 
	def get_others_hands(self, index): 
		others_hands = np.zeros([NUM_COLORS, NUM_VALUES, NUM_HAND, NUM_OTHERS])

		k = 0
		for i in range(NUM_PLAYERS): 
			if i != index: 
				for j in range(len(self.hands[i])): 
					others_hands[self.hands[i][j].color, (self.hands[i][j].value-1), j, k] = 1
				k += 1

		return others_hands


	def total_known_cards(self, known_in_hand, played, discarded): 
		return known_in_hand + played + discarded 


	# change bools in target player's cards 
	# 
	# your beliefs dont change 
	# target player's beliefs change 
	# 
	# remove a hint token
	def hint(self, me, player, which, val): 
		indices = [] # keeps track of which cards are hinted 

		# flip values 
		if which == 'value': 
			for i in range(len(self.hands[player])): 
				if self.hands[player][i].value == (val+1): 
					self.hands[player][i].know('value')
					indices.append(i)
					
		# flip colors
		elif which == 'color': 
			for i in range(len(self.hands[player])): 
				if self.hands[player][i].color == val: 
					self.hands[player][i].know('color')
					indices.append(i)

		# print("hinted indices: ", indices)

		# make sure we can actually hint something before updating anything
		if indices != []: 
			
			# update board state 
			self.hints -= 1	

			# update my hints and states 
			self.players[me].me_hint(self.hints)
			for i in range(len(self.hands)): 
				known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
				# update hints for the non-hinted players 
				if i != player: 
					self.players[i].other_hint(self.hints)
				# update the target's beliefs and states 
				elif i == player: 
					self.players[player].hint_update(known, indices, which, val, self.hints, self.bombs)

		# WHAT IF YOU BY PROCESS OF ELIMINATION FLIP YOUR OWN BOOL

		

	# discard own card at index. 
	# draw another to the right side of hand. 
	# 
	# your beliefs change because now you see the card + discard/draw
	# other beliefs change beceause they see the drawn card
	# 
	# flip a token. 
	def discard(self, player, index): 
		# discard 
		disc = self.hands[player].pop(index)
		self.discarded.append(disc)
		self.discarded_features[disc.color, (disc.value-1)] += 1
		# print("discard: ", disc.color, disc.value)

		# update hints
		if self.hints <= 7: 
			self.hints += 1

		# if there are cards remaining, draw
		if self.deck.num_cards > 0: 
			new = self.deck.draw()
			self.hands[player].append(new)
			print("new: ", new.color, new.value)
		
			# update knowns and beliefs 
			for i in range(len(self.hands)): 
				known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
				if i != player: 
					self.players[i].draw_update(True, known, self.get_others_hands(i), new.color, new.value, self.hints, self.bombs, self.played)
				elif i == player: 
					self.players[player].discard_draw_update(True, known, index, disc.color, disc.value, self.hints, self.bombs, self.played)	
		# if deck is empty, dont draw
		else: 
			for i in range(len(self.hands)): 
				known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
				if i != player: 
					self.players[i].draw_update(False, known, self.get_others_hands(i), 0, 0, self.hints, self.bomb, self.played)
				elif i == player: 
					self.players[player].discard_draw_update(False, known, index, disc.color, disc.value, self.hints, self.bombs, self.played)	
		

	# play a card at index, draw another to the right side of hand. 
	# if success: change self.played to reflect. 
	# 	if stack was completed: also flip a token
	# if fail: flip a bomb. append to discarded 
	def play(self, player, index): 
		# take the card out
		c = self.hands[player].pop(index)
		# print("play: ", c.color, c.value)
	
		# check if it can be added to the stack by seeing if it has
		# a 1-higher value for a color
		success = False
		for i in range(len(self.played)): 
			if c.color == i and c.value == (self.played[i]+1): 
				self.played[i] += 1
				self.played_features[c.color, (c.value-1)] += 1
				success = True

		# if completed a stack, add a hint and update arrays
		if success == True and c.value == max(VALUES) and self.hints < 8: 
			self.hints += 1			

		# if fail to play, discard and update arrays, and use up a bomb
		elif success == False: 
			self.discarded.append(c)
			self.discarded_features[c.color, (c.value-1)] += 1
			self.bombs -= 1
		# print("play result: ", success)

		# if there are cards remaining, draw
		if self.deck.num_cards > 0: 
			new = self.deck.draw()
			self.hands[player].append(new)
			print("new: ", new.color, new.value)
		
			# update knowns and beliefs 
			for i in range(len(self.hands)): 
				known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
				if i != player: 
					self.players[i].draw_update(True, known, self.get_others_hands(i), new.color, new.value, self.hints, self.bombs, self.played)
				elif i == player: 
					self.players[player].discard_draw_update(True, known, index, c.color, c.value, self.hints, self.bombs, self.played)	
		# if deck is empty, dont draw
		else: 
			for i in range(len(self.hands)): 
				known = self.total_known_cards(self.get_known_in_hand(i), self.played_features, self.discarded_features) 
				if i != player: 
					self.players[i].draw_update(False, known, self.get_others_hands(i), 0, 0, self.hints, self.bombs, self.played)
				elif i == player: 
					self.players[player].discard_draw_update(False, known, index, c.color, c.value, self.hints, self.bombs, self.played)	
	
	# return score, the sum of highest-played cards over the colors
	def score(self): 
		return np.sum(self.played)

	# check if the game has been lost
	def lost(self): 
		if self.bombs == 0 or self.deck.num_cards == 0: 
			return True 
		else: 
			return False 

	# print hands 
	def print_hands(self): 
		for i in range(NUM_PLAYERS): 
			print("player " + str(i))
			for j in range(NUM_HAND): 
				print(self.hands[i][j].name)
			print("\n")



	# DISCARD(x num_hand) - PLAY(x num_hand) - HINT(x (PLAYERS-1) x (COLORS + VALUES)))
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



			


#===============================================================================
# Helper Functions
#===============================================================================



# dictionary of topmost number for each color in the played stack
def played_dic(): 
	dic = {}
	for color in COLOR_NAMES: 
		dic[color] = 0
	return dic 

def multiplicity_dic(): 
	dic = {}

	for value in range(NUM_VALUES): 
		dic[value+1] = VALUES.count(value+1)

	return dic





#===============================================================================
# Test Functions
#===============================================================================

# # check to see deck works and can be drawn from and dealt from 
# hanabi = game() 
# print(hanabi.played)

# hand = hanabi.deck.deal()
# for card in hand: 
# 	print(card.name)
# print(hanabi.deck.num_cards)





