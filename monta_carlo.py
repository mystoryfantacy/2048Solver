#!/usr/bin/python
from game import *
import numpy as np
import math
import os

state_store = {}
store_name = 'MontaCarlo2048.txt'

max_store_size = 100000000

max_sample_num = 100000

game = Game2048()
#def run_monta_carlo():

def get_act(state, act_list):
    act = 5
    if not state in state_store:
        act = random.sample(act_list, 1)[0]
    else:
        max_ub = 0
        visit_num = state_store[state][0]
        current_act = 0
        for i in range(4):
            if i not in act_list:
                state_store[state][1][i][1] = -1
            else:
                act_num,act_score = state_store[state][1][i]
                dec = act_num + 0.001
                ub = float(act_score) / dec + 10 * math.sqrt(visit_num / dec)
                if max_ub < ub:
                    act = i
                    max_ub = ub
    return act

def run_one_episode():
    game.reset()
    track = []
    act_list, score = game.check_state()
    # game.display()
    while len(act_list) > 0:
        act = get_act(game.state, act_list)
        track.append((game.state, act))
        act_list, score = game.move(act)
        # print('[move]',act)
        # game.display()
    # print('---- score:', score)
    return score, track

def update_store(score, track):
    for state,act in track:
        if not state in state_store:
            if len(state_store) < max_store_size:
                state_store[state] = [0, [[0, 0] for i in range(4)]]
            else:
                continue
        state_store[state][0] += 1
        state_store[state][1][act][0] += 1
        state_store[state][1][act][1] += score

def save_state_store():
    print('saving data to', store_name)
    with open(store_name, 'w') as f:
        for state,info in state_store.items():
            s = str(state) + ' ' + str(info[0]) + ' '
            for act_num, act_score in info[1]:
              s += str(act_num) + '|' + str(act_score) + ' '
            s += '\n'
            f.write(s)

def load_state_store():
    print('loading data from', store_name)
    state_store = {}
    with open(store_name, 'r') as f:
        for l in f.readlines():
            table = []
            infos = l.split(' ')
            state = int(infos[0])
            table.append(int(infos[1]))
            act_list = []
            for act_pair in infos[2:-1]:
              act_info = act_pair.split('|')
              act_list.append([int(act_info[0]), int(act_info[1])])
            table.append(act_list)
            state_store[state] = table
    # print(state_store)


def run_monta_carlo(load_data = False):
    if load_data and os.path.exists(store_name):
        load_state_store()
    i = 0
    print_step = max(max_sample_num / 100, 1)
    while i < max_sample_num:
        score, track = run_one_episode()
        update_store(score, track)
        i += 1
        if i % print_step == 0:
            print(i / print_step, '%')
            print(score)
            save_state_store()

    save_state_store()


if __name__ == '__main__':
    print('Start Run')
    run_monta_carlo(load_data=True)
    # load_state_store()
