# coding: utf-8

import random

class Player:
    def __init__(self):
        pass

    def select(self, field, player):
        return None

class RandomUniform(Player):    #探索なしでランダム打ち
    def __init__(self):
        super().__init__()

    def select(self, field, player):
        return self.select_randomly(field, player)

    def select_randomly(self, field, player):
        hands = field.hands(field, player)  #可能な手
        if len(hands) == 0: #手がない
            return None
        else:
            choice = random.randrange(len(hands))   #ランダムに一つ選択
            return hands[choice]