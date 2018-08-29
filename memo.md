# procon29競技プログラム方針

## 方針
- pytorchで実装
- 対局データはMiniMaxでC++かPythonで大量に生成（numpy形式で保存）
- Neural Fitted Q Iteration（バッチ強化学習）


## ファイル構造
* record
	教師データの作成はC++でやってみる
	- ***.npz
	- ***.npz
* policy
	方策ネットワーク
	- data_creator_policy.py
	- network_policy.py
	- train_policy.py
	- model_policy.npz
	- optimizer_policy.npz
* value
	価値ネットワーク
	- data_creator_value.py
	- networl_value.py
	- train_value.py
	- model_value.npz
	- optimizer_value.npz
* player.py
	ランダム
	モンテカルロ木探索
		引数でプレイアウト数を設定
	DQN
	MiniMaxDQN
* evaluate.py
	勝率を出す
	引数で味方と敵プレーヤと対戦回数を指定
* main.py
	入力：盤面（とりあえずファイルで）
	出力：次の手
