import torch
import torch.nn as nn
import torch.nn.functional as F

ch = 100    #中間層のフィルターサイズ
class PolicyNetwork(nn.Module):
    def __init__(self):
        super(PolicyNetwork, self).__init__()
        with self.init_scope():
            self.conv1 = nn.Conv2d(144, ch, kernelsize=3)    #入力は最大フィールドサイズに合わせて144(12*12)
            self.conv2 = nn.Conv2d(ch, 9, kernel_size=3)      ##出力は8方向＋パスで9

    def __call__(self, x):
        x = F.relu(self.conv1(x)) #中間層の活性化関数はReLU
        x = F.relu(self.conv2(x))
        return F.softmax(x) #出力層の活性化関数はソフトマックス(softmax)

    #xを入力した際のネットワーク出力（ネットワークのQ値）を返す
    def predict(self, x):   #x:入力
        h1 = F.leaky_relu(self.l1(x))
        h2 = F.leaky_relu(self.l2(h1))
        h3 = F.leaky_relu(self.l2(h2))
        h4 = F.leaky_relu(self.l2(h3))
        y = F.leaky_relu(self.l5(h4))
        return y