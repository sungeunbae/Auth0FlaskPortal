from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

from apps.app1 import app as app1
from apps.app2 import app as app2
from apps.app3 import app as app3

access_level={"devel":[app1],
			"eap":[app2],
			"private":[app3]}

app = Flask(__name__)

def get_access_level(this_app):
	for key in access_level:
		if this_app in access_level.get(key):
			return key
	return None

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/{}/app1".format(get_access_level(app1)): app1,
    '/{}/app2'.format(get_access_level(app2)): app2,
    '/{}/app3'.format(get_access_level(app3)): app3
})

@app.route('/')
def hello_world():
    return 'Hello World! from main'

if __name__ == "__main__":
    app.run()