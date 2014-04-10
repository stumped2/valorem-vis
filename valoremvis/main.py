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
        abort(500)

    data = resp.json()

    if data['status'] == 'okay':
        session.update({'email': data['email']})
        print session
        return resp.content

@app.route('/auth/logout', methods=["POST"])
def logout():
    session.pop('email', None)
    return redirect('/')

@app.route('/<action>')
def action(action):
  session.permament = True

  if action == 'store':
    if verify_store_args(request.args):
      data = []
      ia = request.args.getlist('Persona')
      privly = request.args.getlist('Privly')
      email_key = get_email_ia(ia[0])
      pgp_key = get_pgp_ia(privly[0])
      
      if email_key is None:
        abort(400)
      
      if pgp_key is None:
        abort(400)

      data.append(ia[0])
      data.append(privly[0])
      app.config['CACHE'].set(email_key, json.dumps(data))
      app.config['CACHE'].set(pgp_key, json.dumps(data))
      
      return jsonify({'success': True})
  
    else:
      abort(400)
  
  elif action == 'search':
    if verify_search_args(request.args):
      if 'PGP' in request.args:
        key = request.args.getlist('PGP')
      elif 'Email' in request.args:
        key = request.args.getlist('Email')
      else: #catch all, should never get here because verify_search_args
        abort(400)

      data = app.config['CACHE'].get(key[0])
      
      if data is None:
        abort(404)
      
      data = json.loads(data)
      return jsonify({'Persona': data[0], 'Privly': data[1]})
    
    else:
      abort(400)
  
  else:
    abort(400)

# Get email for key from backed ia

def verify_store_args(args):
  '''
  len of args must be 2.
  "Persona" and "Privly must be keys in args.
  len of list of data associated with each key must be 1.
  '''

  if len(args) == 2:
    if 'Persona' in args and 'Privly' in args:
      ia = args.getlist('Persona')
      privly = args.getlist('Privly')
      if len(ia) == 1 and len(privly) == 1:
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
    if 'PGP' in args:
      pgp = args.getlist('PGP')
      if len(pgp) == 1:
        return True
      else:
        return False
    elif 'Email' in args:
      email = args.getlist('Email')
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

def get_email_ia(backedia):
  '''
  Rudamentory format checking of the backed ia.
  Given a backed identity assertion, it will extrac the email from it
  to be used as a key for storage.
  '''

  verifier = Email()
  try:
    ia = backedia.replace('~','.').split('.')
    cert = b64decode(ia[1])
    cert = json.loads(cert)
    if verifier(cert['principal']['email']):
      return cert['principal']['email']
    else:
      return None
  except:
    return None

def get_pgp_ia(privlyia):
  '''
  Rudamentory format checking for Privly assertion.
  Will extract a PGP public key to be used as a key in storage.
  '''

  try:
    ia = privlyia.split('.')
    if len(ia) == 2:
      return ia[0]
    else:
      return None
  except:
    return None
# TODO: Verify the pgp pub key and signature match]
