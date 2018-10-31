# coding: utf-8

import numpy as np

def load_field_file(path):
    with open(path, 'r') as f:
        width, height = map(int, f.readline().split())  #1行目から縦と横の大きさを代入

        value = np.genfromtxt(path, dtype=int, delimiter=' ', skip_header=1, max_rows=width)    #タイルの点数

        for _ in range(width):  #タイルの点数の部分は読み飛ばし _で変数未使用を表す
            f.readline()

        own_a1_x, own_a1_y = map(int, f.readline().split())    #エージェントの位置
        own_a2_x, own_a2_y = map(int, f.readline().split())
        own_a1 = {'x':own_a1_x - 1, 'y':own_a1_y - 1}   #内部的な座標に変換（インデックスは0から始まる）
        own_a2 = {'x':own_a2_x - 1, 'y':own_a2_y - 1}

    return width, height, value, own_a1, own_a2

'''
# for check
print(load_field_file("shape_info.txt"))
'''