from __future__ import print_function
from __future__ import division

import random
import math
from collections import deque
import numpy as np 
import matplotlib.pyplot as plt

COLOR_NAMES = ["red", "yellow", "green", "blue", "white"]
COLORS = range(5)
VALUES = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]

# dictionaries mapping colors to indices and vice versa 
COL_TO_IND = {}
IND_TO_COL = {}
for i in range(len(COLOR_NAMES)): 
	COL_TO_IND[COLOR_NAMES[i]] = i
	IND_TO_COL[i] = COLOR_NAMES[i]

# print(COLORS)
# print(COL_TO_IND)
# print(IND_TO_COL)

