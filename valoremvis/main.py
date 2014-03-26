import json
import redis 

from flask import Flask, session, request, abort, jsonify


app = Flask(__name__)

app.config.from_object('config')


@app.route('/<key>')
def index(key):
    session.permament = True
    value = app.config['CACHE'].get(key)

    if 'value[]' in request.args: # adding/updating entry
        pubkeys = json.loads(value) if value else []
        values = request.args.getlist('value[]')
        for v in values:
            pubkeys.append(v)
        app.config['CACHE'].set(key, json.dumps(pubkeys))
        return jsonify({'success': True})

    else: # querying data
        if not value:
            abort(404)
        return jsonify({'value': json.loads(value) })
