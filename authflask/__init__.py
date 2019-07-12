from flask import Flask

import sys
import os.path

from authenticate import Auth
from constants import ACCESS_LEVELS


class AuthFlask(Flask):
    def __init__(self, *args, **kwargs):
        try:
            self.permission = kwargs.pop("permission")
        except KeyError:
            caller = os.path.abspath(sys._getframe().f_back.f_code.co_filename)
            print("caller: " + caller)
            try:
                # stripping the permission part from "./apps/permission/XXXX/__init__.py"
                caller_permission = (
                    os.path.dirname(caller).split("apps")[-1].split("/")[1]
                )
            except IndexError:
                print("Error: Caller {} has no clue of permission".format(caller))
                sys.exit()
            else:
                if caller_permission in ACCESS_LEVELS:
                    self.permission = caller_permission
                    print("Permission:" + self.permission)
                else:
                    print("Error: {} is invalid permission.".format(caller_permission))
                    sys.exit()

        super().__init__(*args, **kwargs)
        self.secret_key = Auth.SECRET_KEY

    def route(self, rule, **options):
        def decorator(f):
            # This achieves the same effect as @app.route('/X') @requires_scope(xxx)

            if self.permission == "stable":
                pass
            elif self.permission == "admin":
                f = Auth.requires_admin(f)
            else:
                f = Auth.requires_scope("access:" + self.permission)(f)

            endpoint = options.pop("endpoint", None)
            try:
                self.add_url_rule(rule, endpoint, f, **options)
            except AssertionError:
                print(
                    "WARNING: Duplicate possibly harmless endpoints:"
                    + str(rule)
                    + " "
                    + str(options)
                )
            return f

        return decorator
