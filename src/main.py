import threading
from strategy import StrategySelector
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    json_data = request.get_json()

    thr = threading.Thread(target=main, args=(json_data['url'], json_data['filename']), kwargs={})
    thr.start()

    return make_response(jsonify({
        'status': 'success'
    })), 201


def main(url, filename):
    context = StrategySelector(url=url, filename=filename)
    context.execute()


if __name__ == '__main__':
    app.run()
