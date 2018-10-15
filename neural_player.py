# coding: utf-8

import copy
import numpy as np
import torch
import game
import player

DEBUG = False

class DQNPlayer(player.Player):
    def __init__(self, model):
        super().__init__()  #親クラスのコンストラクタ
        self.model = model  #評価値生成に用いるモデルを設定
        if torch.cuda.is_available(): #GPUが使える場合は、モデルをGPUに転送
            self.model.cuda()

    def select(self, field, player):
        value = field.value
        own_state = field.own_state
        opponent_state = field.opponent_state
        pos = field.conv_agent_field([field.conv_turn_pos(player)['x'], field.conv_turn_pos(player)['y']])

        #大きさをフィールドの最大値に固定
        value = np.pad(value, [(0, game.MAX_BOARD_SIZE - field.value.shape[0]),(0, game.MAX_BOARD_SIZE - field.value.shape[1])], 'constant')
        own_state = np.pad(own_state, [(0, game.MAX_BOARD_SIZE - field.value.shape[0]),(0, game.MAX_BOARD_SIZE - field.value.shape[1])], 'constant')
        opponent_state = np.pad(opponent_state, [(0, game.MAX_BOARD_SIZE - field.value.shape[0]),(0, game.MAX_BOARD_SIZE - field.value.shape[1])], 'constant')
        pos = np.pad(pos, [(0, game.MAX_BOARD_SIZE - field.value.shape[0]),(0, game.MAX_BOARD_SIZE - field.value.shape[1])], 'constant')

        inputs = np.array([value, own_state, opponent_state, pos]).reshape(1, 4, game.MAX_BOARD_SIZE, game.MAX_BOARD_SIZE)  #入力データを結合させる　サイズは[バッチ, チャンネル, height, width]

        self.model.eval()   #推論モード
        inputs = torch.from_numpy(inputs).float()
        if torch.cuda.is_available(): #GPUを使える時
            inputs = torch.autograd.Variable(inputs.cuda())
        else:
            inputs = torch.autograd.Variable(inputs)

        out = self.model(inputs)
        if DEBUG is True:
            print(out)
        max_sorted = torch.sort(out, descending=True)   #価値が高い順に並べる
        sorted_directions = max_sorted[1][0].tolist()   #移動方向のみのリストを生成

        for move_direction in sorted_directions:
            hand = field.conv_direction_hand(move_direction, own_state, opponent_state, [field.conv_turn_pos(player)['x'], field.conv_turn_pos(player)['y']])
            if DEBUG is True:
                print("dict : ", move_direction, "hand : ", hand)
            if hand is None: continue   #不可能な手だったら、次点の手について処理する

            return hand

# class MinimaxDQNPlayer(player.Player):
#     def __init__(self, model):
#         super().__init__()  #親クラスのコンストラクタ
#         self.model = model  #評価値生成に用いるモデルを設定

#     def select(self, field, player):
#         pass