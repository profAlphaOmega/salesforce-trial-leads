#!/usr/bin/env python

from datetime import datetime
from flask import request
from src.utils import *
from src.gcp import GCP
from src.redis import Redis
from src.exceptions.api_exceptions import *
from src.constants import *
from src.logger import Logging
from simple_salesforce import Salesforce

import json
import logging
import redis

gcp = GCP()
r = Redis()


class LeadsUpdateV2:
    def __init__(self):
        self.required_fields = [
            'REDACTED',
        ]
        return

    def update(self):
        '''V2 Update Method'''
        log = Logging(category="v2_update")
        log.info("Enter V2 Updater...")

        # get payload
        payload = request.json
        if not payload:
            raise ItemNotFoundError

        #  standardize tenantId parameter in case someone sends a different spelling (legacy)
        if payload.get("tenantId"):
            payload["REDACTED"] = payload["tenantId"]
            payload.pop("tenantId")

        # Required Field Check
        if not required_fields_check(requires=self.required_fields, payload=payload):
            raise ItemNotFoundError

        # salesforce_id
        timestamp = datetime.now().isoformat()
        salesforce_id = 123
        # try:
        #     salesforce_id = f"{payload['Tenant_ID__c']}_{timestamp}"
        # except:
        #     raise ItemNotFoundError

        payload = json.dumps(payload)
        r.RQ.set(f'salesforce-{salesforce_id}', payload)

        response = gcp.create_task(params={"salesforce_id": salesforce_id, "timestamp": timestamp}, url='/redacted/path/salesforce/v2', queue=GCP_V2_UPDATE_QUEUE)

        log.info(f"V2 Update - Created task for {salesforce_id} at {timestamp}: Response - {response}")
        return make_resp(msg="OK", status_code=200)

    def handler(self):
        '''Task handler for salesforce leads'''
        log = Logging(category="v2_update_handler")
        log.info("Enter V2 Update Handler, requesting paramters...")

         # Get ids
        salesforce_id = request.params.get("salesforce_update_id")
        timestamp = request.params.get("timestamp")

        # Confirm ids exist
        if not timestamp:
            raise BadRequestError
        if not salesforce_id:
            raise BadRequestError

        log.info(f"V2 Update - Enter salesforce_update_id: {salesforce_id}, TimeStamp: {timestamp}")

        # Get payload
        # payload = memcache.get(f"salesforce-{salesforce_id}")
        payload = r.get(f"salesforce-{salesforce_id}")
        if not payload:
            log.error(f"v2-salesforce-updater-{salesforce_id}")
            raise ItemNotFoundError
        log.info(f"V2 - Found Paylod: {payload}")

        # Required Field Check
        if not required_fields_check(requires=self.required_fields, payload=payload):
            raise ItemNotFoundError

        #  Simple Salesforce Initialization
        ss = Salesforce(
                username=SALESFORCE_USERNAME,
                password=SALESFORCE_PASSWORD,
                security_token=SALESFORCE_TOKEN
            )
        log.info(f"SF LoginResult: {ss}")

        # Find lead
        query_result = ss.query(f"SELECT Id FROM REDACTED WHERE REDACTED='{payload['REDACTED']}'")
        log.info(f"V2 Update - Query Result: {query_result}")

        # No results found
        if query_result.size == 0:
            log.error(f"V2 Update - No record found for {payload['REDACTED']}")
            raise ItemNotFoundError

        # get lead id
        sf_lead_id = query_result.records[0]["Id"]

        #  create a lead obj
        lead = ss.Lead.create({
            "Id": sf_lead_id
        })

        # remove tenantId from being updated
        payload.pop("REDACTED")

        # insert updated attributes and values into lead object
        for k, v in payload.items():
            lead[k] = v

        # update lead
        result = ss.update(lead)

        # handle result
        if not result.success:
            log.error(f"V2 Update - leadUpdateStatus: Attempted, sfResponseObj: {result}")
            raise BadRequestError

        return make_resp(msg="OK", status_code=200)
