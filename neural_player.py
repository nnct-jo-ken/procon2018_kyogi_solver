# coding: utf-8

import copy
import numpy as np
import torch
import game
import player

class DQNPlayer(player.Player):
    def __init__(self, model):
        super().__init__()  #親クラスのコンストラクタ
        self.model = model  #評価値生成に用いるモデルを設定
        if torch.cuda.is_available(): #GPUが使える場合は、モデルをGPUに転送
            self.model.cuda()

    def select(self, field, player):
        states = [] #playerが移動可能な位置に移動した状態をリストに突っ込む
        eva_val = []    #推論した評価値 statesに対応している

        hands = field.hands(field, player)  #可能な手
        if len(hands) == 0: #手がない
            return None

        for hand in hands:  #着手可能な手を網羅
            # 実際に移動させたくないから、移動前の状態を記憶する
            x = field.conv_turn_pos(player)['x']
            y = field.conv_turn_pos(player)['y']
            state = copy.deepcopy(field.state)

            states.append(field.move(field.state, player, hand))

            field.conv_turn_pos(player)['x'] = x
            field.conv_turn_pos(player)['y'] = y
            field.state = copy.deepcopy(state)

        value_pad = np.pad(field.value, [(0, game.MAX_BOARD_SIZE - field.value.shape[0]),(0, game.MAX_BOARD_SIZE - field.value.shape[1])], 'constant')  #大きさをフィールドの最大値に固定
        value_pad = torch.from_numpy(value_pad) #Tensorに変換
        value_pad = value_pad.reshape(1, 1, game.MAX_BOARD_SIZE, game.MAX_BOARD_SIZE).float()   #モデルの入力に合わせる

        for state in states:    #移動可能な位置に移動した状態について、評価値を推論
            #大きさをフィールドの最大値に固定
            state_pad = np.pad(state, [(0, game.MAX_BOARD_SIZE - state.shape[0]),(0, game.MAX_BOARD_SIZE - state.shape[1])], 'constant')
            state_pad = torch.from_numpy(state_pad) #Tensorに変換
            state_pad = state_pad.reshape(1, 1, game.MAX_BOARD_SIZE, game.MAX_BOARD_SIZE).float()   #モデルの入力に合わせる
            if torch.cuda.is_available(): #GPUを使えるとき
                value_pad = torch.autograd.Variable(value_pad.cuda())
                state_pad = torch.autograd.Variable(state_pad.cuda())
                player = torch.Tensor([player]).cuda()
            else:
                value_pad = torch.autograd.Variable(value_pad)
                state_pad = torch.autograd.Variable(state_pad)
                player = torch.Tensor([player])
            eva_val.append(self.model(value_pad, state_pad, player))

        max_eva_val_index = eva_val.index(max(eva_val)) #評価値のリストのうち、最初に表れた最大値のインデックス

        return hands[max_eva_val_index] #推論した評価値が最も高い移動先（orひっくり返し）を返す

# class MinimaxDQNPlayer(player.Player):
#     def __init__(self, model):
#         super().__init__()  #親クラスのコンストラクタ
#         self.model = model  #評価値生成に用いるモデルを設定

#     def select(self, field, player):
#         pass