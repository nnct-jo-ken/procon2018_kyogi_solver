# coding: utf-8

import numpy as np
import random
import linecache
import game

DEBUG = True   #デバッグ時はTrue

def get_partial(record):    #対局データから、各種データを分離
    try:
        npz = np.load(record)
        X_value = npz["X_value"]
        X_own_status = npz["X_own_status"]
        X_opponent_status = npz["x_opponent_status"]
        X_own_points = npz["X_own_points"]
        X_opponent_points = npz["X_opponent_points"]
        X_a1_poss = npz["X_a1_poss"]
        X_a2_poss = npz["X_a2_poss"]
        X_a1_best_moves = npz["X_a1_best_moves"]
        X_a2_best_moves = npz["X_a2_best_moves"]
        won = npz["won"]

        # if DEBUG is True: #デバッグ用 読み込んだ値を表示
        #     print("value\n{}".format(X_value))
        #     print("status\n{}".format(X_status))
        #     print("player\n{}".format(X_players))
        #     print("won\n{}".format(won))

        return X_value, X_own_status, X_opponent_status, X_own_points, X_opponent_points, X_a1_poss, X_a2_poss, X_a1_best_moves, X_a2_best_moves, won

    except: #データが得られない
        return None

    # 対局データのデバッグ用 例外処理をしないから、事故ったらエラーで止まる
    # npz = np.load(record)
    # X_value = npz["X_value"]
    # X_status = npz["X_status"]
    # X_players = npz["X_players"]
    # won = npz["won"]
    # return X_value, X_status, X_players, won

def get_dataset(record_list_path, batch_size, record_index):
    #入力: 対局データ一覧表 バッチサイズ 対局データの読み出し位置
    # 1対局で得られたデータを種類ごとにリストに追記していき、最後にndarrayに変換してリストに固める

    records = []    #対象の対局データ名
    # dataset = []    #データセット {バッチサイズ}回分の対局データを要素別に格納 対局ごとにリストを作成していた時の名残

    value_list = []
    own_state_list = []
    opponent_state_list = []
    own_point_list = []
    opponent_point_list = []
    a1_pos_list = []
    a2_pos_list = []
    a1_best_move_list = []
    a2_best_move_list = []
    won_list = []

    # 一覧から全行読み取って一括処理する場合
    # with open(record_list_path) as f:
    #     for line in f:
    #         records.append(line)
    # print("{} records".format(len(records)))

    for i in range(record_index+1, record_index + 1 + batch_size):  #getline()は1行目がスタート
        records.append(linecache.getline(record_list_path, i).rstrip('\r\n'))  #1行ごとに読み取り,改行除去 バッチサイズ分の対局データ一覧
    linecache.clearcache()  #linecache.getline に使ったキャッシュをクリア

    for record in records:
        get_val = get_partial(record)
        if get_val is None: #事故った or 読み込むものがなかった
            return None
        value, own_status, opponent_status, own_points, opponent_points, a1_poss, a2_poss, a1_best_moves, a2_best_moves, won = get_val

        #大きさをフィールドの最大値に固定
        value_pad = np.pad(value, [(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')
        own_status_pad = np.pad(own_status, [(0,0),(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')
        opponent_status_pad = np.pad(opponent_status, [(0,0),(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')
        a1_poss_pad = np.pad(a1_poss, [(0,0),(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')
        a2_poss_pad = np.pad(a2_poss, [(0,0),(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')

        # player_list.append(0)  ##playersとstatusの長さを合わせる 先頭に0を追加
        for own_state, opponent_state, own_point, opponent_point, a1_pos, a2_pos, a1_best_move, a2_best_move in zip(own_status_pad, opponent_status_pad, own_points, opponent_points, a1_poss_pad, a2_poss_pad, a1_best_moves, a2_best_moves):
            value_list.append(value_pad)
            own_state_list.append(own_state)
            opponent_state_list.append(opponent_state)
            own_point_list.append(own_point)
            opponent_point_list.append(opponent_point)
            a1_pos_list.append(a1_pos)
            a2_pos_list.append(a2_pos)
            a1_best_move_list.append(a1_best_move)
            a2_best_move_list.append(a2_best_move)
            won_list.append(won)

    dataset = [np.array(value_list), np.array(own_state_list), np.array(opponent_state_list), np.array(own_point_list), np.array(opponent_point_list), np.array(a1_pos_list), np.array(a2_pos_list), np.array(a1_best_move_list), np.array(a2_best_move_list), np.array(won_list)]

    return dataset
