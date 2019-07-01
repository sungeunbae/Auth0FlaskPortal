from flask import Flask
from functools import wraps
import sys



class AuthFlask(Flask):
   
    def __init__(self, *args, **kwargs):
        try:
            self.permission=kwargs.pop('permission')
        except KeyError:
            print("Error:{} needs a permission attribute.".format(self.__class__.__name__))
            sys.exit()

        
        super().__init__(*args, **kwargs)
        

    def route(self, rule, **options):   
        def decorator(f):
            # This achieves the same effect as @app.route('/X') @check_permission
            f=self.check_permission(f) 
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def check_permission(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            print("CAN CHECK PERMISSION HERE: "+self.permission)
            return f(*args, **kwargs)

        return decorated

