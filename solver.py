# coding: utf-8

import random

def solve(field):
    '''
    今は、ランダムで返しているだけ
    各プレーヤーの移動方向を、相対座標で出力
    '''
    buf = ""
    num = 0
    while num < 2:
        buf += str(random.randint(-1, 1))
        buf += ' '
        buf += str(random.randint(-1, 1))
        buf += ':'
        buf += '0'
        buf += ':'
        num += 1
    return buf