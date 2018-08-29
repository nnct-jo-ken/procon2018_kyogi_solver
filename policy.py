import random
import glob
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import train_data_creator

GAMMA = 0.97    #割引率
BATCH_SIZE = 32 #一度に処理する局面数
EPOCH = 100 #学習のループを回す回数

MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/model.pth")       #モデルの保存パス
OPTIMIZER_PATH = os.path.join(os.path.dirname(__file__), "./output/optimizer.pth")       #オプティマイザの保存パス
RECORD_PATH = os.path.join(os.path.dirname(__file__), "./record/*.npz")         #対局データ一覧表（学習用）の保存パス
TEST_RECORD_PATH = os.path.join(os.path.dirname(__file__), "./test_record.npz") #対局データ一覧表（テスト用）の保存パス


class PolicyNetwork(nn.Module):

    def __init__(self):
        #ニューラルネットワークを作成 <= 畳み込み(Conv2d)を使った方がいい（画像の特徴を抽出できる）と思うけれど、後回し
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Liner(144, 100)   #入力は最大フィールドサイズに合わせて144(12*12) ニューロンは100
        self.fc2 = nn.Liner(100, 100)
        self.fc3 = nn.Liner(100, 9)     #出力は8方向＋パスで9

    def fowward(self, x):
        x = F.relu(self.fc1(x)) #中間層の活性化関数はReLU
        x = F.relu(self.fc2(x))
        return F.log_softmax(x) #出力層の活性化関数はソフトマックス(softmax)


#モデルが保存されていれば読み込み、なければ新規作成
if os.path.exists(MODEL_PATH):
    fine_tune = True
    model = PolicyNetwork()
    model.load_state_dict(torch.load(MODEL_PATH))
else:
    fine_tune = False
    model = PolicyNetwork()

#オプティマイザが保存されていれば読み込み、なければ新規作成
if os.path.exists(MODEL_PATH):
    fine_tune = True
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    optimizer.load_state_dict(torch.load(OPTIMIZER_PATH))
else:
    fine_tune = False
    optimizer = optim.Adam(model.parameters(), lr=0.1)

# 学習データの数だけ繰り返す
#   ミニバッチするために、複数の学習データ(10とか20とか...)を取り出す
#   教師信号（）、入力（状態・行動）を作成
#   ミニバッチデータを今のニューラルネットワークに突っ込んで得たQ値と教師データの誤差を得る
#   誤差を勾配法で最小化
#   なんとかして、学習を収束させるor一定の条件を満たす できたら、その時点のQ値を返す
# 結果、Q値が返った

# 対局データの数を取得

creator = train_data_creator.TrainDataCreator(model, GAMMA)

for i in range(1, EPOCH):
    print("epoch:", i)          #現在のエポック数（何回目のループか）
    records = glob.glob(RECORD_PATH)    #対局データのファイル名一覧
    print("{} records".format(len(records)))
    np.random.shuffle(records)  #時間の相関をなくす

    record_index = 0
    for j in range(1, 100000):  #どんな数字にしたらいいか後で調べる
        print("{0}-{1}: record_index:{2}/{3}".format(i, j, record_index, len(records)))
        end_index, data = creator.create_train_data(records, record_index)
        if end_index > len(records):    #インデックスがレコードを超えている
            print("index exceeds records len")
            break
        if data is None:    #データが空
            print("data is none")
            break
        X_color, X_action, y_target = data  #dataからそれぞれの要素に分離 __create_train_data()を参照
        print("train: {0} samples, {1} files".format(len(X_color), end_index-record_index)) #