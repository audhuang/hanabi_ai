from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt

from const import (COLORS, VALUES, COLOR_NAMES)
from card import card
from func import decklist

NUM_HAND = 5


class deck(object): 
	
	def __init__(self): 
		self.cards = deque(decklist()) # list of shuffled cards in the deck
		self.num_cards = len(self.cards) # number of cards remaining in the deck

	# draws one card from the top of the deck
	def draw(self): 
		drawn = self.cards.pop()
		self.num_cards -= 1
		return drawn 

	# deals five cards from the top of the deck 
	def deal(self): 
		hand = []
		for i in range(NUM_HAND): 
			hand.append(self.cards.pop())
		self.num_cards -= NUM_HAND
		return hand


#===============================================================================
# Helper Functions
#===============================================================================




