#!/usr/bin/bash
export PYTHONPATH=$PYTHONPATH:/home/seb56/local/flask_dev
/home/seb56/py36_devel/bin/uwsgi --http 0.0.0.0:3000 --http-websockets --mount /=server:main_app --master -b 8192 #32768

