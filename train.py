# coding: utf-8

import os
import glob
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.utils.data
import network
import train_data_creator
import game
import evaluate

GAMMA = 0.97    #割引率
BATCH_SIZE = 32 #一度に学習する局面数
EPOCH = 3 #1つの訓練データを何回学習させるか
TURN = 32

MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/model.pth")       #モデルの保存パス
BEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/best_model.pth")       #最善モデルの保存パス
OPTIMIZER_PATH = os.path.join(os.path.dirname(__file__), "./output/optimizer.pth")       #オプティマイザの保存パス
RECORD_LIST_PATH = os.path.join(os.path.dirname(__file__), "./recordlist_train")         #対局データ一覧表（学習用）の保存パス
TEST_RECORD_LIST_PATH = os.path.join(os.path.dirname(__file__), "./recordlist_test") #対局データ一覧表（テスト用）の保存パス

#モデルが保存されていれば読み込み、なければ新規作成
if os.path.exists(MODEL_PATH):
    fine_tune = True
    model = network.Network()
    model.load_state_dict(torch.load(MODEL_PATH))
else:
    fine_tune = False
    model = network.Network()

#オプティマイザが保存されていれば読み込み、なければ新規作成
if os.path.exists(OPTIMIZER_PATH):
    fine_tune = True
    optimizer = optim.Adam(model.parameters(), lr=0.1)
    optimizer.load_state_dict(torch.load(OPTIMIZER_PATH))
else:
    fine_tune = False
    optimizer = optim.Adam(model.parameters(), lr=0.1)

criterion = nn.MSELoss()   #推論値と理論値の差を計算

max_win_ratio = -1.0    #勝率の最高値

for epoch in range(1, EPOCH+1):   #エポックを回す
    print("epoch:", epoch)          #現在のエポック数（何回目のループか）

    record_index = 0

    while True: #全学習データを扱う
        print("epoch:{0} record:{1}".format(epoch, record_index))

        # 一括でデータセットを作った場合
        # x_batch = x_train[j : j+BATCH_SIZE] #訓練データをバッチサイズ分取り出し
        # y_batch = y_train[j : j+BATCH_SIZE] #教師データをバッチサイズ分取り出し

        #バッチサイズ分の訓練データ（陣形とタイルの点数）と正解ラベルを取得
        #datasetは、[value, state, player, won] それぞれの要素は、バッチサイズ分の対局の全局面でシャッフルなし
        dataset = train_data_creator.get_dataset(RECORD_LIST_PATH, BATCH_SIZE, record_index)
        if dataset is None: #学習データがなくなった
            break

        # train_np = np.r_[dataset[0], dataset[1], dataset[2]]    #入力データを結合し、一つの配列にする
        target_np = np.copy(dataset[3])

        # #データ型をndarrayからtorchに変更 float,longにしているのは決まりだから
        # train_torch = torch.from_numpy(train_np).float()
        # target_torch = torch.from_numpy(target_np).long()

        dataset[1] = dataset[1].reshape(len(dataset[1]), 1, game.MAX_BOARD_SIZE, game.MAX_BOARD_SIZE)
        dataset[3] = dataset[3].reshape(len(dataset[3]), 1, 1, 1)

        train = torch.utils.data.TensorDataset(torch.from_numpy(dataset[1]).float(), torch.from_numpy(dataset[3]).float())
        train_loader = torch.utils.data.DataLoader(train, batch_size=BATCH_SIZE, shuffle=True)

        total_loss = 0
        for i, data in enumerate(train_loader):
            x, t = data
            x, t = torch.autograd.Variable(x), torch.autograd.Variable(t)
            optimizer.zero_grad()
            y = model(x)
            t = t.reshape((32, 1))  #入力にラベルのデータの大きさを合わせる

            # print(x.shape)
            # print(y.shape)
            # print(t.shape)

            loss = criterion(y, t)
            total_loss += loss.item()
            loss.backward()
            optimizer.step()

            # if i % 1000 == 999:    #ミニバッチ1000個ごとにロスの表示
            #     print('[%d, %5d] loss: %.3f' %
            #         (epoch + 1, i + 1, total_loss / 1000))
            #     total_loss = 0.0
            
            # print("x:{0} t:{1} y:{2} loss:{3}".format(x, t, y, loss))
            print(loss)

            torch.save(model.state_dict(), MODEL_PATH)  #モデルの保存
            if i%50 == 0:   #ミニバッチ50個ごとにモデルが最善か確認
                ratio = evaluate.evaluate_model(model, 10)  #勝率
                print("win ratio:{}".format(ratio))
                if max_win_ratio <= ratio:  #勝率が今までの最高値より高い
                    print("max update:{0} >= {1}".format(ratio, max_win_ratio))
                    max_win_ratio = ratio
                    torch.save(model.state_dict(), BEST_MODEL_PATH)  #ベストモデルの保存
                else:
                    print("{0} <= {1}".format(ratio, max_win_ratio))

        record_index += BATCH_SIZE

    torch.save(optimizer.state_dict(), OPTIMIZER_PATH)  #オプティマイザの保存

print("Finished Training")