#!/usr/bin/bash
/home/seb56/py36_devel/bin/uwsgi --http :3000 --http-websockets --mount /=server:app --master
