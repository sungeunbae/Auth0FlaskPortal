#!/usr/bin/bash
/home/seb56/py36_devel/bin/uwsgi --http 0.0.0.0:3000 --http-websockets --mount /=server:main_app --master -b 8192 #32768

