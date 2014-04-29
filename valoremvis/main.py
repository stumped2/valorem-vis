import json
import redis
import requests
from flask import Flask, session, request, abort, jsonify, render_template, redirect
from lepl.apps.rfc3696 import Email
from base64 import b64decode

app = Flask(__name__)

app.config.from_object('config')


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/auth/login', methods=["POST"])
def login():
    if 'assertion' not in request.form:
        abort(400)

    assertion_info = {'assertion': request.form['assertion'],
                        'audience': 'localhost:5000' } # window.location.host
    resp = requests.post('https://verifier.login.persona.org/verify',
                        data=assertion_info, verify=True)

    if not resp.ok:
        print "Invalid response from remote verifier"
        abort(500)

    data = resp.json()

    if data['status'] == 'okay':
        session.update({'email': data['email']})
        email_key = get_email_ia(request.form['assertion'])
        data = []
        data.append(request.form['assertion'])
        app.config['CACHE'].set(email_key, json.dumps(data))
        return resp.content

@app.route('/auth/logout', methods=["POST"])
def logout():
    session.pop('email', None)
    return redirect('/')

@app.route('/store', methods=["GET"])
def store():
  session.permanent = True
  verifier = Email()

  if verify_store_args(request.args):
    data = []
    email = request.args.getlist('email')
    pgp = request.args.getlist('pgp')

    #pgp_key = get_pgp_key(pgp[0])
    pgp_key = pgp[0]
    email_key = email[0]

    if not verifier(email_key):
      print "Incorrect email"
      abort(400)

    if email_key is None:
      print "email not found"
      abort(400)

    if pgp_key is None:
      print "PGP key not found"
      abort(400)

    data = app.config['CACHE'].get(email_key)

    if data is None:
      print "email not found in storage"
      abort(404)

    data = json.loads(data)
    data.append(pgp[0])
    app.config['CACHE'].set(email_key, json.dumps(data))
    app.config['CACHE'].set(pgp_key, json.dumps(data))

    return jsonify({'success': True})

  else:
    print "Incorrect in general url"
    abort(400)

@app.route('/search', methods=["GET"])
def search():
  session.permanent = True

  if verify_search_args(request.args):
    if 'pgp' in request.args:
      key = request.args.getlist('pgp')
    elif 'email' in request.args:
      key = request.args.getlist('email')
    else: #catch all, should never get here because verify_search_args
      abort(400)

    data = app.config['CACHE'].get(key[0])

    if data is None:
      print "backed ia not found"
      abort(404)

    data = json.loads(data)
    return jsonify({'bia': data[0], 'pgp': data[len(data) - 1]})

  else:
    print "Incorrect search url"
    abort(400)


def get_email_ia(backedia):
  '''
  Rudamentory format checking of the backed ia.
  Given a backed identity assertion, it will extrac the email from it
  to be used as a key for storage.

  BUG: It seems persona right now is sending back incorrectly padded certs
       for some email addresses. Our current fix is to add a single or a double
       '=' character. If that still doesn't work, then fail outright.
  '''

  verifier = Email()
  try:
    ia = backedia.replace('~','.').split('.')
  except:
    print "Invalid backed identity assertion format"
    return None

  try:
    cert = b64decode(ia[1])
  except TypeError:
    print "Concluding Cert needs padding 1"
    ia[1] += "="  # add first padding char
    try:
      cert = b64decode(ia[1])
    except TypeError:
      print "Concluding Cert needs padding 2"
      ia[1] += "="  # add second padding char
      try:
        cert = b64decode(ia[1])
      except:
        print "Concluding invalid Cert."
        return None

  cert = json.loads(cert)
  if verifier(cert['principal']['email']):
    return cert['principal']['email']
  else:
    print "Invalid email format"
    return None

def verify_store_args(args):
  '''
  len of args must be 2.
  "Email" and "PGP" must be keys in args.
  len of list of data associated with each key must be 1.
  '''

  if len(args) == 2:
    if 'email' in args and 'pgp' in args:
      email = args.getlist('email')
      pgp = args.getlist('pgp')
      if len(email) == 1 and len(pgp) == 1:
        return True
      else:
        return False
    else:
      return False
  else:
    return False

def verify_search_args(args):
  '''
  len of args must be 1.
  "PGP" or "Email" must be the search by arguement.
  len of list of data associated with the search key must be 1.
  If "Email" is the key, verify email sent is a correctly formatted email
  '''

  verifier = Email()
  if len(args) == 1:
    if 'pgp' in args:
      pgp = args.getlist('pgp')
      if len(pgp) == 1:
        return True
      else:
        return False
    elif 'email' in args:
      email = args.getlist('email')
      if len(email) == 1:
        if verifier(email[0]):
          return True
        else:
          return False
      else:
        return False
    else:
      return False
  else:
    return False


def get_pgp_key(pgp):
  '''
  Rudamentory format checking for Privly assertion.
  Will extract a PGP public key to be used as a key in storage.
  '''

  try:
    ia = pgp.split('.')
    if len(ia) == 2:
      return ia[0]
    else:
      return None
  except:
    return None


# TODO: Verify the pgp pub key and signature match]
