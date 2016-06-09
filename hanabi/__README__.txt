All of the game-playing happens in the main loop of play.py. Right now I test 
playing, discarding, and hinting there but it should be changed. 

Let g be the game instance. 

The game has a list called PLAYERS of player objects. PLAYERS has length NUM_PLAYERS. 
For NUM_PLAYERS = 2 players, we have
g.players[0] 
g.players[1]

PLAY: 
g.play(0, 1) 
All indexing occurs from 0. This causes the 0-index player (player 1) to play
the 1-index card (2nd card from left). 

DISCARD: 
g.discard(0, 1) 
All indexing occurs from 0. This causes the 0-index player (player 1) to discard
the 1-index card (2nd card from left). 

DISCARD: 
g.hint(1, 0, 'color, 0) 
All indexing occurs from 0. This causes the 1-index player (player 2) to hint the
0-index player (player 1) that he has cards of color index 0 (red). 

g.hint(0, 1, 'value', 0) 
**NOTE that the cards can be 1-5, but this corresponds to value indices 0-4. 
All indexing occurs from 0. This causes the 0-index player (player 1) to hint the
1-index player (player 2) that he has cards of value index 0 (value 1). 

Each player has the follow attributes: 
-known (NUM_COLORS x NUM_VALUES array)
known[color][value] holds # of that card which we know for sure exist: 
cards in others' hands, discarded cards, played cards, 
cards in our hand that we know both the color and value of

-beliefs (NUM_COLORS x NUM_VALUES x NUM_HAND array)
beliefs[color][value][index in hand] gives # of unplayed cards with that color/value
for a given card index in our hand. takes into accounts hints. 

-states (1D array of flattened features: # hints, # bombs, normalized beliefs, other players' cards)
-hints (# hints in game)
-bombs (# bombs in game)

