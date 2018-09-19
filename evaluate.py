# coding: utf-8

import player
import neural_player

DEBUG = False

TURN = 60

def play(target, opponent, play_num):
    #入力
    #   * target:評価するプレーヤ（学習済みのモデルで評価値を推定する）
    #   * opponent:targetと対戦する相手
    #   * playnum:対戦回数

    # global game #このやり方だと、2回目で死ぬ

    #こうしないと、gameをローカル変数だと見なされてしまう
    #なんか書き方が汚いけれど、仕方がなかったんや...
    #直せそうなら直す
    import game

    players = {
        game.OWN_1: target,
        game.OWN_2: target,
        game.OPPONENT_1: opponent,
        game.OPPONENT_2: opponent
    }

    wons = 0    #勝利数

    player = (game.OWN_1, game.OWN_2, game.OPPONENT_1, game.OPPONENT_2) #エージェント識別用タプル（リストの変更できないヴァージョン）

    field = game.field()        #フィールド作成

    for i in range(play_num):   #{play_num}回対局を繰り返す
        print("game:", i, end='\r')

        field.clear()   #フィールド情報をクリア
        field.create_rand_field()   #乱数で初期化

        for game in range(TURN):    #1試合あたり{TURN}ターンで打ち切る

            for turn in player: #各エージェントごとに行動させる
                hand = players[turn].select(field, turn)
                if DEBUG is True:
                    print("player:{0} hand:{1}".format(turn, hand))
                if hand is not None:    #次の手があれば
                    field.status.append(field.state)
                    field.players.append(turn)
                    field.state = field.move(field.state, turn, hand)

        won = field.judge(field.state)      #勝者
        if won > 0: wons += 1   #自陣の勝ちなら、勝ち数を1つ増やす

    return wons / play_num  #勝率

def evaluate_model(model, play_num):
    target = neural_player.DQNPlayer(model)
    opponent = player.RandomUniform()   #本当はランダム打ちのモンテカルロ木探索にしたい
    return play(target, opponent, play_num)