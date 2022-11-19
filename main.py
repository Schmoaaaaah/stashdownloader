from flask import Flask, request, jsonify
import json
from downloader import videoslist, phprofile, test
from os import environ

mode = environ.get("DEBUG")

app = Flask(__name__)


@app.route('/videourllist', methods=['PUT'])
def videolistdownloader():
    record = json.loads(request.data)
    if record.get('method') == 'videos':
        videoslist(record.get('urls'))
        return jsonify({"status":"OK","message":"Videos added to Stash"})
    else:
        return jsonify({"status":"Error"})
    

@app.route('/phprofile', methods=['PUT'])
def phprofiledownloader():
    record = json.loads(request.data)
    if record.get('method') == 'phprofile':
        #info = test(record.get('urls'))
        info = phprofile(record.get('urls'))
        return jsonify(info)
    else:
        return jsonify({"status": "Error"})

app.run(debug=mode, host='0.0.0.0')
