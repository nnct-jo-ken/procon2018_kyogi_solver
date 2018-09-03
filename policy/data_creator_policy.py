import torch
import torch.nn as nn
#from torch.autograd import Variable
import numpy as np
import os
import main
import game
import train_utils
import network_policy

class PolicyDataCreator:

    def __init__(self, model ,gamma):
        self.model = model
        self.gamma = gamma  #割引率

    def curve(self, l):
        x = np.arange(l).astype(float)  #0.0, 1.0, 2.0, 3.0, ...
        x[3:] = 1.1
        x[0:3] = 0.01 * (x[0:3] + 1)    #0.01, 0.02, 0.03, 1.1, 1.1, 1.1, ...
        return x
    
    def get_partial(self, record):  #対局データたちから、ランダムで一部の対局データを取得
        try:    #データが抽出できない可能性もあるから
            npz = np.load(record)
            X_player = npz["X_player"]
            X_action = npz["X_action"][1:]
            Won = npz["Won"]

            l = len(player) #手数
            
            mask = np.random.uniform(0, 1, 1) < self.curve(l)
            #0以上1未満1個の一様乱数の配列とcurve()を比較して条件判断し、TrueかFalseのbool型がmaskに入る
            #curve()が返す値をみると、最初の3つしか条件に一致しないから、最初の3つだけがTrueになる

            players = np.array(X_player[mask])    #X_playerにマスクを適用 Trueの要素だけを抜きだせる [-1 1]の形
            actions = np.array(X_action[mask])    #X_actionにマスクを適用

            rs = np.zeros([len(colors)]).reshape([-1, 1])
            rs[-1] = colors[-1]*Won #-1は、最後の要素を表す（最後から1番目） 

            return players, actions, rs
        except: #データが得られなかったら、形だけしかない空のデータを返す
            return np.zeros([0, 1]),\
                   np.zeros([0, main.MAX_BOARD_SIZE, main.MAX_BOARD_SIZE]),\
                   np.zeros([0, 1])

    def multiple(self, board):  #1つの盤面から合計4種類の盤面に増やす
        b_t = np.transpose(board)   #転置（軸が逆になる TA[x,y] = A[y,x]）
        b_r = np.rot90(board, 2)    #180度回転
        b_rt = np.rot90(b_t, 2)     #転置＋180度回転

        boards = np.array([board], [b_t], [b_r], [b_rt])    #オリジナル＋上記3種類のボードの詰め合わせ
        return boards

    def create_train_data(self, records, start):    #records:学習用データ一覧 start:recordsのどこから始めるか（ミニバッチ単位で処理）
        record_players = [] #どっちがプレーしたか 1:自分 -1:敵
        record_actions = [] #移動先
        record_move_from = np.zeros([0, 1])  #移動方向 これでエージェントをわける
        record_rs = np.zeros([0, 1])    #勝ったか負けたか 1:勝ち -1:負け 0:引き分け

        for record_index in range(start, len(records)): #指定された対局データから最後までループ ただ、十分なファイル数を処理したら、ループ中でbreakする
            record = records[record_index]
            players, actions, rs = self.get_partial(record)
            record_players.append(players)  #プレーヤーを管理しているリストに今の対局データのデータを追加
            record_actions.append(actions)  #行動を管理しているリストに今の対局データのデータを追加
            record_rs = np.append(record_rs, rs)    #勝敗の合計を管理しているリストに今の対局データのデータを追加
            if len(record_rs) > 8192:   #8192個のデータを処理したら、break 後でmultiple()関数によって4倍になるかも
                break
        else:
            #対局データの最後に達した(きっちりと固定長のファイル数を処理していないけれど、処理していないファイルがなくなった)
            return record_index+1, None
        record_players = np.concatenate(record_players).reshape([-1, 1])    #デフォルト:axix=0 縦に同じものを連結
        record_actions = np.concatenate(record_actions).reshape([-1, main.MAX_BOARD_SIZE, main.MAX_BOARD_SIZE])  #縦に同じものを連結し、フィールド最大サイズ(12×12)の配列？を1次元的に並べる
        return record_index+1, self.__create_train_data(record_players, record_actions, record_rs)

    def __create_train_data(self, players, actions, rs):
        #訓練用
        X_player = []
        X_action = []
        #教師信号計算用
        pred_player = []
        pred_action = []
        num_action_primes = []
        turn_change = []

        for p, a, in zip(players, actions): #2つの値が同時に更新される
            X_player.append([p]*4)    #actionはmultiple()関数によって4倍になるから、それに合わせる
            X_action.append(self.multiple(a)) #4種類に増やして、末尾に追加

            next_p = -p #次のプレーヤーに変える
            hands = game.hands(a, next_p)   #次のプレーヤーが移動可能な位置
            num_action_primes.append(len(hands)*4)  # 4倍に増えたX_actionに対応
            turn_change.append(p*next_p)    #プレイヤーが変わっていれば-1 変わっていなければ1
            for hand in hands:  #移動可能な位置ごとに
                action_prime = game.move(a, next_p, hand)   #移動した後の盤面
                pred_player.append([next_p]*4)  #プレーヤーを追加
                pred_action.append(self.multiple(action_prime)) #移動した後の盤面を4種類に増幅して、pred_actionの末尾に追加

            #予測
            pred_player = np.array(pred_player)    #リストをnumpy配列に変換
            pred_player = np.reshape(pred_player, [-1, 1])  #1次元に並べる -1は、自動調整の意味
            pred_action = np.array(pred_action)
            pred_action = np.reshape(pred_action, [-1, main.MAX_BOARD_SIZE, main.MAX_BOARD_SIZE]) #盤面を1次元に並べる

            #kerasでいうmodel.predict
            x = [pred_player, pred_action]
            preds = self.model.predict(x)   #ニューラルネットワークにデータを通した結果（Q値）を代入

            #Q値を計算
            targets = np.hstack([rs.reshape([-1, 1])]*4).astype(float)  #[-1, 4] どっちが勝ったかを4倍にして、水平方向に結合 -1は自動調整の意味
            start = 0
            for i in range(len(num_action_primes)): #移動可能な位置を順にたどる
                num = num_action_primes[i] #移動可能な位置
                if num > 0:
                    r_max = np.max(preds[start:start+num])   #startからstart+numの間で最大のQ値を代入
                    targets[i] += self.gamma * r_max * turn_change[i]  #次の行動のQ値
                    start += num    #start+numの次の状態に移行

            #配列を変形
            X_player = np.array(X_player)   #Numpy配列に変換
            X_player = np.reshape(X_player, [-1, 1])    #1次元に変換
            X_action = np.array(X_action)
            X_action = np.reshape(X_action, [-1, game.MAX_BOARD_SIZE, game.MAX_BOARD_SIZE])
            y_target = targets.reshae([-1, 1])

            return X_player, X_action, y_target

    def load_test_record(self, records, start):    #records:テスト用データ一覧 start:recordsのどこから始めるか（ミニバッチ単位で処理）
        record_players = [] #どっちがプレーしたか 1:自分 -1:敵
        record_actions = [] #移動先
        record_move_from = np.zeros([0, 1])  #移動方向 これでエージェントをわける

        for record_index in range(start, len(records)): #指定された対局データから最後までループ ただ、十分なファイル数を処理したら、ループ中でbreakする
            record = records[record_index]
            players, actions = self.get_partial(record)
            record_players.append(players)  #プレーヤーを管理しているリストに今の対局データのデータを追加
            a = self.multiple(actions)
            record_actions.append(a)  #行動を管理しているリストに今の対局データのデータを追加
        else:
            #対局データの最後に達した(きっちりと固定長のファイル数を処理していないけれど、処理していないファイルがなくなった)
            return record_index+1, None
        record_players = np.hstack([record_players]*4).reshape([-1, 1])    #デフォルト:axix=0 縦に同じものを連結
        record_actions = np.array(record_actions)
        record_actions = np.reshape(record_actions, [-1, main.MAX_BOARD_SIZE, main.MAX_BOARD_SIZE])
        return record_index+1, record_players, record_actions