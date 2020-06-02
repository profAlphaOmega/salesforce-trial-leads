#!/usr/bin/env python
#
# Copyright 2019 Volusion, LLC (http://www.volusion.com)
#
# Coded by Brad Bolander & Phil Manno, April 2019
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from src.constants import *

import os
import json
import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDENTIALS
taskQueue = tasks_v2.CloudTasksClient()


class GCP:
    def __init__(self):
        self.project = GCP_PROJECT
        self.location = GCP_LOCATION
        return

    def create_task(self, params, url, queue):

        parent = taskQueue.queue_path(self.project, self.location, queue)

        task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': 'POST',
                'relative_uri': url
            }
        }       
        
        # in_seconds is the minimum amount of time we want GCP to wait before sending the task to be executed
        in_seconds = 10
        if in_seconds is not None:
            # Convert "seconds from now" into an rfc3339 datetime string.
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            task['schedule_time'] = timestamp

        s = json.dumps(params)
        task['app_engine_http_request']['body'] = s.encode('utf-8')
        
        return taskQueue.create_task(parent, task)
