# coding: utf-8

import os, time
import numpy as np
import game
import player

DEBUG = True

RECORD_NUM = 10000  #対局データ作成数
TURN = 60   #1試合あたりのターン数
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "record")  #出力ディレクトリ

players = {
    game.OWN_1: player.RandomUniform(),
    game.OWN_2: player.RandomUniform(),
    game.OPPONENT_1: player.RandomUniform(),
    game.OPPONENT_2: player.RandomUniform()
}

def save_record(field, won):
    if DEBUG is True: return    #デバッグ時はファイル生成をしない
    
    X_value = np.array(field.value).reshape([-1, field.width, field.height])
    X_state = np.array(field.state).reshape([-1, field.width, field.height])
    X_players = np.array(field.players).reshape([-1, 1])

    now = int(round(time.time()*1000))
    path = os.path.join(OUTPUT_DIR, "{0}.npz".format(now))  #ファイル名の指定

    np.savez(path,              #対局データの保存
             X_value=X_value,
             X_state=X_state,
             X_players=X_players,
             won=won)

    try:    #きちんと読み込めるか確認
        np.load(path)
    except:
        os.remove(path)

for i in range(1, RECORD_NUM):
    print("game:", i, end='\r')

    field = game.field()        #フィールド作成
    field.create_rand_field()   #乱数で初期化

    for i in range(TURN):   #ターン数まで繰り返す
        #エージェントに一通り行動させる（値で管理するとか、もっと考えれば良かった...）

        for turn in range(game.OWN_1, game.OWN_2):  #味方
            hand = players[turn].select(field, turn)
            if hand is not None:    #次の手があれば
                field.status.append(field.state)
                field.players.append(turn)
                field.state = field.move(field.state, turn, hand)

        for turn in range(game.OPPONENT_1, game.OPPONENT_2, -1):   #敵 -1,-2の順に辿りたいから、stepは-1
            hand = players[turn].select(field, turn)
            if hand is not None:    #次の手があれば
                field.status.append(field.state)
                field.players.append(turn)
                field.state = field.move(field.state, turn, hand)

        #フィールドの状態を確認（デバッグ用）
        time.sleep(1)
        field.print_field()

    won = field.judge(field.state)      #勝者
    field.status.append(field.state)    #終了時の盤面の保存

    save_record(field, won)  #対局データの保存