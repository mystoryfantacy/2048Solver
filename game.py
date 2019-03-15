#!/usr/bin/python
import numpy as np
import random

"""
transition_table[s][dir], dir means direction with 0 meaning right and
1 meaning left
"""
transition_table = np.zeros((65536, 2), np.int)

def init_table():
  # this is a row state, i.e the type of state is uint16
  def revert(state):
      ret = 0
      mask = 0x000F
      for i in range(4):
          ret |= ((state & mask) << ((3 - i) * 4))
          state >>= 4
      return ret

  # `i` is a row state, i.e the type of `i` is uint16
  for i in range(65536):
      state = i
      mask = 0x000F
      res = 0x0000
      for j in range(4):
          if (state & mask) == 0:
              state >>= 4
          else:
              res |= (state & mask)
              mask <<= 4
      state = res
      mask = 0x000F
      res = 0x0000
      add = 1
      for j in range(4):
          if (state & mask) == 0:
              break
          if ((state >> 4) & mask) == (state & mask):
              res |= ((state & mask) + (1 << (j * 4)))
              state >>= 4
          else:
              res |= (state & mask)
          mask <<= 4
      transition_table[i][0] = i ^ res
      transition_table[revert(i)][1] = revert(i) ^ revert(res)

class Board():
  def __init__(self):
      init_table()
  # `s` is a board state, i.e the type of `s` is uint64
  def transpose(self, s):
      s = int(s)
      ret = 0
      for i in range(4):
          for j in range(4):
              v = ((s >> (4 * (i * 4 + j))) & 0x0F)
              ret |= (v << (4 * (j * 4 + i)))
      return ret

  def insert(self, s, k, v):
      if isinstance(k, tuple):
          if len(k) != 2:
              raise ValueError
          k = k[0] * 4 + k[1]
      s = s | (int(v) << (k * 4))
      return s

  def move_up(self, s):
      tmp_s = self.transpose(s)
      for i in range(4):
          offset = i * 16
          tmp_s ^= int(transition_table[((tmp_s >> offset) & 0xFFFF)][1] << offset)
      s = self.transpose(tmp_s)
      return s

  def move_down(self, s):
      tmp_s = self.transpose(s)
      for i in range(4):
          offset = i * 16
          tmp_s ^= int(transition_table[((tmp_s >> offset) & 0xFFFF)][0] << offset)
      s = self.transpose(tmp_s)
      return s

  def move_left(self, s):
      for i in range(4):
          offset = i * 16
          s ^= int(transition_table[((s >> offset) & 0xFFFF)][1] << offset)
      return s

  def move_right(self, s):
      for i in range(4):
          offset = i * 16
          s ^= int(transition_table[((s >> offset) & 0xFFFF)][0] << offset)
      return s

  def get_empty_tile(self, s):
      ret = []
      for i in range(15, -1, -1):
          if((s >> (i * 4)) & 0xF) == 0:
              ret.append(i)
      return ret

  def get_score(self, s):
      score = 1
      for i in range(15, -1, -1):
          v = (1 << ((s >> (i * 4)) & 0xF))
          score = max(score, v)
      return score if score > 1 else 0

  def display(self, s):
      a = [0] * 16
      for i in range(15, -1, -1):
          a[15 - i] = (1 << ((s >> (i * 4)) & 0xF))
          if a[15 - i] == 1:
              a[15 - i] = 0
      for i in range(4):
          for j in range(4):
              print("%4d" %(a[i * 4 + j]),end='')
          print("")



class Game2048():
    board = Board()
    action = [board.move_down, board.move_right, board.move_up, board.move_left]
    def __init__(self):
        self.state = 0
        self.reset()

    def reset(self):
        self.state = 0
        tiles = Game2048.board.get_empty_tile(self.state)
        tiles = random.sample(tiles, 2)
        values = self.get_value(size = 2)
        for i in range(2):
            self.state = Game2048.board.insert(self.state, tiles[i], values[i])

    def get_value(self, size = 1):
        return list(np.random.choice(a= [1,2], size=size, replace=True, p = [0.5, 0.5]))

    def random_policy(self):
        end,score = self.check_state()
        if end:
            return end, score
        else:
            state = self.state
            while state == self.state:
              self.move(np.random.randint(0,4))
            return False, 0

    def move(self, act):
        state = Game2048.action[act](self.state)
        if state != self.state:
          tile = Game2048.board.get_empty_tile(state)
          tile = random.sample(tile, 1)
          value = self.get_value(size = 1)
          self.state = Game2048.board.insert(state, tile[0], value[0])
          return self.check_state()
        else:
          score = Game2048.board.get_score(self.state)
          return True, score

    def check_state(self):
        score = Game2048.board.get_score(self.state)
        for act in Game2048.action:
            state = act(self.state)
            if state != self.state:
              return False, score
        return True, score

    def display(self):
        Game2048.board.display(self.state)


if __name__ == '__main__':
    game = Game2048()
    end,score = game.check_state()
    step_num = 0
    while not end:
        step_num += 1
        print('-'*20)
        game.display()
        end,score = game.random_policy()
    print("Final score:", score, " steps:", step_num)

