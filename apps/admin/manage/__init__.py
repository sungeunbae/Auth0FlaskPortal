import http.client
import json

from authflask import AuthFlask
from flask import session
from flask import render_template

from authenticate import Auth
from constants import MGMNT_API_TOKEN

app = AuthFlask(__name__)


@app.route("/")
def read_admin():
    """A valid access token and an appropriate scope are required to access this route
    """  
    return render_template('dashboard.html',
                           userinfo=session[MGMNT_API_TOKEN],
                           userinfo_pretty=json.dumps(session[MGMNT_API_TOKEN], indent=4))


##this enables direct access to management API's endpoints. https://auth0.com/docs/api/management/v2 
@app.route("/<path:subpath>", methods=['GET'])
def get_request_management_api(subpath):
    conn = http.client.HTTPSConnection(Auth.AUTH0_DOMAIN+":443")
    headers = { "Authorization":"Bearer "+session[MGMNT_API_TOKEN], 'content-type' : "application/json"}
    conn.request("GET", Auth.AUTH0_BASE_URL+"/api/v2/"+subpath, headers= headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return render_template('dashboard.html',
                           userinfo=data,
                           userinfo_pretty=json.dumps(json.loads(data), indent=4))

if __name__ == '__main__':
    app.run()





	
