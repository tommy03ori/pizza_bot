# なにこれ
discordのテキストチャンネルに投稿された画像からピザを検出するとお知らせしてくれるbot．ピザの認識はYOLOv8でやっています．家計簿機能付き．

# 導入
## 1. clone
```
git clone https://github.com/tommy03ori/pizza_bot.git
```
## 2. 必要なライブラリのインストール
`/pizza_bot`直下で以下のコマンドを実行でOK．
```
pip install requirements.txt
```
## 3. YOLOv8のpretrainのインストール
[yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt)をダウンロードして`/pizza_bot`直下に置く．
## 4. トークン，IDの取得
- discord botのトークン`TOKEN`
- botを動かすチャンネルのID`CHANNEL_ID`
- 家計簿をつける人のID`MASTER_ID`

をそれぞれ取得し，`/pizza_bot/pizza_bot.py`の変数に挿入
## 5. 起動
`/pizza_bot`直下で
```
python pizza_bot.py
```
で実行して，botのチャンネルにあいさつ文が表示されれば成功．

# 機能一覧
- 準備中

# 使い方
- 準備中
