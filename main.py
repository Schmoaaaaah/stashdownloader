from flask import Flask, request, jsonify
import json
from downloader import videoslist
from os import environ

mode = environ.get("DEBUG")

app = Flask(__name__)


@app.route('/videourllist', methods=['PUT'])
def create_record():
    record = json.loads(request.data)
    if record.get('method') == 'videos':
        videoslist(record.get('urls'))
        return jsonify({"status":"OK","message":"Videos added to Stash"})
    else:
        return jsonify({"status":"Error"})

app.run(debug=mode, host='0.0.0.0')
