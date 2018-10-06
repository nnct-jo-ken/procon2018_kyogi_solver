# coding: utf-8

import os, time
import copy
import numpy as np
import game
import player

DEBUG = False    #デバッグ時はTrue

RECORD_NUM = 1000  #対局データ作成数
TURN = 60   #1試合あたりのターン数
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "record")  #出力ディレクトリ
os.makedirs(OUTPUT_DIR, exist_ok=True)  #出力ディレクトリの作成

players = {
    game.OWN_1: player.RandomUniform(),
    game.OWN_2: player.RandomUniform(),
    game.OPPONENT_1: player.RandomUniform(),
    game.OPPONENT_2: player.RandomUniform()
}
# players = {
#     game.OWN_1: player.RandomMTS(100, 5),
#     game.OWN_2: player.RandomMTS(100, 5),
#     game.OPPONENT_1: player.RandomMTS(100, 5),
#     game.OPPONENT_2: player.RandomMTS(100, 5)
# }

def save_record(field, won):
    if DEBUG is True: return    #デバッグ時はファイル生成をしない
    
    X_value = np.array(field.value).reshape([field.width, field.height])
    X_own_status = np.array(field.own_status).reshape([-1, field.width, field.height])
    X_opponent_status = np.array(field.opponent_status).reshape([-1, field.width, field.height])
    X_a1_poss = np.array(field.a1_poss).reshape([-1, field.width, field.height])
    X_a2_poss = np.array(field.a2_poss).reshape([-1, field.width, field.height])

    now = int(round(time.time()*1000))
    path = os.path.join(OUTPUT_DIR, "{0}.npz".format(now))  #ファイル名の指定

    np.savez(path,              #対局データの保存
             X_value=X_value,
             X_own_status=X_own_status,
             X_opponent_status=X_opponent_status,
             X_a1_poss=X_a1_poss,
             X_a2_poss=X_a2_poss,
             won=won)

    try:    #きちんと読み込めるか確認
        np.load(path)
    except:
        os.remove(path)

    if DEBUG is True:   #対局データ中の各種データのサイズを確認
        print("value\n{}".format(len(X_value)))
        print("own status\n{}".format(len(X_own_status)))
        print("opponent status\n{}".format(len(X_opponent_status)))
        print("a1 positions\n{}".format(len(X_a1_poss)))
        print("a2 positions\n{}".format(len(X_a2_poss)))
        print("won\n{}".format(won))

player = (game.OWN_1, game.OWN_2, game.OPPONENT_1, game.OPPONENT_2) #エージェント識別用タプル（リストの変更できないヴァージョン）

for i in range(1, RECORD_NUM+1):
    print("game:", i, end='\r')

    field = game.field()        #フィールド作成
    field.clear()   #フィールド情報をクリア
    field.create_rand_field()   #乱数で初期化

    for j in range(TURN):   #ターン数まで繰り返す   _はカウンタ変数を使わないという意味
        #全エージェントに一通り行動させる

        #フィールドの状態を確認（デバッグ用）
        if DEBUG is True:
            time.sleep(1)
            print() #一行空ける
            print("turn: {0}".format(j))
            field.print_field()

        for turn in player: #各エージェントごとに行動させる
            hand = players[turn].select(field, turn)
            if DEBUG is True:
                print("player:{0} hand:{1}".format(turn, hand))
            if hand is not None:    #次の手があれば
                if field.check_team(turn) == game.OWN:
                    field.own_status.append(field.own_state)
                elif field.check_team(turn) == game.OPPONENT:
                    field.opponent_status.append(field.opponent_state)
                # field.players.append(turn)
                if field.check_team(turn) == game.OWN:
                    if turn == game.OWN_1:
                        field.a1_poss.append()
                if field.check_team(turn) == game.OWN:
                    field.own_status = copy.deepcopy(field.move(field.own_state, turn, hand))    #deepcopyしないと参照渡しみたいになって、ひとつ変えると全部変わる
                elif field.check_team(turn) == game.OPPONENT:
                    field.opponent_status = copy.deepcopy(field.move(field.opponent_state, turn, hand))

    w = field.judge(field.state)      #勝者
    if w == game.OWN:   #勝ち1 負け0に対応させる
        won = 1
    elif w == game.OPPONENT:
        won = 0
    field.status.append(field.state)    #終了時の盤面の保存

    save_record(field, won)  #対局データの保存
    if DEBUG is True:
        print()
        print(field.status)
        print("len: {}", len(field.status))

print("created {} records".format(RECORD_NUM))