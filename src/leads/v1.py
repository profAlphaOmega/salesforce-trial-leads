#!/usr/bin/env python

from flask import request
from src.utils import *
from src.exceptions.api_exceptions import *
from src.gcp import GCP
from src.redis import Redis
from src.constants import *
from simple_salesforce import Salesforce
from src.logger import Logging

import datetime
import ast
import json


gcp = GCP()
r = Redis()


class LeadsV1:
    """V1 Leads Data Insertion Class"""
    def __init__(self):
        self.required_fields = [
            'emailAddress',  # TODO: standardize this on the front end -- salesforce name for this -- Email
            'Company',  # TODO: standardize this on the front end
            'FirstName',
            'LastName'
        ]
        return

    def create(self):
        """API for V1 salesforce leads"""
        log = Logging(category="v1_create")
        log.info("enter create method")

        #  get formData
        formData = request.json
        if not formData:
            raise BadRequestError

        #  log formData
        log.info(f"FORM DATA: {formData}")

        #  exclude all runscope tests
        if 'keynote' in formData.get("Email"):
            log.info(f"Keynote EXCLUSION: {formData}")
            return make_resp(msg="OK", status_code=200)

        # Required Field Check
        # TODO: this will fail right now without standardizing Company
        if not required_fields_check(requires=self.required_fields, payload=formData):
            raise ItemNotFoundError


        log.info(f"V1 - FORMDATA: {formData}")

        # Convert formData format to work with Redis
        formData = json.dumps(formData)

        #  set formData into redis
        r.RQ.set(f"salesforce-{salesforce_id}", formData)
        
        # Create the GCP task
        response = gcp.create_task(params={"salesforce_id": salesforce_id, "timestamp": timestamp}, url='/redacted/path/salesforce', queue=GCP_V1_QUEUE)

        log.info(f"V1 - Created task for {salesforce_id} at {timestamp}: Response - {response}")

        return make_resp(msg="OK", status_code=200)

    def handler(self):
        """Task handler for salesforce leads"""
        log = Logging(category="v1_handler")
        log.info("V1 Handler, requesting paramters...")

        #  get ids
        params = ast.literal_eval(request.get_data(as_text=True)) or '(empty params)'
        log.info(f"Params: {params}")

        salesforce_id = params.get("salesforce_id")
        timestamp = params.get("timestamp")

        log.info(f"V1 - Enter. salesforce_id: {salesforce_id}, TimeStamp: {timestamp}")

        #  confirm ids exist
        if not timestamp:
            raise ItemNotFoundError
        if not salesforce_id:
            raise ItemNotFoundError

        #  get formData
        payload = json.loads(r.RQ.get(f"salesforce-{salesforce_id}"))
        log.info(f"Payload: {payload}")

        if not payload:
            log.error(f"salesforce-{salesforce_id} not found")
            raise ItemNotFoundError

        log.info(f"V1 - Payload Found: {payload}")

        #  Simple Salesforce Initialization
        ss = Salesforce(
                username=SALESFORCE_USERNAME,
                password=SALESFORCE_PASSWORD, 
                security_token=SALESFORCE_TOKEN
            )

        log.info(f"V1 - leadStatus: Pending, sfLoginResult: {ss}")

        # Required Field Check
        if not required_fields_check(requires=self.required_fields, payload=payload):
            raise ItemNotFoundError

        # Inject Fields
        payload["REDACTED"] = payload.get("REDACTED", "V1 Sales")
        payload["REDACTED"] = payload.get("REDACTED", "v1")
        payload["RecordTypeID"] = payload.get("RecordTypeID", '01270000000Q4tB')
        if str(payload.get("REDACTED")) == "REDACTED":
            payload["RecordTypeID"] = '01270000000Q54S'

        # Construct lead dict and truncate everything to 100 chars
        # By now all required fields and injected fields should be vetted and everything else is optional
        # if not a valid SF field name the create process will surface an error
        lead = dict()
        for k, v in payload.items():
            lead[k] = v[:100]
        log.info(f"Lead: {lead}")

        #  create a lead obj
        result = ss.Lead.create(lead,{"AssignmentRuleHeader": "01Q70000000Ux1I"})

        log.info(f"Result: {result}")

        if not result.success:
            log.error(f"V1 - leadStatus: Attempted, sfResponseObj: {result}")
            raise BadRequestError

        return make_resp(msg="OK", status_code=200)
