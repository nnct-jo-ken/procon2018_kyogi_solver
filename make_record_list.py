#対局データから、訓練用とテスト用に分ける
import argparse
import os
import random

#引数の設定
parser = argparse.ArgumentParser()
parser.add_argument('dir', type=str, default="./record", help='Directory where records are saved')  #対局データが保存されているフォルダ
parser.add_argument('--ratio', type=float, default=0.9, help="Proportion of records for train")  #訓練用データの割合
args = parser.parse_args()

record_list = []    #対局データファイル一覧
for root, dirs, files in os.walk(args.dir): #root:ディレクトリ名 dirs:内包するディレクトリ一覧 files:内包するファイル一覧
    for file in files:  #対局データファイルをrecord_listに順番に追加
        record_list.append(os.path.join(root, file))

#対局データファイルリストをシャッフル
random.shuffle(record_list)

#訓練データとテストデータに分けて、それぞれの一覧表ファイルにパスを書き出し
train_len = int(len(record_list) * args.ratio)  #訓練データの数を計算
with open('recordlist_train', 'w') as f:
    for i in range(train_len):    #最初から訓練データの数だけ繰り返す
        f.write(record_list[i])
        f.write('\n')

with open('recordlist_test', 'w') as f:
    for i in range(train_len, len(record_list)):    #残りのデータはテスト用
        f.write(record_list[i])
        f.write('\n')

print('total record num = {}'.format(len(record_list)))
print('train record num = {}'.format(train_len))
print('tsst record num  = {}'.format(len(record_list) - train_len))