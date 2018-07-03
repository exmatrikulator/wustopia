#!/bin/bash
set -e


if [ -z "$@" ]; then

    if [ ! -f /app/config/config.py ]; then
        cp /app/config.py.example /app/config/config.py
    fi


    #if app is mounted, Dockerfile is available
    if [ -f Dockerfile ]; then
        pip3 install -r requirements.txt
    fi

    #run translation
    python3 manage.py pybabel

    #chicken and egg problem: checking needs migrations
    #wait for postgres
    # until python3 manage.py db current > /dev/null ; do
    #   >&2 echo "Postgres is unavailable - sleeping"
    #   sleep 1
    # done

    # if /app/migrations is empty init database
    if [ ! -f /app/migrations/README ]; then
        python3 manage.py db init -d /tmp/migrations 2> /dev/null
        mv /tmp/migrations/* /app/migrations
    fi


    python3 manage.py db migrate
    python3 manage.py db upgrade
    python3 manage.py imoprtInitData
    python3 manage.py generate_asset

    #if app is mounted, Dockerfile is available
    if [ -f Dockerfile ]; then
        echo "Running app in debug mode!"
        python3 manage.py runserver -h 0.0.0.0 -p 80
    else
        echo "Running app in production mode!"
        nginx && uwsgi --ini /app/app.ini
    fi
fi

exec "$@"
