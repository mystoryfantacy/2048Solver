import numpy as np
import math
import copy
import random

class Node():
    stringify = None
    def __init__(self, parent, act, state, prob):
        self.parent = parent
        self.act = act
        self.state = state
        self.factor = 1
        self.n = 0
        self.score = 0.0
        self.prob = prob
        self.act_s =[{} for i in range(len(prob))]
        self.act_n =[0 for i in range(len(prob))]
        self.act_v =[0.0 for i in range(len(prob))]

    def __str__(self):
        s = 'parent:' + str(self.parent) + '\n'
        s += 'act:' + str(self.act) + '\n'
        s += 'prob:' + str(self.prob) + '\n'
        s += 'act_n:' + str(self.act_n) + '\n'
        s += 'act_v:' + str(self.act_v) + '\n'
        s += 'act_s:' + str(self.act_s) + '\n'
        return s

    def is_leaf(self, act, state):
        return state in self.acts[act]

    def is_root(self):
        return self.parent == None

    def add_child(self, act, state, prob):
        self.act_s[act][state] = Node(self, act, state, prob)
        return self.act_s[act][state]

    def get_act(self, act_list):
        return max(act_list, key = lambda i: self.get_act_value(i))

    def get_act_value(self, a):
        return math.sqrt(self.n / (self.act_n[a]+1e-10)) * self.prob[a] * self.factor \
               + self.act_v[a]

    def get_child(self, act, state):
        if not state in self.act_s[act]:
            return None
        return self.act_s[act][state]

    def update(self):
        self.n += 1
        for i in range(len(self.act_n)):
            v = self.act_n[i] * self.act_v[i]
        self.score = v / (self.n+1e-10)

    def update_recursive(self):
        if self.parent:
            act = self.act
            tmp = self.parent.act_n[act] * self.parent.act_v[act]
            self.parent.act_n[act] += 1
            self.parent.act_v[act] = float(self.score + tmp) / self.parent.act_n[act]
            self.parent.update()
            self.parent.update_recursive()

    def print(self, fname):
        fout = open(fname, 'w')
        fout.write("digraph G {\n")
        fout.write("node [\n fontname = \"Courier New\"\n")
        fout.write(" fontsize = 8\n shape = record\n]\n")
        Node._cnt = 0
        self._print(fout)
        fout.write("}")

    def _print(self, fout):
        self._id = Node._cnt
        Node._cnt += 1
        name = 'N' + str(self._id)
        if self.parent:
            fout.write('N' + str(self.parent._id) + '_' + str(self.act) + ' -> ' + name + '\n')
        label = Node.stringify(self.state, end = '\\r')
        node = name + ' [\n label=\"{' + name + '|' + label + '}\"\n]\n'
        fout.write(node)
        for i in range(len(self.act_s)):
            fout.write(name + ' -> ' + name + '_' + str(i) + '\n')

        for i in range(len(self.act_s)):
            for s,n in self.act_s[i].items():
                n._print(fout)



def softmax(x):
    prob = np.exp(x - np.max(x))
    prob /= np.sum(prob)
    return prob

class MCTS():
    def __init__(self, game, policy, n_play_out):
        self.game = copy.deepcopy(game)
        self.game.reset()
        self.root = None
        self.policy = policy
        self.n_playout = n_play_out

    def filter_probs(self, act_list, probs):
        p = 0
        for i in act_list:
            p += probs[i]

        updated_probs = [0.0 for j in range(len(probs))]
        for i in act_list:
            updated_probs[i] = probs[i] / p

        return updated_probs

    def init_act_probs(self):
        act_list, score = self.game.check_state()
        act_probs = [0.0 for i in range(len(self.game.action))]
        for i in act_list:
            act_probs[i] = 1.0 / len(act_list)
        return act_probs

    def play_out(self):
        next_node = self.root
        node = None
        act_list, score = self.game.set(self.root.state)
        act = None
        while len(act_list) and next_node:
            node = next_node
            act = node.get_act(act_list)
            act_list,score = self.game.move(act)
            next_node = node.get_child(act, self.game.state)

        if not next_node:
            prob, values = self.policy(self.game.state)
            act_list, score = self.game.check_state()
            prob = self.filter_probs(act_list, prob)
            next_node = node.add_child(act, self.game.state, prob)

        if not len(act_list):
            next_node.score = score
        else:
            next_node.score = values
        next_node.update_recursive()

    def get_move_prob(self):
        temp = 1e1
        # self.game.set(self.root.state)
        # a, _ = self.game.check_state()
        for i in range(self.n_playout):
            self.play_out()

        #self.root.print('test.gv')
        #probs = softmax(1.0 / temp *(np.log(np.array(self.root.act_n) + 1e-10)))
        x = np.array(self.root.act_n)
        probs = x / np.sum(x)
        if (np.sum(x) == 0):
            print('probs =',x, '/', np.sum(x) ,'=', probs)
            exit()
        return probs

    def update_with_move(self, act, state):
        if act and (state in self.root.act_s[act]):
            self.root = self.root.act_s[act][state]
            self.root.parent = None
        else:
            self.game.set(state)
            self.root = Node(None, None, state, self.init_act_probs())

