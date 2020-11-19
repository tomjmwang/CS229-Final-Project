from hanabi import Hanabi, hanabi_cards
import numpy as np
import collections

class DeepQLearning(Hanabi):

    def __init__(self, player_num=2):
        self.player_num = player_num
        self.cards_per_player = 5
        if player_num == 2 or player_num == 3:
            self.cards_per_player = 4
        self.game_states = [] # contains complete info of every player's cards
        self.player_states = [] # contains info of what each player sees
        self.current_stack = []
        self.discard_stack = []
        c, ind = hanabi_cards()
        self.initial_cards = c
        self.index_mappings = ind
        self.cards = None
        self.score = 0
        self.strike = 0
        self.token = 8
        self.current_player = 0
        self.round_end = False
        self.remaining_turns = self.player_num
        self.action_type_count = collections.defaultdict(int)

        self.mask = []
        all_actions, action_index = self.getAllActions()
        self.all_action_pairs = all_actions
        self.action_index = action_index
        self.reset()
        self.input_size = self.getInputState().shape[0]

    def getAllActions(self):
        result = []
        indices = {}
        count = 0
        for i in range(self.player_num):
            for j in range(self.cards_per_player):
                result.append((i, j, 1))
                indices[(i,j,1)] = count
                count += 1
                result.append((i, j, 2))
                indices[(i,j,2)] = count
                count += 1
            for k in range(5):
                result.append((i, k+1)) # second index is the hint type
                indices[(i,k+1)] = count
                count += 1
                result.append((i, k+6)) # 1-5 = color hint, 6-10 = number hint
                indices[(i,k+6)] = count
                count += 1

        return result, indices
    
    def getInputState(self):
        state = []
        for i in range(self.player_num):
            new_index = i + self.current_player
            if new_index >= self.player_num:
                new_index -= self.player_num
            if new_index == self.current_player:
                for j in range(self.cards_per_player):
                    state += self.player_states[new_index][j]
            else:
                for j in range(self.cards_per_player):
                    state += self.game_states[new_index][j]
        state += self.current_stack
        state += self.discard_stack
        state += [self.token]
        return np.array(state)


    def reset(self):
        self.resetGame()
        self.reward = 0
        initial_actions = self.getActions(self.current_player)
        self.mask = [self.action_index[a] for a in initial_actions]

    def step(self, index):
        at_least_once = False
        while True:
            current_state = self.getInputState()
            action = self.all_action_pairs[index]
            actions = self.getActions(self.current_player)
            # print(self.game_states)
            # print(self.current_player)
            # print(actions)
            if self.current_player == 0:
                self.mask = [self.action_index[a] for a in actions]
            else:
                self.mask = []
            if at_least_once and self.current_player == 0:
                r = self.reward
                self.reward = 0
                return current_state, r, False
            if self.current_player == 0:
                at_least_once = True
            else:
                action = self.chooseSemiIntelligentAction(actions)
            current_score = self.score
            current_strike = self.strike
            self.applyAction(action)
            self.reward += 2 * (self.score - current_score) - (self.strike - current_strike)
            self.current_player = self.getNextPlayer()
            if self.game_end:
                return self.getInputState(), r-10, True
            if self.round_end:
                if self.remaining_turns == 0:
                    return self.getInputState(), self.reward, True
                self.remaining_turns -= 1


    def step(self, index):
        action = self.all_action_pairs[index]
        actions = self.getActions(self.current_player)
        # print(self.game_states)
        # print(self.current_player)
        # print(actions)
        self.mask = [self.action_index[a] for a in actions]
        current_score = self.score
        current_strike = self.strike
        self.applyAction(action)
        r = 2 * (self.score - current_score) - (self.strike - current_strike)
        self.current_player = self.getNextPlayer()
        if self.game_end:
            return self.getInputState(), r-10, True
        if self.round_end:
            if self.remaining_turns == 0:
                return self.getInputState(), r, True
            self.remaining_turns -= 1
        return self.getInputState(), r, False
