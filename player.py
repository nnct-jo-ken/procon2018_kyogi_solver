# coding: utf-8

import random
import math
import copy
import numpy as np
import game

DEBUG = True

TURN = 30   #探索するターン数 途中からだから、減らしている

class Player:
    def __init__(self):
        pass

    def select(self, field, player):
        return None

class RandomUniform(Player):    #探索なしでランダム打ち
    def __init__(self):
        super().__init__()

    def select(self, field, player):
        return self.select_randomly(field, player)

    def select_randomly(self, field, player):
        if field.check_team(player) == game.OWN:
            hands = field.hands(field.own_state, player)  #可能な手
        elif field.check_team(player) == game.OPPONENT:
            hands = field.hands(field.opponent_state, player)  #可能な手
        if len(hands) == 0: #手がない
            return None
        else:
            choice = random.randrange(len(hands))   #ランダムに一つ選択
            return hands[choice]

players = {
    game.OWN_1: RandomUniform(),
    game.OWN_2: RandomUniform(),
    game.OPPONENT_1: RandomUniform(),
    game.OPPONENT_2: RandomUniform()
}

#dictで管理しているせいで次のプレーヤーを簡単に指定できないから、専用のdictを用意する
next_players = {
    game.OWN_1: game.OWN_2,    #ONW_2
    game.OWN_2: game.OPPONENT_1,    #OPPONENT_1
    game.OPPONENT_1: game.OPPONENT_2,   #OPPONENT_2
    game.OPPONENT_2: game.OWN_1    #OWN_1
}

class RandomMTS(Player):    #モンテカルロ木探索
    def __init__(self, playout_num=100, max_depth=-1):
        super().__init__()
        self.playout_num = playout_num
        self.max_depth = max_depth

    def select(self, field, player):
        return self.search_and_select(field, player, self.playout_num, self.max_depth)

    def search_and_select(self, field, player, playout_num, max_depth):
        root_node = MTSNode(None, field, player, max_depth) #現在の状態をルートノードとして設定
        for _ in range(playout_num):
            node = root_node    #まず、親ノードを設定

            while len(node.hands) == 0 and len(node.children) > 0:  #手がない ＆ 子ノードがある
                node = node.select_node()   #期待値が最大のノード

            if len(node.hands) > 0: #手がある
                node = node.expand_child()  #子ノードを展開

            win = self.playout(node.field, node.player)
            node.backpropagate(win) #敵が勝った回数と総対戦数を計算
        move = root_node.select_move()

        return move

    def playout(self, field, player):
        # field = copy.deepcopy(field) 
        # pass_count = 0
        # while True:
        #     hands = field.hands(field, player)

        #     if len(hands) > 0:
        #         choice = random.randrange(len(hands))
        #         hand = hands[choice]
        #         field.state = field.move(field.state, player, hand)
        #         pass_count = 0
        #     else:
        #         pass_count += 1
        #         if pass_count > 1:
        #             break
        #     player = -player
        # return field.judge(field.state)

        field = copy.deepcopy(field)    #フィールドのコピー

        #プレーヤーがきりのいいところまで終わるまで、全手動
        #その後は、残りターン数がわからないけれど、とりあえず30ターン後の結果を求める

        while player != game.OWN_1:    #最初に戻るまでは、途中のプレーヤーから始める
            hand = players[player].select(field, player)
            if DEBUG is True:
                print(hand) #この部分の処理が行われるタイミングを確認
            if hand is not None:    #次の手があれば
                field.state = copy.deepcopy(field.move(field.state, player, hand))    #deepcopyしないと参照渡しみたいになる
            player = next_players[player]   #次のプレーヤーにする

        for _ in range(TURN):   #ターン数まで繰り返す   _はカウンタ変数を使わないという意味
            #全エージェントに一通り行動させる

            for turn in players: #各エージェントごとに行動させる
                hand = players[player].select(field, turn)
                if hand is not None:    #次の手があれば
                    field.state = copy.deepcopy(field.move(field.state, turn, hand))    #deepcopyしないと参照渡しみたいになって、ひとつ変えると全部変わる

        return field.judge(field.state)      #勝者

class MTSNode:
    def __init__(self, parent, field, player, max_depth=-1, move=None):
        if DEBUG is True:
            print(player)       #エージェントを確認
            print(max_depth)    #探索深さを確認
        self.parent = parent    #親ノード

        self.field = field      #フィールド（いろいろな情報てんこ盛り）
        self.player = player    #エージェント

        self.move = move        #選んだ手
        self.max_depth = max_depth  #残り探索する深さ

        self.children = []  #子ノードたち
        if max_depth == 0:  #探索深さ0 => 末端だから、探索しない
            self.hands = []
        else:
            self.hands = self.field.hands(self.field, self.player)  #着手可能な手を全て取得
            if len(self.hands) == 0:   #どの手も打てない　たぶん、こんなことは起きない
                self.hands.append(None)

        self.opponent_total_wins = 0    #敵が勝った回数
        self.total_playouts = 0     #プレイアウト数

    def expand_child(self): #子ノードを展開
        move = self.hands.pop(random.randrange(len(self.hands)))    #適当な手を次の手に選ぶ
        if move is None:
            child = MTSNode(self, self.field, next_players[self.player], self.max_depth-1, None) #パスして、次のプレーヤーにする
        else:
            self.field.state = copy.deepcopy(self.field.move(self.field.state, self.player, move)) #着手させる
            child = MTSNode(self, self.field, next_players[self.player], self.max_depth-1, move) #着手させた後の子ノードを代入
        self.children.append(child)
        print("child max_depth {}".format(child.max_depth))
        return child

    def select_node(self):  #期待値が最大の子ノードを返す
        max_score = -9999   #最小の値で初期化
        ret = None
        for child in self.children: #子ノードを順に調べる
            ucb = self.ucb(child)   #期待値を計算
            if max_score <= ucb:
                max_score = ucb
                ret = child
        return ret

    def select_move(self):
        if not self.parent is None: #親ノードがある
            raise Exception("selectMove is only for rootNode.")
        if len(self.children) == 0 and len(self.hands) == 0:    #子ノードがない ＆ 手がない
            return None
        else:
            ret = None
            max_score = -10000
            for child in self.children: #子ノードを順に調べる
                score = child.opponent_total_wins / child.total_playouts    #敵の勝率
                if score >= max_score:  #敵の勝率が最大の時
                    ret = child
                    max_score = score
            return ret.move #敵の勝率が最大の手

    def ucb(self, child):   #UCB1アルゴリズムで期待値を計算
        c = 1
        return child.opponent_total_wins / child.total_playouts \
                + c * np.sqrt(math.log(self.total_playouts) / child.total_playouts)

    def backpropagate(self, win):   #勝った回数と試合数を末端のノードからルートまで遡って計算 winは勝ったプレーヤー
        team = [win, win//3, win//3*2]    #勝ったチームを表すstate上の数字
        node = self #自分自身
        while not node is None: #親ノードがある間
            if node.player not in team: #敵が勝っていたら
                node.opponent_total_wins += 1
            node.total_playouts += 1
            node = node.parent  #親ノードにする

    def get_root_node(self):
        node = self
        while not node.parent is None:  #親ノードがある間
            node = node.parent
        return node

    def print_route(self):  #ルートを表示
        node = self
        while not node.parent is None:  #親がいる間
            print(node.move, end="<-")
            node = node.parent
            print("")
