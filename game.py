# coding: utf-8

import numpy as np
import random
import copy
import load_field_file

DEBUG = False    #デバッグ時はTrue

EMPTY = 0       #空のマス
OWN = 3         #自チーム
OPPONENT = -3   #敵チーム
OWN_1 = 1       #自チームのエージェント１
OWN_2 = 2
OPPONENT_1 = -1 #敵チームのエージェント１
OPPONENT_2 = -2

MAX_BOARD_SIZE = 12

class field:
    width = 0   #縦
    height = 0  #横
    own_a1, own_a2, opponent_a1, opponent_a2 = {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}   #エージェントの位置
    value = np.zeros([width, height], dtype=int)    #タイルの得点
    state = np.zeros([width, height], dtype=int)    #陣形
    status = [] #ターンごとの陣形を管理
    players = []    #ターンごとのエージェントを管理

    def clear(self):    #フィールド情報をクリア
        self.width = 0   #縦
        self.height = 0  #横
        self.own_a1, self.own_a2, self.opponent_a1, self.opponent_a2 = {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}   #エージェントの位置
        self.value = np.zeros([self.width, self.height], dtype=int)    #タイルの得点
        self.state = np.zeros([self.width, self.height], dtype=int)    #陣形
        self.status = [] #ターンごとの陣形を管理
        self.players = []    #ターンごとのエージェントを管理

    def create_rand_field(self):    #フィールドを生成し、タイルに適当な点数を割り振る
        sum_tile = random.randint(80, 144)  #タイルの数
        self.width = random.randint(7, 12)  #縦の大きさをランダムに決定 80//12=7より、7が一辺の最小サイズ
        while sum_tile // self.width > 12:  #heightが13以上だとルールに反しているから、12以下になるまで乱数生成
            self.width = random.randint(7, 12)
        self.height = sum_tile // self.width    #横の大きさをランダムに決定 上のループで、ルールに適合するはず
        print("{0} {1}".format(self.width, self.height))
        self.value = np.resize(self.value, (self.width, self.height))
        self.state = np.resize(self.state, (self.width, self.height))
        self.own_a1['x'] = random.randint(0, self.width//2) #エージェントの位置をランダムに決定
        self.own_a1['y'] = random.randint(0, self.height//2)
        self.opponent_a1['x'] = random.randint(0, self.width//2)
        self.opponent_a1['y'] = random.randint(0, self.height//2)
        self.own_a2['x'] = self.own_a1['x'] #とりあえず線対称になるはずのエージェントの位置を初期化
        self.own_a2['y'] = self.own_a1['y']
        self.opponent_a2['x'] = self.opponent_a1['x']
        self.opponent_a2['y'] = self.opponent_a1['y']


        bunkatsu = random.randint(0, 2) #0:水平垂直 1:水平 2:垂直

        #エージェントの位置を線対称にする
        if bunkatsu == 0 or bunkatsu == 1:  #水平に線対称
            self.own_a2['x'] = self.width - self.own_a1['x'] - 1
            self.opponent_a2['x'] = self.width - self.opponent_a1['x'] - 1
        if bunkatsu == 0 or bunkatsu == 2:  #垂直に線対称
            self.own_a2['y'] = self.height - self.own_a1['y'] - 1
            self.opponent_a2['y'] = self.height - self.opponent_a1['y'] - 1

        #エージェントの位置をstateに反映
        self.state[self.own_a1['x']][self.own_a1['y']] = OWN_1
        self.state[self.own_a2['x']][self.own_a2['y']] = OWN_2
        self.state[self.opponent_a1['x']][self.opponent_a1['y']] = OPPONENT_1
        self.state[self.opponent_a2['x']][self.opponent_a2['y']] = OPPONENT_2

        for i in range(0, self.width):
            for j in range(0, self.height):

                rand_value = random.randint(-16, 16*9)  #マイナスの点数を10%くらいに抑えるため
                if rand_value > 0:
                    rand_value //= 9   #正の点数は、範囲に収まるように、9で割った商を代入

                self.value[i][j] = rand_value

                if bunkatsu == 0 or bunkatsu == 1:  #水平に線対称
                    if self.width % 2 == 0:   #偶数
                        if i > self.width / 2 - 1:   #下半分
                            self.value[i][j] = self.value[self.width-i-1][j]
                    else:
                        if i > self.width / 2:
                            self.value[i][j] = self.value[self.width-i-1][j]
                if bunkatsu == 0 or bunkatsu == 2:    #垂直に線対称
                    if self.height % 2 == 0:  #偶数
                        if j > self.height / 2 - 1:  #右半分
                            self.value[i][j] = self.value[i][self.height-j-1]
                    else:
                        if j > self.height / 2:
                            self.value[i][j] = self.value[i][self.height-j-1]
        
    def create_from_file(self, path):
        self.width, self.height, self.value, self.own_a1, self.own_a2 = load_field_file.load_field_file(path)
        self.state = np.resize(self.state, (self.width, self.height))

    def print_field(self):
        print(" width:{0}\n height:{1}\n own_a1:{2}\n own_a2:{3}\n opponent_a1:{4}\n opponent_a2:{5}" \
            .format(self.width, self.height, self.own_a1, self.own_a2, self.opponent_a1, self.opponent_a2))
        print("value\n{0}".format(self.value))
        print("state\n{0}".format(self.state))

    def can_move_pos(self, pos):    #その座標は操作可能か（範囲内か） posはリスト [x, y]
        if pos[0] < 0 or pos[0] >= self.width or pos[1] < 0 or pos[1] >= self.height:
            return False
        else:
            return True

    def can_move(self, **player):    #エージェントが移動可能か否か
        if player is None:
            return field.can_move(self.own_a1) or field.can_move(self.own_a2) \
                    or field.can_move(self.opponent_a1) or field.can_move(self.opponent_a2) #誰かがTrueならTrue
        
        for i in range(-1, 2):  #width -1から1
            for j in range(-1, 2):  #height -1から1
                if self.can_move_pos([player['x'] + i, player['y'] + j]) is False:    #範囲外
                    continue
                return True
        return False

    def hands(self, field, player):  #可能な手を一覧 移動可能な位置と、タイルをひっくり返す
        #playerは、一番上にあるエージェントの識別定数でくる conv_turn_posで座標に変換
        hands = []  #可能な移動位置
        #hand = [座標, ひっくり返すか（Trueならひっくり返す Falseなら移動）]　というデータ形式

        x = self.conv_turn_pos(player)['x'] #座標に変換
        y = self.conv_turn_pos(player)['y']

        for i in range(-1, 2):  #width -1から1
            for j in range(-1, 2):  #height -1から1
                #print("x+i:{} y+j:{}".format(x+i, y+j))
                if self.can_move_pos([x + i, y + j]) is False:  #範囲外
                    continue
                elif self.state[x + i][y + j] == EMPTY:  #どちらの陣でもない
                    hands.append([{'x':x+i, 'y':y+j}, False])    #移動
                else:   #どちらかの陣地
                    hands.append([{'x':x+i, 'y':y+j} , False]) #移動
                    if i != 0 or j != 0:    #その場をひっくり返すとエージェントの居場所がなくなる
                        hands.append([{'x':x+i, 'y':y+j} , True])  #ひっくり返すだけ
        
        if DEBUG is True:
            print("player:{0} hands:{1}".format(player, hands))

        return hands

    def conv_turn_pos(self, turn):  #ターン（エージェント）が入力されると、座標が辞書で返る
        if   turn == OWN_1: return self.own_a1
        elif turn == OWN_2: return self.own_a2
        elif turn == OPPONENT_1: return self.opponent_a1
        elif turn == OPPONENT_2: return self.opponent_a2

    def move(self, state, player, hand):   #handはリスト hand[0]は辞書
        if self.can_move_pos([hand[0]['x'], hand[0]['y']]) is False: #移動可能か確認
            raise Exception("Can't move!")
        if hand[1] is False:    #移動なら
            #移動元はチームの値を置く　始
            if player > 0:  #OWN
                self.state[self.conv_turn_pos(player)['x']][self.conv_turn_pos(player)['y']] = OWN
            elif player < 0:    #OPPONENT
                self.state[self.conv_turn_pos(player)['x']][self.conv_turn_pos(player)['y']] = OPPONENT
            #移動元はチームの値を置く　終
            self.state[hand[0]['x']][hand[0]['y']] = player  #移動先にタイルを置く
            self.conv_turn_pos(player)['x'] = hand[0]['x']  #エージェントの移動
            self.conv_turn_pos(player)['y'] = hand[0]['y']
        else:
            self.state[hand[0]['x']][hand[0]['y']] = EMPTY   #タイルを除去

        return state

    def inclose_check(self, state, player_state, team, pos):   #state:self.state player_state:例えばown_state pos:[x,y]リスト
        #すでに判定済みなら、そのまま値を返す state_checkでも確認しているが、一応
        if player_state[pos[0]][pos[1]] != 0: return player_state[pos[0]][pos[1]]
        #端にいる時点で囲えない
        if pos[0] < 1 or pos[0] > field.width-2 or pos[1] < 1 or pos[1] > field.height-2:
            return 0

        x = pos[0]
        y = pos[1]
        another_team = -team  #teamの敵チーム
        another_num = [another_team, another_team//3, another_team//3*2]    #敵チームを表すstate上の数字

        player_state[x][y] = 1

        #上下左右が囲まれたマスか確認
        if field.state[x-1][y] == 0 or field.state[x-1][y] in another_num:  #空 or 敵チームのタイル
            val = self.inclose_check(self.state, player_state, team, [x-1, y])
            if val == 0: return 0, None
        if field.state[x-1][y] == 0 or field.state[x+1][y] in another_num:  #空 or 敵チームのタイル
            val = self.inclose_check(self.state, player_state, team, [x+1, y])
            if val == 0: return 0, None
        if field.state[x-1][y] == 0 or field.state[x][y-1] in another_num:  #空 or 敵チームのタイル
            val = self.inclose_check(self.state, player_state, team, [x, y-1])
            if val == 0: return 0, None
        if field.state[x-1][y] == 0 or field.state[x][y+1] in another_num:  #空 or 敵チームのタイル
            val = self.inclose_check(self.state, player_state, team, [x, y+1])
            if val == 0: return 0, None

        if DEBUG is True:   #デバッグ時のみ表示
            print(player_state)

        return 1, player_state  #囲まれていた場合は、使い回せるようにそのときのフィールドの状態も返す

    def state_check(self, state):   #タイルが置いてある場所と囲まれている場所を表す
        #状態を表すための配列
        own_state = np.zeros([self.width, self.height], dtype=int)  #自チーム
        opponent_state = np.zeros([self.width, self.height], dtype=int) #敵チーム

        #囲まれているか確認するための配列
        own_state_copy = copy.deepcopy(own_state)
        opponent_state_copy = copy.deepcopy(opponent_state)

        #タイルが置かれてたら 1
        #囲まれていたら 2
        #得点に関係なければ 0

        team = OWN

        for i in range(0, self.width):
            for j in range(0, self.height):
                if opponent_state[i][j] != 0:   continue    #すでに判定済み
                
                if self.state[i][j] > 0: own_state[i][j] = 1    #自チームのタイルが置かれている
                elif self.state[i][j] == EMPTY:   #囲まれているか判定
                    num, own_state_copy = self.inclose_check(self.state, own_state_copy, team, [i, j])

                    inclose_index = np.where(own_state_copy == 1)   #囲まれているフラグの立つ配列の要素を取得
                    

    def judge(self, state):
        own_tile, own_territory = 0, 0
        opponent_tile, opponent_territory = 0, 0

        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.state[i][j] > 0: own_tile += self.value[i][j]    #OWN_1とかが1以上だから
                if self.state[i][j] < 0: opponent_tile += self.value[i][j]   #OPPONEN_1とかが-1以下だから
                if self.state[i][j] == EMPTY:   #囲まれているか判定
                    pass
            
        if own_tile + own_territory > opponent_tile + opponent_territory:
            return OWN
        else:
            return OPPONENT


'''
# for check
field = field()
field.create_rand_field()
field.print_field()
'''
'''
# for check
field = field()
field.create_from_file("shape_info.txt")
field.print_field()
'''