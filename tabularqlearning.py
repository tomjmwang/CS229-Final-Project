from hanabi import Hanabi, hanabi_cards
import collections, random, pickle


class TabularQLearning(Hanabi):

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

        self.Q = collections.defaultdict(float)
        self.eps = 0.2
        self.discount = 0.95
        self.alpha = 0.05
        self.pi = {}

    def reset(self):
        self.resetGame()

    def chooseQAction(self, actions, state):
        if random.random() < self.eps:
            chosen_action = random.choice(actions)
            return chosen_action, self.Q[(state,chosen_action)]
        max_q = float('-inf')
        max_action = None
        for action in actions:
            if self.Q[(state,action)] > max_q:
                max_q = self.Q[(state,action)]
                max_action = action
        return max_action, max_q

    def calculatePolicy(self):
        self.pi = {}
        state_to_q = {}
        for k,v in self.Q.items():
            if k[0] not in state_to_q:
                self.pi[k[0]] = k[1]
                state_to_q[k[0]] = v
            else:
                if v > state_to_q[k[0]]:
                    state_to_q[k[0]] = v
                    self.pi[k[0]] = k[1]

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
        return tuple(state)

    def simulateQLearning(self):
        self.resetGame()
        last_state = None
        last_q = None
        last_action = None
        while True:
            actions = self.getActions(self.current_player)
            random.shuffle(actions)
            current_state = self.getInputState()
            current_score = self.score
            current_strike = self.strike
            action, q = self.chooseQAction(actions, current_state)
            self.applyAction(action)
            self.current_player = self.getNextPlayer()
            r = 2 * (self.score - current_score) - (self.strike - current_strike)
            if last_state:
                self.Q[(last_state, last_action)] = last_q + self.alpha*(r + self.discount*q - last_q)
            last_state = current_state
            last_action = action
            last_q = q
            if self.game_end:
                self.Q[(last_state,last_action)] = last_q + self.alpha*(r - last_q)
                return
            if self.round_end:
                if self.remaining_turns == 0:
                    self.Q[(last_state,last_action)] = last_q + self.alpha*(r - last_q)
                    return
                self.remaining_turns -= 1

    def evaluatePolicy(self, policy):
        self.resetGame()
        while True:
            player_index = self.current_player
            actions = self.getActions(player_index)
            action = random.choice(actions)
            state = self.getInputState()
            #print(state)
            if state in policy:
                print("policy exist for state", state)
                action = policy[state]
                if action not in actions:
                    print("policy not valid")
                    action = random.choice(actions)
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

def main():

    TRAIN_ITERATION = 50000
    TEST_ITERATION = 1000
    NUM_POINTS = 20
    NUM_PLAYERS = 3
    ITERATION_PER_POINT = int(TRAIN_ITERATION / NUM_POINTS)

    rl = TabularQLearning(player_num=NUM_PLAYERS)
    
    
    
    # Code for learning Q
    # for i in range(TRAIN_ITERATION):
    #     winner = rl.simulateQLearning()
    #     if (i+1) % 1000 == 0:
    #         print("Training iteration", i+1)
    #     if (i+1) % ITERATION_PER_POINT == 0: 
    #         with open("q_data_"+str(i+1), "wb") as f:
    #             pickle.dump(rl.Q, f)
    #         print("Game", i+1, "ends.")
            #print(time.time() - start_time)

    

    

    # Code for calculating win rate

    output_file = open("stats_" + str(NUM_PLAYERS) + ".txt", "w")
    
    for i in range(10):
        print(str((i+1) * ITERATION_PER_POINT))
        with open("q_data_" + str((i+1) * ITERATION_PER_POINT), "rb") as f:
            rl.Q = pickle.load(f)
            rl.calculatePolicy()
        counts = collections.defaultdict(int)
        print(len(rl.pi))
        for j in range(TEST_ITERATION):
            rl.evaluatePolicy(rl.pi)
            counts["score"] += rl.score
            counts["strike"] += rl.strike
        #print("Game", j+1, "ends.")
        #print(counts)
        output_file.write(str((i+1) * ITERATION_PER_POINT) + " iterations: score is" + str(float(counts["score"] / TEST_ITERATION)) + ", strike is"+ str(float(counts["strike"] / TEST_ITERATION))+ "\n")
    output_file.close()

    

if __name__ == "__main__":
    main()