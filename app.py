import functools
import json

import requests
from flask import Flask, abort, make_response, request

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return '<h2>2fanbaby API 中心</h2>'


@functools.lru_cache()
def getWebData(url) -> json:
    session = requests.session()
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    s = session.get(url, headers=header)
    j = json.loads(s.text)
    return j


@functools.lru_cache()
def load_json(path: str) -> dict:
    with open(path, 'rt', encoding='utf-8') as f:
        j = json.loads(f.read().strip())
        f.close()
    return j


@functools.lru_cache()
def get_city(city, info) -> bool:
    """
    获取城市代码或拼音
    :param city: 城市，汉字，不带市县这些单位，例如：北京
    :param info: 需要代码(code)或是拼音(en)
    :return: 
    """
    path = './static/city_info.json'
    try:
        match info:
            case 'code' | 'en':
                j = load_json(path)
                return j[city][info]
            case _:
                return False
    except KeyError:
        return False


data = {
    "high_temp": "N/A",  # 当日最高温
    "low_temp": "N/A",  # 日最低温
    "current_temp": "N/A",  # 实时温度
    "wt_state": "N/A",  # 当前天气状态
    "day_1st_high": "N/A",  # 明天高温
    "day_1st_low": "N/A",  # 明天低温
    "day_2nd_high": "N/A",  # 后天高温
    "day_2nd_low": "N/A",  # 后天低温
    "day_3rd_high": "N/A",  # 大后天高温
    "day_3rd_low": "N/A",  # 大后天低温
    "day_1st_state": "N/A",  # 明天天气状态
    "day_2nd_state": "N/A",  # 后天天气状态
    "day_3rd_state": "N/A",  # 大后天天气状态
    "humidity": "N/A",  # 湿度
    "aqi": "N/A",  # 空气质量
    "direct": "N/A",  # 风向
    "power": "N/A",  # 风力
    "pm25": "N/A",  # pm2.5
    "pm10": "N/A",  # pm10
    "aqi_state": "N/A",  # 污染状态
    "time": "N/A"  # 更新时间
}


def parseReq(req):
    """
    统一解析请求值
    :param request: 请求体 
    :return: 数据
    """
    match req.method:
        case "POST":
            print('POST')
            return req.json
        case "GET":
            return req.args
        case _:
            return None


@app.route('/getcity', methods=['GET', 'POST'])
def getCity():
    try:
        req = parseReq(request)
        x = req.get('x')
        y = req.get('y')
        print(x, y)
        return getGaodeApi(x, y)
    except TypeError:
        abort(403)


def getGaodeApi(x, y):
    """
    通过调用高德的API获取位置信息
    :param x: 维度
    :param y: 经度
    :return: 返回市级行政单位，目前县级行政单位无空气质量
    """
    url = f'https://restapi.amap.com/v3/geocode/regeo?key=f7e2de0fbef462404e89d6f465c20d76&location={y},{x}&poitype=&radius=0&extensions=all&batch=false&roadlevel=1'
    j = getWebData(url)
    data = j['regeocode']['addressComponent']['city']
    if data:
        return data[:-1]
    else:
        return str(j['regeocode']['addressComponent']['district'][:-1])


def getHighTemp(j, day_num):
    """
    获取最高温度
    :param j: 需要解析的json数据 
    :param day_num: 天数，第0天为今天
    :return: 高温
    """
    return j['result']['future'][day_num]['temperature'].strip('℃').split('/')[1]


def getLowTemp(j, day_num):
    """
    获取最低温度
    :param j: 需要解析的json数据
    :param day_num: 天数，第0天为今天
    :return: 高温
    """
    return j['result']['future'][day_num]['temperature'].strip('℃').split('/')[0]


def getWtState(j, day_num):
    data = j['result']['future'][day_num]['weather']
    if '转' in data:
        return data.split('转')[0]
    else:
        return data


def getJuheAPI(city):
    j = getWebData(f'http://apis.juhe.cn/simpleWeather/query?city={city}&key=7df95e3c4321b2217e7217ab08db04ca')
    if j['error_code'] != '0':
        data['wt_state'] = j['result']['realtime']['info']
        data['current_temp'] = j['result']['realtime']['temperature']
        data['high_temp'] = getHighTemp(j, 0)
        data['low_temp'] = getLowTemp(j, 0)
        data['day_1st_high'] = getHighTemp(j, 1)
        data['day_1st_low'] = getLowTemp(j, 1)
        data['day_2nd_high'] = getHighTemp(j, 2)
        data['day_2nd_low'] = getLowTemp(j, 2)
        data['day_3rd_high'] = getHighTemp(j, 3)
        data['day_3rd_low'] = getLowTemp(j, 3)
        data['day_1st_state'] = getWtState(j, 1)
        data['day_2nd_state'] = getLowTemp(j, 2)
        data['day_3rd_state'] = getLowTemp(j, 3)
        data['humidity'] = j['result']['realtime']['humidity']
        data['aqi'] = j['result']['realtime']['aqi']
        data['direct'] = j['result']['realtime']['direct']
        data['power'] = j['result']['realtime']['power']


def getAPIBang(city):
    j = getWebData(f'https://api.help.bj.cn/apis/aqi2/?id={get_city(city, "code")}')
    if j["status"] != "412":
        data['pm25'] = j['data'][0]['val']
        data['pm10'] = j['data'][5]['val']
        data['aqi_state'] = j['lev']
        data['time'] = j['updata'][8:10] + ":" + j['updata'][10:]


@app.route('/weather/<string:city>', methods=['GET', 'POST'])
@functools.lru_cache()
def weather(city) -> json:
    """
    天气请求API
    :param city: 请求城市，格式：不带单位，例如：北京 
    :return: json
    """
    match request.method:
        case 'POST' | 'GET':
            # 调用对应的API并更新数据
            getJuheAPI(city)
            getAPIBang(city)
            print(data)
            resp = make_response(json.dumps(data, ensure_ascii=False))
            resp.content_type = 'application/json'
            return resp
        case _:
            abort(403)
            return None


if __name__ == '__main__':
    app.run()
