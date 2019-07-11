#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/home/seb56/local/app_dispatch:/home/seb56/local/app_dispatch/apps/devel/seistech:/home/seb56/local/app_dispatch/apps/devel/seistech/seistech_web
#export PYTHONPATH=$PYTHONPATH:/home/seb56/local/app_dispatch:/home/seb56/local/app_dispatch/apps/devel
/home/seb56/py36_devel/bin/uwsgi --http 0.0.0.0:3000 --http-websockets --plugins python,gevent --gevent 100 --mount /=server:main_app --master -b 8192 #32768
#/home/seb56/py36_devel/bin/uwsgi --http 0.0.0.0:3001 --http-websockets --mount /=server:main_app --master -b 8192 #32768



