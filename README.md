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
