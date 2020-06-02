#!/usr/bin/env python
#
# Copyright 2019 Volusion, LLC (http://www.volusion.com)
#
# Coded by Brad Bolander & Phil Manno, April 2019

from src.constants import *
from src.exceptions.api_exceptions import *

import redis

class Redis:
    def __init__(self):
        try:
            self.RQ = redis.Redis(host=REDIS_HOST_URL, port=REDIS_PORT, password=REDIS_PASSWORD)
        except BadRequestError as e:
            Logging.insert("redis", e, "error")

        return