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
    def clear(self):    #フィールド情報をクリア
        self.width = 0   #縦
        self.height = 0  #横
        self.own_a1, self.own_a2, self.opponent_a1, self.opponent_a2 = {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}   #エージェントの位置
        self.value = np.zeros([self.width, self.height], dtype=int)    #タイルの得点
        self.own_state = np.zeros([self.width, self.height], dtype=int)    #味方の陣形
        self.opponent_state = np.zeros([self.width, self.height], dtype=int)    #敵の陣形
        self.own_status = [] #味方のターンごとの陣形を管理
        self.opponent_status = [] #敵のターンごとの陣形を管理
        self.a1_poss = []   #エージェント1の座標を管理
        self.a2_poss = []   #エージェント2の座標を管理

    def create_rand_field(self):    #フィールドを生成し、タイルに適当な点数を割り振る
        sum_tile = random.randint(80, 144)  #タイルの数
        self.width = random.randint(7, 12)  #縦の大きさをランダムに決定 80//12=7より、7が一辺の最小サイズ
        while sum_tile // self.width > 12:  #heightが13以上だとルールに反しているから、12以下になるまで乱数生成
            self.width = random.randint(7, 12)
        self.height = sum_tile // self.width    #横の大きさをランダムに決定 上のループで、ルールに適合するはず
        self.value = np.resize(self.value, (self.width, self.height))
        self.own_state = np.resize(self.own_state, (self.width, self.height))
        self.opponent_state = np.resize(self.opponent_state, (self.width, self.height))
        self.own_a1['x'] = random.randint(0, self.width//2) #エージェントの位置をランダムに決定
        self.own_a1['y'] = random.randint(0, self.height//2)
        self.opponent_a1['x'] = random.randint(0, self.width//2)
        self.opponent_a1['y'] = random.randint(0, self.height//2)

        bunkatsu = random.randint(0, 2) #0:水平垂直 1:水平 2:垂直

        #エージェントの位置を線対称にする
        if bunkatsu == 0 or bunkatsu == 1:  #水平に線対称
            self.own_a2['x'] = self.width - self.own_a1['x'] - 1
            self.opponent_a2['x'] = self.width - self.opponent_a1['x'] - 1
        if bunkatsu == 0 or bunkatsu == 2:  #垂直に線対称
            self.own_a2['y'] = self.height - self.own_a1['y'] - 1
            self.opponent_a2['y'] = self.height - self.opponent_a1['y'] - 1

        #エージェントの位置をstateに反映
        self.own_state[self.own_a1['x']][self.own_a1['y']] = OWN_1
        self.own_state[self.own_a2['x']][self.own_a2['y']] = OWN_2
        self.opponent_state[self.opponent_a1['x']][self.opponent_a1['y']] = OPPONENT_1
        self.opponent_state[self.opponent_a2['x']][self.opponent_a2['y']] = OPPONENT_2

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
        self.own_state = np.resize(self.own_state, (self.width, self.height))
        self.opponent_state = np.resize(self.opponent_state, (self.width, self.height))
        self.own_state[self.own_a1['x']][self.own_a1['y']] = OWN_1
        self.own_state[self.own_a2['x']][self.own_a2['y']] = OWN_2

    def create_from_gui(self, value_nums, state_nums):
        self.clear()    #データをリセット

        self.width = int(value_nums[0][0].decode('ascii'))
        self.height = int(value_nums[0][1].decode('ascii'))

        self.value = np.resize(self.value, (self.width, self.height))
        self.own_state = np.resize(self.own_state, (self.width, self.height))
        self.opponent_state = np.resize(self.opponent_state, (self.width, self.height))

        for i in range(1, self.width+1):  #最初はフィールドサイズが入っているから、とばす
            for j in range(0, self.height):
                self.value[i-1][j] = int(value_nums[i][j].decode('ascii'))
                # self.state[i-1][j] = int(state_nums[i][j].decode('ascii'))
                if int(state_nums[i][j].decode('ascii')) == 1:
                    self.own_state[i-1][j] = OWN
                elif int(state_nums[i][j].decode('ascii')) == 2:
                    self.opponent_state[i-1][j] = OPPONENT

        #GUIとsolverで座標軸の扱い方が逆
        self.own_a1['x'] = int(value_nums[self.width+1][1].decode('ascii'))
        self.own_a1['y'] = int(value_nums[self.width+1][0].decode('ascii'))
        self.own_a2['x'] = int(value_nums[self.width+2][1].decode('ascii'))
        self.own_a2['y'] = int(value_nums[self.width+2][0].decode('ascii'))
        self.opponent_a1['x'] = int(value_nums[self.width+3][1].decode('ascii'))
        self.opponent_a1['y'] = int(value_nums[self.width+3][0].decode('ascii'))
        self.opponent_a2['x'] = int(value_nums[self.width+4][1].decode('ascii'))
        self.opponent_a2['y'] = int(value_nums[self.width+4][0].decode('ascii'))

    def print_field(self):
        print(" width:{0}\n height:{1}\n own_a1:{2}\n own_a2:{3}\n opponent_a1:{4}\n opponent_a2:{5}" \
            .format(self.width, self.height, self.own_a1, self.own_a2, self.opponent_a1, self.opponent_a2))
        print("value\n{0}".format(self.value))
        print("own state\n{0}".format(self.own_state))
        print("opponent state\n{0}".format(self.opponent_state))

    def can_move_pos(self, pos):    #その座標は操作可能か（範囲内か） posはリスト [x, y]
        if pos[0] < 0 or pos[0] >= self.width or pos[1] < 0 or pos[1] >= self.height:   #範囲外
            return False
        else:
            return True

    def player_exist(self, state, pos): #その座標にプレーヤがいるか posはリスト [x, y]
        x = pos[0]
        y = pos[1]

        if (x == self.own_a1['x'] and y == self.own_a1['y']) \
            or (x == self.own_a2['x'] and y == self.own_a2['y']) \
            or (x == self.opponent_a1['x'] and y == self.opponent_a1['y']) \
            or (x == self.opponent_a2['x'] and y == self.opponent_a2['y']):
            return True
        else:
            return False

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

    def hands(self, state, player):  #可能な手を一覧 移動可能な位置と、タイルをひっくり返す
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
                elif state[x + i][y + j] == EMPTY:  #どちらの陣でもない
                    hands.append([{'x':x+i, 'y':y+j}, False])    #移動
                else:   #どちらかの陣地
                    if i == 0 and j == 0:   #自分のいる場所
                        hands.append([{'x':x+i, 'y':y+j} , False]) #移動
                    else:   #隣り合った場所
                        if self.player_exist(state, [x + i, y + j]) is True:  #他のプレーヤーがいる
                            continue
                        else:   #プレーヤーがいない
                            hands.append([{'x':x+i, 'y':y+j} , False]) #移動
                            hands.append([{'x':x+i, 'y':y+j} , True]) #ひっくり返す
        
        if DEBUG is True:
            print("player:{0} hands:{1}".format(player, hands))

        return hands

    def conv_turn_pos(self, turn):  #ターン（エージェント）が入力されると、座標が辞書で返る
        if   turn == OWN_1: return self.own_a1
        elif turn == OWN_2: return self.own_a2
        elif turn == OPPONENT_1: return self.opponent_a1
        elif turn == OPPONENT_2: return self.opponent_a2

    def move(self, state, player, hand):   #handはリスト hand[0]は辞書
        if self.can_move_pos([hand[0]['x'], hand[0]['y']]) is False: #範囲内か確認
            raise Exception("Can't move!")
        if hand[1] is False:    #移動なら
            #移動元はチームの値を置く　始
            if player > 0:  #OWN
                state[self.conv_turn_pos(player)['x']][self.conv_turn_pos(player)['y']] = OWN
            elif player < 0:    #OPPONENT
                state[self.conv_turn_pos(player)['x']][self.conv_turn_pos(player)['y']] = OPPONENT
            #移動元はチームの値を置く　終
            state[hand[0]['x']][hand[0]['y']] = player  #移動先にタイルを置く
            self.conv_turn_pos(player)['x'] = hand[0]['x']  #エージェントの移動
            self.conv_turn_pos(player)['y'] = hand[0]['y']
        else:
            state[hand[0]['x']][hand[0]['y']] = EMPTY   #タイルを除去

        return state

    def area_score(self, state, team):
        score = 0   #領域ポイント
        # height個の要素のリストがwidth個入ったリストができる
        is_searched = [[False for i in range(self.height)] for j in range(self.width)]  #探索済みか
        is_end = [[False for i in range(self.height)] for j in range(self.width)]   #端か

        my_team = [team, team//3, team//3*2]    #自チームを表すstate上の数字

        #端の部分はTrueを代入
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or y == 0 or x == self.width-1 or y == self.height-1:
                    is_end[x][y] = True

        for x in range(self.width):
            for y in range(self.height):
                if state[x][y] not in my_team:    #自チームではない
                    if is_searched[x][y] is False:  #未探索
                        _reach_end = False  #まだ探索が終了していない
                        sscore = 0
                        sscore, _reach_end = self.count_area_score(state, [x, y], is_searched, is_end, _reach_end, sscore, my_team)
                        if _reach_end is False:
                            score += sscore

        return score

    def count_area_score(self, state, pos, is_searched, is_end, _reach_end, sscore, teams): #posは[x, y] teamsはリスト[team, team_a1, team_a2]
        x = pos[0]
        y = pos[1]

        if state[x][y] in teams or is_searched[x][y] == True: #自陣 or すでに探索済み
            return sscore, _reach_end
        is_searched[x][y] = True    #探索済みにする
        sscore += abs(self.value[x][y])   #タイルポイントの絶対値を代入
        if is_end[x][y] is True:    #端まで達したら、探索終了
            _reach_end = True

        if x > 0:
            s, r = self.count_area_score(state, [x-1,y], is_searched, is_end, _reach_end, sscore, teams)
            sscore = s
            _reach_end = r
        if x < self.width-1:
            s,r = self.count_area_score(state, [x+1,y], is_searched, is_end, _reach_end, sscore, teams)
            sscore = s
            _reach_end = r
        if y > 0:
            s, r = self.count_area_score(state, [x,y-1], is_searched, is_end, _reach_end, sscore, teams)
            sscore = s
            _reach_end = r
        if y < self.height-1:
            s, r = self.count_area_score(state, [x,y+1], is_searched, is_end, _reach_end, sscore, teams)
            sscore = s
            _reach_end = r

        return sscore, _reach_end

    def judge(self, own_state, opponent_state):
        own_tile, own_territory = 0, 0
        opponent_tile, opponent_territory = 0, 0

        for i in range(0, self.width):
            for j in range(0, self.height):
                if own_state[i][j] != 0: own_tile += self.value[i][j]    #OWN_1とかが1以上だから
                if opponent_state[i][j] != 0: opponent_tile += self.value[i][j]   #OPPONEN_1とかが-1以下だから

        own_territory = self.area_score(own_state, OWN)
        opponent_territory = self.area_score(opponent_state, OPPONENT)

        if own_tile + own_territory > opponent_tile + opponent_territory:
            return OWN
        else:
            return OPPONENT

    def check_team(self, player):   #エージェントが属すチームを返す
        if player > 0:
            return OWN
        if player < 0:
            return OPPONENT

    def agent_field(self, pos): #エージェントの位置を盤面で表す pos リスト[x,y]
        x = pos[0]
        y = pos[1]

        pos_field = np.zeros([self.width, self.height], dtype=int)  #全部0の盤面
        pos_field[x][y] = 1

        return pos_field

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