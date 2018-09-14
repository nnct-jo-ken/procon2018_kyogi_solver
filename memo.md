# procon29競技プログラム方針

## 方針
- pytorchで実装
- 対局データはMiniMaxでC++かPythonで大量に生成（numpy形式で保存）
- Neural Fitted Q Iteration（バッチ強化学習）

- rs値は、勝ちか負けか
- それぞれのプレイヤーにとって得点が最大になるように考えて、同じチームだったら得点を合算する
- ↑の案却下
	- 自分と敵が、同時に2箇所を動かす、または、2回ずつプレーできる（2度指し）と考えた方がいいかも
- 割引率っていらないかも
	- とりあえず割引率を定数とかで定義ておく　必要なければ、1.0をセットする

- 得点計算
	1. Winding Number Algorithm
	1. 一方向に自チームのタイルがあるか確認
	1. 外側にあるタイルから、一周するまで順に辿ってみる
		* スタックに突っ込んで、行き止まりなら分岐点まで戻る
		* 分岐点では、できるだけ外側を選ぶ

## ファイル構造
* `record`  
	教師データの作成はC++でやってみる
	- `***.npz`
	- `***.npz`
* `policy`  
	方策ネットワーク
	- `data_creator_policy.py`
	- `network_policy.py`
	- `train_policy.py`
	- `model_policy.npz`
	- `optimizer_policy.npz`
* `value`  
	価値ネットワーク
	- `data_creator_value.py`
	- `networl_value.py`
	- `train_value.py`
	- `model_value.npz`
	- `optimizer_value.npz`
* `player.py`  
	ランダム  
	モンテカルロ木探索  
		引数でプレイアウト数を設定  
	DQN  
	MiniMaxDQN  
* `evaluate.py`  
	勝率を出す
	引数で味方と敵プレーヤと対戦回数を指定
* `main.py`  
	入力：盤面（とりあえずファイルで）
	出力：次の手
