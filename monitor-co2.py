import pandas as pd
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# CSV ファイルの場所を必要に応じて変える
path = '/home/pi/logs/co2.csv'

# LINE チャネルアクセストークン
CHANNEL_ACCESS_TOKEN = ''

# LINE 経由で友達にメッセージを送る
def send_message(text):
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

    try:
        line_bot_api.broadcast(TextSendMessage(text=text))
    except LineBotApiError as e:
        print(e.message)

# 前回実行時の状態を取得する
def get_previous_state(state_file_path: str):
    try:
        with open(state_file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# 状態をファイルに保存する
def write_state(state: str, state_file_path: str):
    with open(state_file_path, 'w') as file:
        file.write(state)

# レベル判定
def get_state(co2: float):
    if co2 >= 1000:
        return "危険"
    elif 900 <= co2 < 1000:
        return "警告"
    else:
        return "正常"

def main():

    # CSVファイルからデータを読み込む
    df = pd.read_csv(path, parse_dates=['timestamp'])

    # 現在の時間を取得
    current_time = datetime.now()

    # 直近5分のデータを抽出
    recent_data = df[(df['timestamp'] >= current_time - timedelta(minutes=5)) & (df['timestamp'] <= current_time)]

    # CO2の平均を計算
    average_co2 = recent_data['co2'].mean()

    # CO2の異常判定
    current_state = get_state(average_co2)

    # 状態保存用のファイル
    state_file_path = 'previous_state.txt'
    previous_state = get_previous_state(state_file_path)

    # 状態が前回と変化した場合にメッセージを出力
    if previous_state is None or current_state != previous_state:

        message = ""
        if current_state == "危険":
            message = "ちょっと高めなので換気して！"
        elif current_state == "警告":
            message = "まだ大丈夫だけど換気できたらして！"
        elif current_state == "正常":
            message = "正常だよ！大丈夫！"

        alert = "[ " + current_state + " ] CO2 濃度: " + str(average_co2) + "\n\n" + message
        send_message(alert)

    write_state(current_state, state_file_path)


if __name__ == "__main__":
    main()