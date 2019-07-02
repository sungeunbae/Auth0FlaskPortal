from flask import Flask
#from functools import wraps
import sys

from authenticate import requires_scope, requires_admin
from flask import session

from app_dispatch.authenticate import SECRET_KEY


class AuthFlask(Flask):
   
    def __init__(self, *args, **kwargs):
        print("{} {}".format(self.__class__.__name__,SECRET_KEY))
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
            if self.permission == 'admin':
                f=requires_admin(f)
            else:
                f=requires_scope(self.permission)(f)
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator



