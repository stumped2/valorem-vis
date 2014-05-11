# Definitions, params, and return values
While some of the functions listed here do not take and actual parameter to function, they rely on request arguments available to them by the flask routes.


index
=====
This function is the landing point for the Directory Provider.
It renders the ```index.html``` page that allows to user to "login" to persona.

### Params
None

### Usage
It should do nothing more than just facilitate the persona login process for the Privly PGP application.

### Returns

login
=====
This function is responsible for handling the Persona log in protocol.

### Params
The landing point should be a ```POST``` request with the Persona Backed Identity Assertion (or referred to as ```assertion```) in the data.
### Usage
If the ```assertion``` was sent in the request, we must send it to a Persona verifier. Once verified, the ```assertion``` is stored in the key-value store.

There are 2 fields of data to send to the Persona verifier:

```javascript
{
  'assertion': <Persona Backed Identity Assertion (base64url encoded)>,
  'audience': <dns:port of the webserver>
}
```

Using this python flask as a local example:
```javascript
{
  'assertion': <Persona backed identity assertion>,
  'audience': 'localhost:5000'
}
```

Right now, we use Persona's remote verifier to verify the ```assertion```. The url is ```https://verifier.login.persona.org/verify```.
You can check this verification manually using a tool like ```curl```:

```
curl --data "assertion=<backed identity assertion>&audience=<dns:port>" https://verifier.login.persona.org/verify
```

### Returns
If for some reason the ```assertion``` is not in the request, the page should return an ```HTTP 400``` error indicating a bad request.

The ```login``` function is also crucial because we store the **_verified_** backed identity assertion into the key-value store under the email address the user logged into persona with.

logout
======
### Params
### Usage
### Returns
This function updates the log in button on the Directory Provider index page to indicate the user should login.

It will redirect to the index page of the Directory Provider.

store
=====
### Params
### Usage
### Returns
This function is what will take the PGP public key from the Privly PGP application, identified by and **email**, and store it on the Directory Provider.

```email```: The email address associated with the PGP public key.
```pgp```: The PGP public key to upload to the Directory Provider.



search
======
### Params
### Usage
### Returns

get_email_ia
============
### Params
### Usage
### Returns

verify_store_args
=================
### Params
### Usage
### Returns

verify_search_args
==================
### Params
### Usage
### Returns

from_bas64url
=============
### Params
### Usage
### Returns

which_store
===========
### Params
### Usage
### Returns