from flask import Flask
#from functools import wraps
import sys

from authenticate import requires_scope
from flask import session

sys.path.append("/home/seb56/local/flask_dev")
from app_dispatch.constants import SECRET_KEY


class AuthFlask(Flask):
   
    def __init__(self, *args, **kwargs):
        
        try:
            self.permission=kwargs.pop('permission')
        except KeyError:
            print("Error:{} needs a permission attribute.".format(self.__class__.__name__))
            sys.exit()

        super().__init__(*args, **kwargs)
        self.secret_key = SECRET_KEY

    def route(self, rule, **options):   
        def decorator(f):
            # This achieves the same effect as @app.route('/X') @requires_scope(xxx)
            f=requires_scope(self.permission)(f)
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator



