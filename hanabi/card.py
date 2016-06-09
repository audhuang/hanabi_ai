from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt

from const import COL_TO_IND
from const import IND_TO_COL

class card(object): 
	
	def __init__(self, value, color, k_val, k_col): 
		self.value = value 
		self.color = color 

		self.know_val = k_val
		self.know_col = k_col

		self.name = IND_TO_COL[self.color] + " " + str(self.value)
		self.know_name = self.get_name()

	# sets either the color or value boolean to true
	def know(self, which): 
		if which == 'value': 
			self.know_val = True
		elif which == 'color': 
			self.know_col = True
		self.know_name = self.get_name()

	# returns what we know about the card based on what's been hinted
	def get_name(self): 
		if self.know_val == True and self.know_col == False: 
			return str(self.value)
		if self.know_val == True and self.know_col == True: 
			return IND_TO_COL[self.color] + " " + str(self.value)
		if self.know_val == False and self.know_col == True: 
			return IND_TO_COL[self.color]
		else: 
			return ""


#===============================================================================
# Helper Functions
#===============================================================================


