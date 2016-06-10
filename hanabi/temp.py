def discard_update(index, hand, known, hints, bombs, beliefs, others, known, 
	o_beliefs, o_others, o_known):
	disc = hand[index]
	hints += 1
	reward = 0

	# update known 
	if disc.know_val == False or disc.know_col == False: 
		known[disc.color, (disc.value - 1)] += 1

	beliefs = np.delete(beliefs, index, axis=2)
	beliefs[color, (value-1), :] -= 1
	beliefs = np.insert(beliefs, (NUM_HAND-1), (FRESH_BELIEF-known), axis=2)

	
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


def hint_update(player, which, value, hands, hints, bombs, beliefs, known, others, o_beliefs, o_known, o_others):
	# update my state
	hints -= 1
	reward = 0

	# hint opponent
	indices = [] # keeps track of which cards are hinted 
	# flip values 
	if which == 'value': 
		for i in range(len(hands[player])): 
			if hands[player][i].value == (val+1): 
				if hands[player][i].know_col == True: 
					o_known[hands[player][i].color][hands[player][i].value] += 1
				indices.append(i)
	# flip colors
	elif which == 'color': 
		for i in range(len(self.hands[player])): 
			if hands[player][i].color == val: 
				if hands[player][i].know_val == True: 
					o_known[hands[player][i].color][hands[player][i].value] += 1
				indices.append(i)

	# update opponent beliefs. opponent others stays the same
	if which == 'color': 
		for i in range(NUM_HAND): 
			if i not in indices: 
				o_beliefs[value, :, i] = 0
			elif i in indices: 
				for j in COLORS: 
					if j != value: 
						o_beliefs[j, :, i] = 0
	elif which == 'value': 
		for i in range(NUM_HAND): 
			if i not in indices: 
				o_beliefs[:, (value), i] = 0
			elif i in indices: 
				for j in range(NUM_VALUES): 
					if j != (value): 
						o_beliefs[:, j, i] = 0

	return reward, hints, bombs, beliefs, known, others, o_beliefs, o_known, o_others