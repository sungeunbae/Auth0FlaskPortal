#!/bin/bash
export ROOT=/home/ec2-user/Auth0FlaskPortal
export PYTHONPATH=$PYTHONPATH:$ROOT:$ROOT/apps/devel/seistech:$ROOT/apps/devel/seistech/seistech_web
#export PYTHONPATH=$PYTHONPATH:$ROOT:$ROOT/apps/devel
/home/ec2-user/py3env/bin/uwsgi --http 0.0.0.0:5000 --http-websockets --plugins python37,gevent --gevent 1000 --mount /=server:main_app --master -b 8192 --logger file:logfile=logs/uwsgi.log,maxsize=200000 --socket /run/seistech.sock --chmod-socket=777 --vacuum --die-on-term #32768


