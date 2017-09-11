#!/bin/bash
set -e


if [ -z "$@" ]; then

    if [ ! -f /app/config/config.py ]; then
        cp /app/config.py.example /app/config/config.py
    fi

    if [ ! -f /app/migrations/README ]; then
        python3 manage.py db init -d /tmp/migrations 2> /dev/null
        mv /tmp/migrations/* /app/migrations
    fi

    #wait for postgres
    until python3 manage.py db current > /dev/null 2>&1 ; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 1
    done


    python3 manage.py db migrate
    python3 manage.py db upgrade
    python3 manage.py imoprtInitData

    #if app is mounted, Dockerfile is available
    if [ -f Dockerfile ]; then
        echo "Running app in debug mode!"
        python3 app.py
    else
        echo "Running app in production mode!"
        nginx && uwsgi --ini /app/app.ini
    fi
fi

exec "$@"
