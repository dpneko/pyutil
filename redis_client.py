#!/usr/bin/env python
# -*- coding:utf8 -*-

import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)   #实现一个连接池

r = redis.Redis(connection_pool=pool)
keys = r.keys(pattern='*')
count = 0
total = len(keys)
for key in keys:
    r.delete(key)
    count += 1
    if count/1000 == 0:
        print(f"{count}/{total}")
