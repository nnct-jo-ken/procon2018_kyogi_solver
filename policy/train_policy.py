import random
import glob
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import network_policy
import data_creator_policy
import read_records

GAMMA = 0.97    #割引率
BATCH_SIZE = 32 #一度に処理する局面数
EPOCH = 100 #学習のループを回す回数

MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/model.pth")       #モデルの保存パス
OPTIMIZER_PATH = os.path.join(os.path.dirname(__file__), "./output/optimizer.pth")       #オプティマイザの保存パス
RECORD_PATH = os.path.join(os.path.dirname(__file__), "./record/*.npz")         #対局データ一覧表（学習用）の保存パス
TEST_RECORD_PATH = os.path.join(os.path.dirname(__file__), "./test_record.npz") #対局データ一覧表（テスト用）の保存パス

#モデルが保存されていれば読み込み、なければ新規作成
if os.path.exists(MODEL_PATH):
    fine_tune = True
    model = network_policy.PolicyNetwork()
    model.load_state_dict(torch.load(MODEL_PATH))
else:
    fine_tune = False
    model = network_policy.PolicyNetwork()
 #オプティマイザが保存されていれば読み込み、なければ新規作成
if os.path.exists(MODEL_PATH):
    fine_tune = True
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    optimizer.load_state_dict(torch.load(OPTIMIZER_PATH))
else:
    fine_tune = False
    optimizer = optim.Adam(model.parameters(), lr=0.1)

creator = data_creator_policy.PolicyDataCreator(model, GAMMA)   #

for i in range(1, EPOCH):   #エポックごとに
    print("epoch:", i)
    records = read_records(RECORD_PATH) #学習用対局データ一覧を取得
    print("{0} reords".format(len(records)))    #学習データの数
    np.random.shuffle(records)  #ランダムに並び替え

    record_index = 0
    