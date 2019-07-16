from flask import Flask

import logging
import sys
import os.path

from authenticate import Auth
from constants import ACCESS_LEVELS
from tzlogging import TZLogger

class AuthFlask(Flask):
    def __init__(self, *args, **kwargs):
        self.permission = None
        try:
            self.permission = kwargs.pop("permission")
        except KeyError:
            pass
            #will work out the permission from the directory name

        super().__init__(*args, **kwargs) #create a narmal Flask object

        debug_msg ="" #logger is yet to be created. Add to the string variable for now
        error_msg = ""
        #find out the permission and app name
        if self.permission is None:
            caller = os.path.abspath(sys._getframe().f_back.f_code.co_filename)
            debug_msg +="caller: " + caller + '\n'
            try:
                # stripping the permission part from "./apps/permission/XXXX/__init__.py"
                caller_permission, app_name = (
                    os.path.dirname(caller).split("apps")[-1].split("/")[1:3]
                )
            except IndexError:
                error_msg+="Caller {} has no clue of permission".format(caller) + '\n'
            else:
                if caller_permission in ACCESS_LEVELS:
                    self.permission = caller_permission
                    debug_msg += "Permission:" + self.permission + '\n'
                else:
                    error_msg +="{} is invalid permission.".format(caller_permission) + '\n'
                self.app_name = app_name
        try:
            log_name = "logs/{}_{}.log".format(self.permission, self.app_name)
        except AttributeError: #self.app_name may not have been set
            log_name = "logs/{}_temp.log".format(self.permission)

        #add a logger
        self.logger=TZLogger(__name__, log_name).getLogger()

        if debug_msg:
            self.logger.debug(debug_msg)
        if error_msg:
            self.logger.error(error_msg)
            sys.exit()

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
                self.logger.warning(
                    "Duplicate possibly harmless endpoints:"
                    + str(rule)
                    + " "
                    + str(options)
                )
            return f

        return decorator
