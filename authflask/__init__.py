from flask import Flask
#from functools import wraps
import sys

#from authenticate import requires_scope, requires_admin
#from flask import session

#from app_dispatch.authenticate import SECRET_KEY
from authenticate import Auth

class AuthFlask(Flask):
   
    def __init__(self, *args, **kwargs):
        try:
            self.permission=kwargs.pop('permission')
        except KeyError:
            print("Error:{} needs a permission attribute.".format(self.__class__.__name__))
            sys.exit()
        super().__init__(*args, **kwargs)
        self.secret_key = Auth.SECRET_KEY

    def route(self, rule, **options):   
        def decorator(f):
            # This achieves the same effect as @app.route('/X') @requires_scope(xxx)
            
            if self.permission == 'product':
                pass
            elif self.permission == 'admin':
                f=Auth.requires_admin(f)
            else:
                print("Checking permission")
                f=Auth.requires_scope("access:"+self.permission)(f)
            
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator



