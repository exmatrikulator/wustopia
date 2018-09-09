#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
from rq import Worker, Queue, Connection
from webapp import app

listen = ['update_places','achievements']

conn = redis.from_url(app.config['REDIS_URI'])

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
