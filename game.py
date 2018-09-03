import numpy as np
import random

def create_field(width, height): #空のフィールド生成
    field = []  #フィールド全体の情報
    states = [] #ターンごとの陣形を管理

    width = width   #縦
    height = height #横
    own_a1, own_a2, opponent_a1, opponent_a2 = {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}, {'x':0, 'y':0}   #エージェントの位置
    value = np.zeros([width, height], dtype=int)    #タイルの得点
    state = np.zeros([width, height], dtype=int)    #陣形

    field.append((width, height, own_a1, own_a2, opponent_a1, opponent_a2, value, state))
    return field

    '''
	int turn;	//ターン数
	int width;	//縦の大きさ
	int height;	//横の大きさ
	struct agent {
		int x;	//横方向の位置
		int y;	//縦方向の位置
	}own_a1, own_a2, enemy_a1, enemy_a2;
	std::vector<std::vector<int>> value;	//点数
	std::vector<std::vector<int>> state;	//0:どちらでもない 1:自陣 2:敵陣
    '''

def create_rand_field(width, height):   #フィールドを生成して、得点は適当に対称になるように設定
    field = create_field(width, height) #空のフィールド
    middle = random.randint(0,2)    #どこで対称にするか  0:水平垂直 1:水平 2:垂直

    for i in range(0, width):
        for j in range(0, height):
            tmp = random.randint(-16, 16*9) #タイルのプラスの得点を多くするため
            if tmp > 0: #正の値だったら、範囲に収まるようにする
                tmp //= 9
            
        field[0]


def print_board(board): #フィールド表示

def is_in_board(position):  #座標がフィールド内か判定

def can_move(board, player=None, position=None):  #移動できるか

def move(board, player, position):  #移動

def judge(board):   #どちらが勝っているか

def hands(board, player):   #移動できる場所
