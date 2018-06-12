from flask import Flask, jsonify

from oneconfig import Configuration

app = Flask(__name__)

config = Configuration()
config.add_file_by_prefix('appsettings')


@app.route('/')
def index():
    return jsonify({'mode': config['mode']})


if __name__ == '__main__':
    app.run(port=5001)
