import random
import collections

class Hanabi:

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
        self.game_end = False
        self.remaining_turns = self.player_num
        self.action_type_count = collections.defaultdict(int)

    def resetGame(self):
        self.game_states = []
        self.player_states = []
        self.discard_stack = [0 for i in range(50)]
        self.score = 0
        self.strike = 0
        self.token = 8
        self.current_player = 0
        card_list = self.initial_cards.copy()
        self.cards = collections.deque(card_list)
        self.round_end = False
        self.game_end = False
        self.remaining_turns = self.player_num

        random.shuffle(self.cards)
        for i in range(self.player_num):
            player_cards = [] # What other players see
            self_cards = [] # What this player sees
            for j in range(self.cards_per_player):
                card = self.cards.popleft()
                player_cards.append([card[0], card[1], 0, 0]) # card value and 0's indicating no hint
                self_cards.append([0, 0])
            self.game_states.append(player_cards)
            self.player_states.append(self_cards)
        self.current_stack = [0, 0, 0, 0, 0]

    def getActions(self, player_index):
        result = []
        for i in range(self.player_num):
            if player_index == i:
                for j in range(len(self.player_states[i])):
                    if self.game_states[i][j][0] != 0 :
                        result.append((i, j, 1)) # third index is the action, 1 = play, 2 = discard
                        if self.token < 8:
                            result.append((i, j, 2))
            else:
                if self.token > 0:
                    for k in range(5):
                        result.append((i, k+1)) # second index is the hint type
                        result.append((i, k+6)) # 1-5 = color hint, 6-10 = number hint

        return result

    def chooseSemiIntelligentAction(self, actions):
        new_actions = actions.copy()
        random.shuffle(new_actions)
        eps = 0.7
        for a in new_actions:
            i = a[0]
            j = a[1]
            if len(a) == 3:
                if a[2] == 1:
                    if self.player_states[i][j][0] > 0 and self.current_stack[self.player_states[i][j][0]-1] + 1 == self.player_states[i][j][1]:
                        return a
                    if self.player_states[i][j][1] > 0 and self.player_states[i][j][1]-1 in self.current_stack and random.random() > 0.2:
                        return a
            else:
                for k in self.game_states[i]:
                    if j < 6:
                        if j == k[0] and self.current_stack[j-1] == k[1]-1 and random.random() > eps:
                            return a
                    else:
                        if j-5 == k[1] and self.current_stack[k[0]-1] == k[1]-1 and random.random() > eps:
                            return a


        return random.choice(actions)

    def applyAction(self, action):
        if len(action) == 3:
            card = self.game_states[action[0]].pop(action[1])
            self.player_states[action[0]].pop(action[1])
            if len(self.cards) > 0:
                new_card = self.cards.popleft()
                self.game_states[action[0]].append([card[0], card[1], 0, 0])
                self.player_states[action[0]].append([0, 0])
            else:
                self.round_end = True
                self.game_states[action[0]].append([0, 0, 0, 0])
                self.player_states[action[0]].append([0, 0])
            if action[2] == 1:
                self.action_type_count["play"] += 1
                if self.current_stack[card[0]-1] == card[1]-1:
                    self.current_stack[card[0]-1] += 1
                    self.score += 1
                else:
                    self.strike += 1
                    # if self.strike >= 3:
                    #     self.game_end = True
                    #self.discard_stack.append((card[0], card[1]))
                    self.discard_stack[self.index_mappings[(card[0], card[1])]] = 1
            else:
                #self.discard_stack.append((card[0], card[1]))
                self.action_type_count["discard"] += 1
                self.discard_stack[self.index_mappings[(card[0], card[1])]] = 1
                self.token += 1
        else:
            self.action_type_count["hint"] += 1
            for i in range(len(self.game_states[action[0]])):
                if action[1] < 6 and self.game_states[action[0]][i][0] == action[1]:
                    self.game_states[action[0]][i] = [self.game_states[action[0]][i][0], self.game_states[action[0]][i][1], 
                        self.game_states[action[0]][i][3], action[1]]
                    self.player_states[action[0]][i] = [self.player_states[action[0]][i][1], action[1]]
                if action[1] >= 6 and self.game_states[action[0]][i][1] == action[1] - 5:
                    self.game_states[action[0]][i] = [self.game_states[action[0]][i][0], self.game_states[action[0]][i][1], 
                        action[1] - 5, self.game_states[action[0]][i][2]]
                    self.player_states[action[0]][i] = [action[1] - 5, self.player_states[action[0]][i][0]]
            self.token -= 1

    def getNextPlayer(self):
        next_player = self.current_player + 1
        if next_player == self.player_num:
            next_player = 0
        return next_player

    def simulateGame(self):
        self.resetGame()
        it = 0
        while True:
            player_index = self.current_player
            actions = self.getActions(player_index)
            action = random.choice(actions)
            #action = self.chooseSemiIntelligentAction(actions)
            self.applyAction(action)
            # print("Turn", it, "Player", player_index, "Action", action)
            # print(self.game_states)
            # print(self.player_states)
            # print(self.current_stack)
            if self.game_end:
                return self.score, self.strike
            if self.round_end:
                if self.remaining_turns == 0:
                    return self.score, self.strike
                self.remaining_turns -= 1
            self.current_player = self.getNextPlayer()
            it += 1



def hanabi_cards():
    cards = []
    ind = {}
    count = 0
    for i in range(1, 6):
        # i is color index
        for j in range(1,6):
            # j is card value
            cards.append((i, j))
            if j != 5:
                cards.append((i,j))
            if j == 1:
                cards.append((i,j))
            ind[(i,j)] = count
            count += 1
    return cards, ind


def main():
    game = Hanabi(player_num=3)
    count = collections.defaultdict(int)
    for i in range(1000):
        result = game.simulateGame()
        count["score"] += result[0] / 1000
        count["strike"] += result[1] / 1000
    print(count)
    total_actions = game.action_type_count["play"] + game.action_type_count["discard"] + game.action_type_count["hint"]
    print(game.action_type_count["play"] / total_actions, game.action_type_count["discard"] / total_actions , game.action_type_count["hint"] / total_actions)

if __name__ == "__main__":
    main()