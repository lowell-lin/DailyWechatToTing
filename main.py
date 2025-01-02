from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import os
import json
from datetime import datetime, timedelta
import requests
import pytz
from datetime import datetime

tz = pytz.timezone('Asia/Shanghai')
nowtime = datetime.now(tz)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_time():
    dictDate = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期天'
    }
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a


def get_words():
    words = requests.get("https://tenapi.cn/v2/yiyan?format=json").json()
    print(words)
    if words['code'] != 200:
        return get_words()
    return words['data']['hitokoto']


def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather


def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days


if __name__ == '__main__':
    # app_id = os.getenv("APP_ID")
    app_id = "wx9c9ce32f0cd56900"
    # app_secret = os.getenv("APP_SECRET")
    app_secret = "15715b9f67c1d856afc32c11c7a0a2c3"
    # template_id = os.getenv("TEMPLATE_ID")
    template_id = "C4rF5oL9cF8ZdVK5mlIoV2LPrqzHqvdWKzIeAyW2GI8"
    # weather_key = os.getenv("WEATHER_API_KEY")
    weather_key = "SfNuCvlskOuT5_ixh"

    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    f = open("users_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    data = js_text['data']
    num = 0
    words = get_words()
    out_time = get_time()
    print(words, out_time)

    for user_info in data:
        born_date = user_info['born_date']
        birthday = born_date[5:]
        city = user_info['city']
        user_id = user_info['user_id']
        name = user_info['user_name'].upper()

        wea_city, weather = get_weather(city, weather_key)
        data = dict()
        data['time'] = {'value': out_time}
        data['words'] = {'value': words}
        data['weather'] = {'value': weather['text_day']}
        data['city'] = {'value': wea_city}
        data['tem_high'] = {'value': weather['high']}
        data['tem_low'] = {'value': weather['low']}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': weather['wind_direction']}
        data['name'] = {'value': name}

        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")
