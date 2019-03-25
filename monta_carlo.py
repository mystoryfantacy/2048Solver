#!/usr/bin/python
from game import *
import numpy as np
import math
import os
import copy
import sys
import state_db as db
import time

state_store = {}
store_name = 'MontaCarlo2048.txt'

max_store_size = 100000

max_sample_num = 1000

game = Game2048()

def get_act(state, act_list):
    act = 5
    state_act = None
    fetch_from_db = False
    if not state in state_store:
        v = db.query(state)
        if v:
            state_act = [v[1], [[v[2], v[3]], [v[4], v[5]],
                                [v[6], v[7]], [v[8], v[9]]]]
            state_store[state] = state_act
            fetch_from_db = True
        else:
            act = random.sample(act_list, 1)[0]
            return act
    else:
        state_act = state_store[state]

    max_ub = -1
    visit_num = state_act[0]
    current_act = 0
    for i in range(4):
        if i not in act_list:
            state_act[1][i][1] = -1
        else:
            act_num,act_score = state_act[1][i]
            dec = act_num + 0.001
            ub = act_score + 10 * math.sqrt(visit_num / dec)
            if max_ub < ub:
                act = i
                max_ub = ub
    if act > 4:
        if fetch_from_db:
            print('fetch_from_db')
        print(state)
        print(state_act)
        print(state_store[state])
        raise IndexError("act " + str(act) + " is not a valid action")
    return act

max_step_num = 20
def steps(n, g, track):
    act_list, score = g.check_state()
    if n > max_step_num or len(act_list) == 0:
        return score
    act = get_act(g.state, act_list)
    track.append((g.state, act))
    act_list, score = g.move(act)
    return steps(n+1, g, track)

def monta_carlo_sample(game, n):
    global state_store
    for i in range(n):
        tmp_game = copy.copy(game)
        track = []
        score = steps(0, tmp_game, track)
        update_store(score, track)
    state = game.state
    act = 0
    current_act = 0
    max_act_num = 0
    for act_num,act_score in state_store[state][1]:
        print('(', act_num, act_score, ')', end = " ")
        if act_num > max_act_num:
            max_act_num = act_num
            act = current_act
        current_act += 1
    return act

def play_game(epoch = 0):
    db.opendb()
    for i in range(epoch):
        game.reset()
        act_list, score = game.check_state()
        while len(act_list) > 0:
            game.display()
            act = monta_carlo_sample(game, 100)
            print(" act:",act," score:", score)
            print('-' * 50)
            # print('game:',game.state," act:",act," score:", score)
            act_list, score = game.move(act)
        print("--score", score)
    db.closedb()

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

def write_to_db(store_factor):
    total_len = len(state_store)
    store_len = total_len * store_factor
    cnt = 0
    drop_items = []
    for s,v in state_store.items():
        if cnt >= store_len:
            break
        db.update(s, cnt = v[0],
                  a0_cnt = v[1][0][0], a0_score = v[1][0][1],
                  a1_cnt = v[1][1][0], a1_score = v[1][1][1],
                  a2_cnt = v[1][2][0], a2_score = v[1][2][1],
                  a3_cnt = v[1][3][0], a3_score = v[1][3][1])
        drop_items.append(s)
        cnt += 1
    for s in drop_items:
        del state_store[s]

def update_store(score, track):
    global state_store
    for state,act in track:
        state_act = None
        if not state in state_store:
            if len(state_store) >= max_store_size:
                write_to_db(0.5)
            v = db.query(state)
            if v:
                state_act = [v[1], [[v[2], v[3]], [v[4], v[5]],
                                    [v[6], v[7]], [v[8], v[9]]]]
                state_store[v[0]] = state_act
            else:
                state_act = [0, [[0, 0] for i in range(4)]]
                state_store[state] = state_act
                db.insert(state)
        else:
            state_act = state_store[state]
        state_act[0] += 1
        state_act[1][act][0] += 1
        tmp = score - state_act[1][act][1]
        state_act[1][act][1] += float(tmp) / state_act[1][act][0]

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


def run_monta_carlo_training(load_data = False):
    if load_data and os.path.exists(store_name):
        load_state_store()
    i = 0
    print_step = max(max_sample_num / 100, 1)
    total_score = 0
    while i < max_sample_num:
        score, track = run_one_episode()
        update_store(score, track)
        i += 1
        total_score += score
        if i % print_step == 0:
            print(i / print_step, '%')
            print("average score:", float(total_score) / print_step)
            total_score = 0

    save_state_store()

def run_monta_carlo_training_db():
    db.opendb()
    i = 0
    print_step = max(max_sample_num / 100, 1)
    total_score = 0
    while i < max_sample_num:
        print('step', i)
        print('run episode')
        score, track = run_one_episode()
        print('update store')
        update_store(score, track)
        i += 1
        total_score += score
        if i % print_step == 0:
            print(i / print_step, '%')
            print("average score:", float(total_score) / print_step)
            total_score = 0
    write_to_db(1)
    db.closedb()

if __name__ == '__main__':
    mode = 'play'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    print('Start Run')
    play_game(100)
    # run_monta_carlo_training_db()
    #if mode == 'train':
    #    # run_monta_carlo_training(load_data=True)
    #    # load_state_store()
    #else:
    #    play_game()
