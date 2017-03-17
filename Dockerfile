FROM jazzdd/alpine-flask:python3

#build tools for Flask-SQLAlchemy-->cffi
RUN apk add --no-cache python3-dev libffi-dev alpine-sdk postgresql-dev
