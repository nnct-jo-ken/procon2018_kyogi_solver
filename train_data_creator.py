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
        X_status = npz["X_status"]
        X_players = npz["X_players"]
        won = npz["won"]

        # if DEBUG is True: #デバッグ用 読み込んだ値を表示
        #     print("value\n{}".format(X_value))
        #     print("status\n{}".format(X_status))
        #     print("player\n{}".format(X_players))
        #     print("won\n{}".format(won))

        return X_value, X_status, X_players, won

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
    state_list = []
    player_list = []
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
        value, status, players, won = get_val

        #大きさをフィールドの最大値に固定
        value_pad = np.pad(value, [(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')
        status_pad = np.pad(status, [(0,0),(0, game.MAX_BOARD_SIZE - value.shape[0]),(0, game.MAX_BOARD_SIZE - value.shape[1])], 'constant')

        # 1対局で得られたデータをリストに固め、それをdatasetに追加していく
        # dataset.append([value, status, players, won])
        # players = np.insert(players, 0, [0]).reshape(-1, 1)    #playersとstatusの長さを合わせる 先頭に0を追加
        # for state, player in zip(status, players):
        #     dataset.append([value, state, player, won])
        #     # デバッグ用 データセットの中身を、ひとつずつ表示 1対局あたりターン数ぶん生成される
        #     # print("\n\n\n\n\n\n\n\n\n")
        #     # print(dataset[-1])
        #     # print("\n\n\n\n\n\n\n\n\n")

        # player_list.append(0)  ##playersとstatusの長さを合わせる 先頭に0を追加
        for state, player in zip(status_pad, players):
            value_list.append(value_pad)
            state_list.append(state)
            player_list.append(player)
            won_list.append(won)

    dataset = [np.array(value_list), np.array(state_list), np.array(player_list), np.array(won_list)]

    # print(value_list)

    # random.shuffle(dataset)  #時間の相関をなくす

    return dataset
