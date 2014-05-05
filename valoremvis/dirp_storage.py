from flask import abort
import json
def which_store(data, key, value):

  # A flag used for key updates/store later.
  flag = False

  # Check to see if data is empty
  if data is None:

    print 'email not found in storage, creating new record list'
    to_store = dict()
    to_store[key] = value
    data = [to_store]

  else:
    print 'Email found in storage'
    data = json.loads(data)
    # Get the latest dict in the list
    temp = data[0]

    if 'bia' in temp:
      print 'bia key exists'

      if 'pgp' in temp:
        print 'pgp key exists'

        # A matched record was found, create new record
        print 'Matched record found, creating new record'
        to_store = dict()
        to_store[key] = value

        # Make sure the new record is at the beginning of the list
        data.insert(0, to_store)

      else:
        # If key is bia, overwrite unmatched bia
        # If key is pgp, match bia to pgp
        temp[key] = value
        if key is 'pgp':
          print 'matching bia to pgp'
          flag = True
        else:
          print 'overwriting unmatched bia'

    else:
      print 'key "bia" not found'
      if 'pgp' in temp:
        temp[key] = value
        if key is 'bia':
          print 'Matching bia to pgp'
          flag = True
        else:
          print 'Overwriting unmatched pgp'

      else:
        print 'The server somehow stored invalid data'
        abort(500) # I don't know if this is valid here

  return data, flag