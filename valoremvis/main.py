from flask import Flask, session, request, abort, jsonify


app = Flask(__name__)

app.config['SECRET_KEY'] = 'This key is really secret NOT'


@app.route('/<key>')
def index(key):
    session.permament = True
    if 'value' not in request.args:
        if key not in session:
            abort(404)
        return jsonify({'value': session[key]})

    session[key] = request.args.get('value')
    return jsonify({'success': True})

