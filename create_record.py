import os, time
import numpy as np
import game
import player

CREATE_RECORD_NUM = 10000   #対局データを作る数
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "record")  #対局データの出力ディレクトリ

players = {
    game.OPPONENT: player.RandomUniform(),
    game.ONESELF: player.RandomUniform()
}

def save_record(boards, players, won, move_label, width, height):
    X_board = np.array(boards)
    X_board = np.reshape(X_board, [-1, width, height])
    X_player = np.array(players)
    X_player = np.reshape(X_player, [-1, 1])
    X_move = np.array(move_label)
    X_move = np.reshape(X_move, [-1, 1])

    now = int(round(time.time()*1000))
    path = os.path.join(OUTPUT_DIR, "{0}.npz".format(now))  #現在の時刻を元に、適当なファイル名をつける

    np.savez(path,
            X_board=X_board,
            X_player=X_board,
            X_move=X_move,
            y_won=won,
            width=width,
            height=height)

    try:    #numpy配列で読み込んで、例外が発生したらそのファイルは消す
        np.load(path)
    except:
        os.remove(path)

    
for i in range(1, CREATE_RECORD_NUM):
    print("game:", i, end='\r')

    board = game.create_field()

    boards = []
    players = []

    turn = game.OWN #ターンを設定
    while game.can_put(board):  #置ける手がある
        hand = players[turn].select(board, turn)
        if hand is not None:
            boards.append(board)
            players.append(turn)

            board = game.move(board, turn, hand)

        turn = -turn    #ターンの交代

    won = game.judge(board)
    boards.append(board)

    save_record(boards, players, won)