class MCTSPlayer():
    def __init__(self, game, policy_value_net):
        self.policy_value_net = policy_value_net
        self.mcts = MCTS(game, self.policy, 10)
        self.game = game
        self.actions = np.array(range(len(game.action)), dtype = np.int)
        self.history = []
        self.batch_size = 4 #1024
        self.evaluate_sample_num = 5
        self.evaluate_interval = 1
        self.train_num = 10
        self.epoch = 2
        self.learn_rate = 1e-3

    def policy(self, state):
        state = np.array(self.game.board.decompress(state)).reshape(1, 1, 4, 4)
        probs, score_vec = self.policy_value_net.predict(state)
        i = np.argmax(score_vec[0])
        #print('probs:',probs, 'scores:', score_vec, 'i:', i)
        return probs[0], (1 << (i + 1))

    def play(self):
        self.game.reset()
        state_list = []
        prob_list = []
        score_list = []
        act_list, score = self.game.check_state()
        act = None
        while len(act_list) > 0:
            self.mcts.update_with_move(act, self.game.state)
            prob = self.mcts.get_move_prob()
            state_list.append(self.game.state)
            prob_list.append(prob)
            act = np.random.choice(self.actions, p = prob)
            # print('p=', prob, 'move=', act)
            self.game.move(act)
            act_list, score = self.game.check_state()
        print('score', score)
        score_list = [score] * len(state_list)
        return zip(state_list, prob_list, score_list)

    def score2vec(self, score):
        v = [0] * 12
        idx = -1
        while score != 0:
            score >>= 1
            idx += 1
        v[idx] = 1
        return v

    def train_once(self):
        while 1:
            play_data = self.play()
            self.history.extend(play_data)
            if len(self.history) > self.batch_size:
                print('training...')
                mini_batch = random.sample(self.history, self.batch_size)
                states = np.array([ np.array(self.game.board.decompress(b[0])).reshape(1, 4, 4)
                            for b in mini_batch ])
                probs = np.array([ np.array(b[1]) for b in mini_batch ])
                scores = np.array([ np.array(self.score2vec(b[2])) for b in mini_batch ])
                for j in range(self.epoch):
                    #loss, entropy = self.policy_value_net.train_step(states, probs, scores, self.learn_rate)
                    self.policy_value_net.train_step(states, probs, scores, self.learn_rate)
                self.history = []
                break

    def evaluate(self):
        total_score = 0.0
        for i in range(self.evaluate_sample_num):
          self.game.reset()
          act_list, score = self.game.check_state()
          act = None
          while len(act_list) > 0:
              self.mcts.update_with_move(act, self.game.state)
              prob = self.mcts.get_move_prob()
              act = np.argmax(prob)
              try:
                  self.game.move(act)
              except ValueError:
                  print('prob=',prob)
                  print(ValueError)
                  exit()

              act_list, score = self.game.check_state()
          print('Game', i, 'score', score)
          total_score += score
        print('average score:',total_score / self.evaluate_sample_num)

    def train(self):
        for i in range(self.train_num):
            self.train_once()
            if i % self.evaluate_interval == 0:
                self.evaluate()
        self.policy_value_net.save_model('game_2048_pv.weight')



if __name__ == '__main__':
    import game as g
    game = g.Game2048()
    Node.stringify = game.board.stringify

    from game2048_policy_net import PolicyValueNet as PV_Net
    def simple_policy(s):
        n = len(game.action)
        return [1.0/n for i in range(n)], 128

    player = MCTSPlayer(game, PV_Net())
    player.train()
