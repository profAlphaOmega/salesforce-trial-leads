#!/usr/bin/env python
#
# Copyright 2019 Volusion, LLC (http://www.volusion.com)
#
# Coded by Brad Bolander & Phil Manno, April 2019
from flask import jsonify
import re
import random


def make_resp(msg, status_code):
    """builds the return response in json format"""
    response = jsonify(message=msg)
    response.status_code = status_code
    return response


def golden_ticket():
    # Needed for Zapier Call Integration for Sales Reps
    golden_ticket = '0000'
    while not re.findall(r'\D', golden_ticket):
        golden_ticket = ''.join(
            random.choice('123456789ABCDEFGHIJKMNPQRSTWXY') for i in range(random.randint(4, 4)))
    return golden_ticket


def required_fields_check(requires=None, payload=None):
    for r in requires:
        if r not in payload:
            return False
        return True

