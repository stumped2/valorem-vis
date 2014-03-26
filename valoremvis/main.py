import redis 

from flask import Flask, session, request, abort, jsonify


app = Flask(__name__)

app.config.from_object('config')


@app.route('/<key>')
def index(key):
    session.permament = True
    if 'value' not in request.args:
        value = app.config['CACHE'].get(key) 
        if not value:
            abort(404)
        return jsonify({'value': value })

    app.config['CACHE'].set(key, request.args.get('value'))
    return jsonify({'success': True})

