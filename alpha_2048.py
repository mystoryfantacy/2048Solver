import numpy as np
import math

class Node():
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
        for i in range(len(self.act_n)):
            v = self.act_n[i] * self.act_v[i]
        self.score = v / (self.n+1e-10)

    def update_recursive(self):
        if self.parent:
            act = self.act
            tmp = self.parent.act_n[act] * self.parent.act_v[act]
            self.parent.act_n[act] += 1
            self.parent.act_v[act] = float(self.parent.act_v[act]) / self.parent.act_n[act]
            self.parent.update()
            self.parent.update_recursive()

def softmax(x):
    prob = np.exp(x - np.max(x))
    prob /= np.sum(prob)
    return prob

class MCTS():
    def __init__(self, game, policy, n_play_out):
        self.game = game
        self.game.reset()
        self.root = Node(None, None, game.state, self.init_act_probs())
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
        act = -1
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

    def get_move_prob(self, state):
        temp = 1e1
        self.game.set(state)
        for i in range(self.n_playout):
            self.play_out()

        probs = softmax(1.0 / temp *(np.log(np.array(self.root.act_n) + 1e-10)))
        #x = np.array(self.root.act_n)
        #probs = x / np.sum(x)
        return probs

    def update_with_move(self, act, state):
        if state in self.root.act_s[act]:
            self.root = self.root.act_s[act][state]
            self.root.parent = None
        else:
            self.game.set(state)
            self.root = Node(None, state, self.init_act_probs())

class MCTSPlayer():
    def __init__(self, game, policy):
        self.mcts = MCTS(game, policy, 100)
        self.game = game
        self.actions = np.array(range(len(game.action)), dtype = np.int)

    def play(self):
        self.game.reset()
        prob = self.mcts.get_move_prob(self.game.state)
        move = np.random.choice(self.actions, p = prob)
        print('p=', prob, 'move=', move)


if __name__ == '__main__':
    import game as g
    game = g.Game2048()

    def simple_policy(s):
        n = len(game.action)
        return [1.0/n for i in range(n)], 128

    player = MCTSPlayer(game, simple_policy)
    player.play()
