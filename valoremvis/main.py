import json
import redis
import requests
from flask import Flask, session, request, abort, jsonify, render_template, redirect, Response
from lepl.apps.rfc3696 import Email
import base64
from dirp_storage import which_store

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
        print 'Invalid response from remote verifier'
        abort(500)

    data = resp.json()

    if data['status'] == 'okay':
        session.update({'email': data['email']})
        email_key = get_email_ia(request.form['assertion'])
        value = app.config['CACHE'].get(email_key)

        value, flag = which_store(value, 'bia', request.form['assertion'])

        print 'storing under email'
        app.config['CACHE'].set(email_key, json.dumps(value))

        if flag:
          print 'storing under pgp key'
          pgp_key = value[0]['pgp']
          app.config['CACHE'].set(pgp_key, json.dumps(value))
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
    email = request.args.getlist('email')
    pgp = request.args.getlist('pgp')

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

    value = app.config['CACHE'].get(email_key)

    value, flag = which_store(value, 'pgp', pgp_key)

    print 'storing under email'
    app.config['CACHE'].set(email_key, json.dumps(value))


    if flag:
      print 'storing under pgp key'
      pgp_key = value[0]['pgp']
      app.config['CACHE'].set(pgp_key, json.dumps(value))

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
      print "Incorrect query url"
      abort(400)

    value = app.config['CACHE'].get(key[0])

    if value is None:
      print "backed ia not found"
      abort(404)

    value = json.loads(value)
    temp = value[0]

    if 'bia' in temp and 'pgp' in temp:
      return Response(json.dumps(value), mimetype='application/json')

    if 'bia' not in temp and 'pgp' not in temp:
      print 'somehow stored an invalid record without pgp and bia'
      abort(500)

    if 'bia' not in temp or 'pgp' not in temp:
      print 'unmatched pgp to bia, returning first matched record'
      # If pgp unmatched to bia, return first matched record

      if len(value) < 2:
        # We only 1 record in the list, unmatched. Don't return
        print 'No matched records to return'
        abort(404)

      else:
        print 'Removing unmatched record from return list'
        value.pop(0)

      if not isinstance(value, list):
        print 'Making sure record is a list'
        value = [value]

      return Response(json.dumps(value), mimetype='application/json')

    # Use thig instead of jsonify, jsonify doesn't allow lists
    return Response(json.dumps(value), mimetype='application/json')

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
       This bug is addressed by using the added from_base64url function which
       will pad the base64 url correctly.
  '''

  verifier = Email()

  # Try to break up the BIA into useful parts
  try:
    ia = backedia.replace('~','.').split('.')
  except:
    print "Invalid backed identity assertion format"
    return None

  # Try to decode the User Certificate to get the email
  try:
    cert = from_base64url(str(ia[1]))
  except:
    print "Invalid user certificate"
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
  return False

# TODO: Verify the pgp pub key and signature match]

def from_base64url(src):
    return base64.urlsafe_b64decode(src + '=' * (len(src) % 4 ))
