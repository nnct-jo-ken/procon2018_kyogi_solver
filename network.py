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
        self.conv1 = nn.Conv2d(in_channels=4, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1)

        self.fc1 = nn.Linear(in_features=64, out_features=128)
        self.fc2 = nn.Linear(in_features=128, out_features=128)
        self.fc3 = nn.Linear(in_features=128, out_features=128)
        self.fc4 = nn.Linear(in_features=128, out_features=9)   #出力：8方向＋停留

    def forward(self, x):   #xは4チャンネルを含む（タイルの点数、自陣・敵陣の陣形、エージェントの位置）
        out = F.relu(self.conv1(x))
        out = F.relu(self.conv2(out))
        out = F.relu(self.conv3(out))
        out = F.relu(self.conv4(out))
        out = F.max_pool2d(out, kernel_size=x.shape[2:])

        b,c,h,w = out.shape #batch channnel height width
        out = F.relu(self.fc1(out.reshape(b,-1)))
        out = F.relu(self.fc2(out))
        out = F.relu(self.fc3(out))
        out = F.relu(self.fc4(out))
        return F.softmax(out)