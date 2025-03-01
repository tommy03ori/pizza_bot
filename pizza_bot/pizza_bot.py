import datetime as dt
import cv2
from ultralytics import YOLO
import discord
from discord.ext import tasks

# 初期設定部分
TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True

CHANNEL_ID = 0
MASTER_ID = 0

# YOLOの準備
model = YOLO('yolov8n.pt')

# 本体
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    loop.start()
    print("ログインしました")
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('こんにちは，pizza_botです！\n誰かがピザを食べた場合全員に通知します．')

# 毎日午前2:55に自爆する部分
@tasks.loop(seconds=60)
async def loop():
    # 現在の時刻
    year = dt.datetime.now().strftime('%y')
    month = dt.datetime.now().strftime('%m')
    date = dt.datetime.now().strftime('%d')
    now = dt.datetime.now().strftime('%H:%M')
    # print(date)
    if now == '00:00' and date == "01":
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(f"{month}月になりました！")
        # historyを開く
        f_history = open("./past_data/history.txt", "a",encoding="UTF-8")
        # 先月の出費を出力
        f_total_price = open("./past_data/total_price.txt")
        price = f_total_price.readline()
        await channel.send(f"先月の累計出費: {price}円")
        # 先月の情報を登録　month - 1してアレする
        month = int(month) - 1
        if month == 0:
            month = 12
            year = str(int(year) - 1)
        month = str(month)
        # hitory書き込み
        f_history.write(f"{year}年{month}月 {price}円 ")
        f_total_price.close()
        # ファイルの数字をリセットする
        f_total_price = open("./past_data/total_price.txt", "w")
        f_total_price.write("0")
        f_total_price.close()

        # 先月のピザ枚数を出力
        f_total_pizza = open("./past_data/total_pizza.txt")
        pizza_count = f_total_pizza.readline()

        await channel.send(f"先月のピザ枚数: {pizza_count}枚")
        f_history.write(f"{pizza_count}枚\n")
        f_total_pizza.close()
        # ファイルの数字をリセットする
        f_total_pizza = open("./past_data/total_pizza.txt", 'w')
        f_total_pizza.write("0")
        f_total_pizza.close()
        f_history.close()
        print("送った")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    

    # コマンド対応
    if message.content == "p!hello":
        await message.channel.send("こんにちは，pizza_botです！\n"\
                                    "ピザ画像の検出，食費の管理をお手伝いします．\n"\
                                    "コマンド一覧:\n"\
                                    "   p!hello: このメッセージを再度表示\n"\
                                    "   p!total: 今月の出費の合計を表示\n"\
                                    "   p!pizza: 今月食べたピザの枚数を表示\n"\
                                    "   p!lastpizza: 最後にピザを食べた日を表示\n"\
                                    "   p!prediction: 最新画像の分類結果を表示\n"\
                                    "   p!history: これまでの出費とピザ枚数を月ごとに表示\n"\
                                    "これらのコマンドは私のプロフィール欄でいつでも見ることが出来ます．")
    if message.content == "p!total":
        f_total_price = open("./past_data/total_price.txt")
        await message.channel.send(f"今月の累計出費: {f_total_price.readline()}円")
        f_total_price.close()
    if message.content == "p!pizza":
        f_total_pizza = open("./past_data/total_pizza.txt")
        await message.channel.send(f"今月の累計ピザ回数: {f_total_pizza.readline()}枚")
        f_total_pizza.close()
    if message.content == "p!lastpizza":
        f_last_pizza_date = open("./past_data/last_pizza_date.txt")
        await message.channel.send(f"最後にピザを食べた日: {f_last_pizza_date.readline()}")
        f_last_pizza_date.close()
    if message.content == "p!prediction":
        f_past_prediction = open("./past_data/past_prediction.txt")
        predictions = []
        for prediction in f_past_prediction:
            predictions.append(prediction)
        f_past_prediction.close()
        await message.channel.send(f"直近の分類結果: {predictions[-1]}")
        await message.channel.send(file=discord.File("./picture/prediction.png"))
    if message.content == "p!history":
        f_history = open("./past_data/history.txt", encoding="UTF-8")
        await message.channel.send("ピザ履歴\n")
        await message.channel.send(f_history.read())

    # 家計簿をつける処理
    if message.content.endswith("円") and message.author.id == MASTER_ID:
        price = int(message.content[:-1])
        f = open("./past_data/total_price.txt", 'r')
        total_price = int(f.readline())
        f.close()
        total_price += price
        f = open("./past_data/total_price.txt", "w")
        f.write(f"{total_price}")
        await message.channel.send(f"今月の累計出費：{total_price}円")
        f.close()


    # 画像が投稿されたときの処理
    if len(message.attachments) > 0:
        print("画像を検出しました")
        for attachment in message.attachments:
            if attachment.content_type.startswith("image"):
                await attachment.save("./picture/img.png")
                results = model("./picture/img.png")
                # 結果画像を取っておく
                output_img = results[0].plot()
                cv2.imwrite("./picture/prediction.png", output_img)
                for result in results:
                    # label に検出されたクラスが保存される
                    label = []
                    for box in result.boxes:
                        label.append(model.names[int(box.cls)])
                    print(label)
                    # 最新のラベルをテキストに保存
                    f_past_prediction = open("./past_data/past_prediction.txt", "a")
                    f_past_prediction.write(" ".join(label) + "\n")
                    f_past_prediction.close()
                    if 'pizza' in label:
                        if message.author.id == MASTER_ID:
                            # 合計ピザ枚数の更新
                            f_total_pizza = open("./past_data/total_pizza.txt", "r")
                            total_pizza = int(f_total_pizza.readline()) + 1
                            f_total_pizza.close()
                            f_total_pizza = open("./past_data/total_pizza.txt", "w")
                            f_total_pizza.write(f"{total_pizza}")
                            f_total_pizza.close()
                            # 最後にピザを食べた日を更新
                            f_last_pizza_date = open("./past_data/last_pizza_date.txt", "w")
                            d_today = dt.date.today()
                            f_last_pizza_date.write(f"{d_today.year}-{d_today.month}-{d_today.day}")
                            f_last_pizza_date.close()
                            f_total_price = open("./past_data/total_price.txt")
                            total_price = f_total_price.readline()
                            await message.channel.send(f"@everyone ピザを検出しました\n今月の累計ピザ枚数: {total_pizza}枚\n今月の累計出費: {total_price}円")
                            f_total_price.close()
                        else:
                            await message.channel.send(f"ピザを検出しました")

client.run(TOKEN)
