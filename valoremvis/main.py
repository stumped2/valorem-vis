import json
import redis 

from flask import Flask, session, request, abort, jsonify
from lepl.apps.rfc3696 import Email

app = Flask(__name__)

app.config.from_object('config')
verifier = Email()

@app.route('/<key>')
def index(key):
  session.permament = True
  values = app.config['CACHE'].get(key)
  if verify_args(request.args):
    if len(request.args) == 0:
      if not values:
        abort(404)
      else:
        values = json.loads(values)
        return jsonify({'Persona': values[0], 'Privly': values[1]})
    ia = request.args.getlist('Persona')
    privly = request.args.getlist('Privly')
    ia = ia[0]
    privly = privly[0]
    data = []
    data.append(ia)
    data.append(privly)
    app.config['CACHE'].set(key, json.dumps(data))
    return jsonify({'success': True})
  else:
    abort(400)



# Get email for key from backed ia

def verify_args(args):
  '''
  len of ars must be either 2 (storing data) or 0 (queryring data).
  "Persona" and "Privly must be keys in args.
  '''

  if len(args) == 2: # storing data
    if 'Persona' in args and 'Privly' in args:
      ia = args.getlist('Persona')
      privly = args.getlist('Privly')
      if len(ia) == 1 and len(privly) == 1:
        return True
      else:
        return False
    else:
      return False

  elif len(args) == 0: # querying data
    return True

  else: # catch any unknown things
    return False
