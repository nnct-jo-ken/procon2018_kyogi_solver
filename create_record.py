# coding: utf-8

import os, time
import numpy as np
import game
import player

DEBUG = True    #デバッグ時はTrue

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

player = (game.OWN_1, game.OWN_2, game.OPPONENT_1, game.OPPONENT_2) #エージェント識別用タプル（リストの変更できないヴァージョン）

for i in range(1, RECORD_NUM+1):
    print("game:", i, end='\r')

    field = game.field()        #フィールド作成
    field.create_rand_field()   #乱数で初期化

    for _ in range(TURN):   #ターン数まで繰り返す   _はカウンタ変数を使わないという意味
        #全エージェントに一通り行動させる

        #フィールドの状態を確認（デバッグ用）
        if DEBUG is True:
            time.sleep(1)
            print() #一行空ける
            field.print_field()

        for turn in player: #各エージェントごとに行動させる
            hand = players[turn].select(field, turn)
            if DEBUG is True:
                print("player:{0} hand:{1}".format(turn, hand))
            if hand is not None:    #次の手があれば
                field.status.append(field.state)
                field.players.append(turn)
                field.state = field.move(field.state, turn, hand)

    won = field.judge(field.state)      #勝者
    field.status.append(field.state)    #終了時の盤面の保存

    save_record(field, won)  #対局データの保存