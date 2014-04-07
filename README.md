# Valorem Vis

"the value you want"


Dead simple Flask key-value storage using redis. Valorem Vis is not tested for security and should only be used in development environments for experiment purposes.


# How to use

1. [Setup Redis](http://redis.io/topics/quickstart)
1. git clone https://github.com/spectralsun/valorem-vis.git
1. cd valorem-vis
1. virtualenv env
  - **Note**: you will need to specify python 2.X if python 3.X is default on your system (example: "virtualenv -p /usr/bin/python2 env")
1. source env/bin/activate
1. pip install -r requirements.txt
1. cp config.py.dist config.py
1. python manage.py runserver

# Interaction
## Uploading
using the ``store`` endpoint of the Directory Provider, you can upload a **Backed Identity Assertion** as well as a **PGP Public Key** and the pgp key signature.
The expected upload format is:
```javascript
{
   "Persona": "<base64 encoded pserona backed identity assertion>",
    "Privly": "<base64 encoded pgp public key>.<pgp signature>"
}
```

All the uploading to the Directory Provider is handled by ``GET`` requests.
Example:
```
http://<ip or dns>:<port>/store?Persona=<backed identity assertion>&Privly=<pgp key>.<pgp signature>
```
The Directory Provider will then verify the backed identity assertion with a persona verifier, decompose the backed ia to extract the email, and then store the Privly information and Persona information in the keystore using the email as the key. The Directory will also sotre the same information using the pgp key as the key value store key.

If anything other than ``Privly`` and ``Persona`` are sent to the directory provider, it will return a ``400`` error. If an incorrectly formatted backed identity assertion is uploaded, it will return a ``400`` as well.

## Searching
Using the ``search`` endpoint of the directory provide, you can query the keyvalue store for the backed identity assertion and pgp public key by either **Email** or **PGP Public key**.
An example is:
```
http://<ip or dns>:<port>/search?Email=<validly formatted email>
```
to search by email. To search by pgp public key:
```
http://<ip or dns>:<port>/search?PGP=<pgp public key>
```

If the directory provider cannot find any information associated with the email or the pgp key, it will return a ``404`` error.

If anything other than ``PGP`` or ``Email`` , it will return a ``400`` error.
