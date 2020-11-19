import numpy as np
from q2_linear import Linear
from deeplearning import DeepQLearning
import sys, getopt
import collections
from configs.hanabi import config


def output_action(model, state):
    #  get q values of all actions
    q_actions = model.get_all_actions_values(state)
    #  sort the actions based on q values DESC
    sorted_actions = np.argsort(q_actions)[::-1]
    return sorted_actions

if __name__ == '__main__':

    checkpoint_dir = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:o:", ["ckptDir="])
    except getopt.GetoptError:
        print('python eval.py -c <checkpoint_dir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-c", "--ckptDir"):
            checkpoint_dir = arg

    # model setup
    env = DeepQLearning(player_num=5)
    model = Linear(env, config)
    model.initialize()
    model.load(checkpoint_dir)
    model.test()
