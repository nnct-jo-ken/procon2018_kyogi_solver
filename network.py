# coding: utf-8

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import game

ch = 192    #中間層のフィルター枚数

class Network(nn.Module):

    def __init__(self):
        #ニューラルネットワークを作成 <= 畳み込み(Conv2d)を使った方がいい（画像の特徴を抽出できる）と思うけれど、後回し
        super(Network, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=ch, kernel_size=(4, 4), stride=1, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=[2, 2], stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=ch, out_channels=ch, kernel_size=(4, 4), stride=1, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=[2, 2], stride=1, padding=1)
        self.conv3 = nn.Conv2d(in_channels=ch, out_channels=ch, kernel_size=(4, 4), stride=1, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=[2, 2], stride=1, padding=1)
        self.fc1 = nn.Linear(ch * 12 * 12 * 2, 100)
        self.fc2 = nn.Linear(100, 100)
        self.fc3 = nn.Linear(100, 1)     #出力は、勝ち負けの値1コ

        # self.fc1 = nn.Linear(1, 10)   #入力はプレイヤーが1次元データだから、1 ニューロンは10
        # self.fc2 = nn.Linear(10, 10)
        # self.fc3 = nn.Linear(10, 1)     #出力は勝ち負けを表す値1コ

    def forward(self, x, y):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))

        y = self.pool1(F.relu(self.conv1(y)))
        y = self.pool2(F.relu(self.conv2(y)))
        y = self.pool3(F.relu(self.conv3(y)))

        x = x.view(-1, ch * 12 * 12)
        y = y.view(-1, ch * 12 * 12)  
        merge_layer = torch.cat([x, y], dim=1)  #水平方向にくっつけている

        out = F.relu(self.fc1(merge_layer))
        out = F.relu(self.fc2(out))
        out = self.fc3(out)
        return out

        # h1 = F.relu(self.fc1(x)) #中間層の活性化関数はReLU
        # h2 = F.relu(self.fc2(h1))
        # h3 = self.fc3(h2)
        # return h3
        #return F.log_softmax(x) #出力層の活性化関数はソフトマックス(softmax)