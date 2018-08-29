import numpy as np

class TrainDataCreator:

    def __init__(self, model, gamma):
        self.model = model
        self.gamma = gamma

    def get_partial(self, record):  #予測を取得　<= 後でやる curve()が何をやりたいのかも確認
        try:    #対局データを読み込んでみる　データがなかったら事故るので、tryブロック内にする
            npz = np.load(record)
        except: #事故ったときは、空（ゼロ）の配列？リスト？を返す
            #hogehoge
        
    def multiple(self, board):
        b_t = np.transpose(board)   #転置（軸が逆になる TA[x,y] = A[y,x]）
        b_r = np.rot90(board, 2)    #180度回転
        b_rt = np.rot90(b_t, 2)     #転置＋180度回転
        
        boards = np.array([board], [b_t], [b_r], [b_rt])    #オリジナル＋上記3種類のボードの詰め合わせ
        return boards
    
    def create_train_data(self, records, start):
        record_colors = []
        record_actions = []
        record_rs = np.zeros([0,1]) #rsは最適な戦略のことみたい
        for record_index in range(start, len(records)):
            record = records[record_index]  #処理対象の1つのファイルを取り出し
            colors, actions, rs = self.get_partial(record)  #色、行動、戦略を取り出している
            record_colors.append(colors)    #record_colors配列の末尾にcolorsを追加
            record_actions.append(actions)
            record_rs = np.append(record_rs, rs)    #record_rs配列をコピーして末尾にrsを追加したものを代入
            if len(record_rs) > 8192:   #4回ごとに予測が行われるそうな
                break   #この時点でのrecord_indexが、処理したファイルの数（最後のインデックス）
        else:
            #対局データの最後に達した(きっちりと固定長のファイル数を処理していないけれど、処理していないファイルがなくなった)
            return record_index+1, None
        record_colors = np.concatenate(record_colors).reshape([-1, 1])  #なんか知らんけれど配列を結合し、2次元にしているみたい？-1は、適切な値に変換してくれる
        record_actions = np.concatenate(record_actions).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])
        return record_index+1, self.__create_train_data(record_colors, record_actions, record_rs)

    def __create_train_data(self, colors, actions, rs): #外部から参照されない
        # for train
        X_color = []
        X_action = []
        # for calculate Rs
        pred_color = []
        pred_action = []
        num_action_primes = []
        turn_change = []

        for c, a, in zip(colors, actions):  #2つの値が同時に次の状態に更新される
            X_color.append([c]*4)
            X_action.append(self.multiple(a))   #予測値を配列（もしかしたらリスト？）に入れている

            next_c = -c if reversi.can_put(a, -c) else c    #もし-cの立場で置けるなら、次は-cが打つ　そうでなければcが打つ
            hands = reversi.hands(a, next_c)    #打てる手
            num_action_primes.append(len(hands)*4)
            turn_change.append(c*next_c)
            for hand in hands:  #各手ごとに
                action_prime = reversi.put(a, next_c, hand) #打った状態の盤面を代入
                pred_color.append([next_c]*4)   #
                pred_action.append(self.multiple(action_prime)) #盤面を計4種類にしてpred_actionの末尾に追加

            # predict
            pred_color = np.array(pred_color).reshape([-1, 1])  #pred_colorを2次元へ -1の部分は適切な大きさに自動で変換してくれる
            pred_action = np.array(pred_action).reshape([-1, reversi.BOARD_SIZE, reversi.BOARD_SIZE])   #

            preds = self.model.predict([pred_color, pred_action],   #karasのメソッド　入力サンプルに対する予想の出力を生成　バッチ処理で行われる
                                   verbose=1,
                                   batch_size=1024)

            # calculate targets
            targets = np.hstack([rs.reshape([-1, 1])]*4).astype(float) # [-1, 4] 水平方向に連結
            start = 0
            for i in range(len(num_action_primes)):
                num = num_action_primes[i]
                if num > 0:
                    r_max = np.max(preds[start:start+num])
                    targets[i] += self.gamma * r_max * turn_change[i]
                    start += num