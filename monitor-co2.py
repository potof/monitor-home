import pandas as pd
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# CSV ファイルの場所を必要に応じて変える
path = '/home/pi/logs/co2.csv'

# 状態保存用のファイル
state_file_path = 'previous_state.txt'

# LINE チャネルアクセストークン
CHANNEL_ACCESS_TOKEN = ''

def send_message(text):
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

    try:
        line_bot_api.broadcast(TextSendMessage(text=text))
    except LineBotApiError as e:
        print(e.message)

# 状態保存ファイルから前回の状態を読み込む
try:
    with open(state_file_path, 'r') as file:
        previous_state = file.read().strip()
except FileNotFoundError:
    previous_state = None

# CSVファイルからデータを読み込む
df = pd.read_csv(path, parse_dates=['timestamp'])

# 現在の時間を取得
current_time = datetime.now()

# 直近5分のデータを抽出
recent_data = df[(df['timestamp'] >= current_time - timedelta(minutes=5)) & (df['timestamp'] <= current_time)]

# CO2の平均を計算
average_co2 = recent_data['co2'].mean()

# CO2の異常判定
current_state = None
message = ""
if average_co2 >= 1000:
    current_state = "危険"
    message = "ちょっと高めなので換気して！"
elif 900 <= average_co2 < 1000:
    current_state = "警告"
    message = "まだ大丈夫だけど換気できたらして！"
else:
    current_state = "正常"
    message = "正常だよ！大丈夫！"

# 状態が前回と変化した場合にメッセージを出力
if previous_state is None or current_state != previous_state:
    alert = "[ " + current_state + " ] CO2 濃度: " + str(average_co2) + "\n\n" + message
    send_message(alert)

# 現在の状態を外部ファイルに書き込む
with open(state_file_path, 'w') as file:
    file.write(current_state)
