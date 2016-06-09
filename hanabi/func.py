from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt

from card import card
from const import (COLORS, VALUES, COLOR_NAMES)


# initial full decklist where all colors/values are unknown
def decklist(): 
	deck = []
	deck += [card(value, color, False, False) for value in VALUES for color in COLORS]
	random.shuffle(deck)
	return deck

# gives action


#===============================================================================
# Test Functions
#===============================================================================

# deck = decklist()
# for card in deck: 
	# card.know('color')
	# print(card.know_name)

# test = np.zeros([3, 3, 3])
# test = np.delete(test, 0, axis=2)
# print(test)