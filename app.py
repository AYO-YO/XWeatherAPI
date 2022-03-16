from flask import Flask, abort, url_for
import json
import functools
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@functools.lru_cache()
def getData(url) -> json:
    session = requests.session()
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    s = session.get(url, headers=header)
    j = json.loads(s.text)
    return j

def load_json(path: str) -> dict:
    with open(path, 'rt', encoding='utf-8') as f:
        j = json.loads(f.read().strip())
        f.close()
    return j


@app.route('/getcity/<string:code>/<string:city>')
def get_city(code, city):
    path = './static/city_info.json'
    print(path)
    match code:
        case 'code' | 'en':
            j = load_json(path)
            return j[city][code]
        case _:
            abort(404)
            return None





if __name__ == '__main__':
    app.run()
