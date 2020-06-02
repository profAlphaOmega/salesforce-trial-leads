#!/usr/bin/env python
#
from flask import request
from src.utils import *
from src.exceptions.api_exceptions import *
from src.gcp import GCP
from src.redis import Redis
from src.constants import *
from simple_salesforce import Salesforce
from src.logger import Logging

import datetime
import redis
import ast
import json

gcp = GCP()
r = Redis()


class LeadsV2:
    """
    LeadsV2 Data Insertion Class
    """
    def __init__(self):
        self.required_fields = [
            'Email',
            'REDACTED',
            'FirstName',
            'LastName',
        ]
        return

    def create(self):
        """API for V2 salesforce leads"""
        log = Logging(category="v2_create")
        log.info("Enter V2 salesforce_leads")

        #  get formData
        formData = request.json
        if not formData:
            raise BadRequestError

        #  log formData
        log.info(f"FORM DATA: {formData}")

        #  exclude all runscope tests
        if 'REDACTED' in formData.get("Email"):
            log.info(f"RUNSCOPE EXCLUSION: {formData}")
            return make_resp(msg="OK", status_code=200)

        #  standardize tenantId parameter in case someone sends a different spelling (legacy)
        if formData.get("tenantId"):
            formData["REDACTED"] = formData["tenantId"]
            formData.pop("tenantId")

        # Required Field Check
        if not required_fields_check(requires=self.required_fields, payload=formData):
            raise ItemNotFoundError

        #  salesforce_id
        timestamp = datetime.datetime.now().isoformat()
        salesforce_id = 123
        # try:
        #     salesforce_id = f"{formData['Tenant_ID__c']}_{timestamp}"
        # except:
        #     raise ItemNotFoundError

        formData = json.dumps(formData)
        r.RQ.set(f'salesforce-{salesforce_id}', formData)

        response = gcp.create_task(params={"salesforce_id": salesforce_id, "timestamp": timestamp}, url='/redacted/path/salesforce/v2', queue=GCP_V2_QUEUE)

        log.info(f"V2 - Created task for {salesforce_id} at {timestamp}: Response - {response}")
        return make_resp(msg="OK", status_code=200)

    def handler(self):
        """Task handler for salesforce leads"""
        log = Logging(category="v2_handler")
        log.info("V2 Handler, requesting paramters...")

        #  get ids
        # salesforce_id = request.params.get("salesforce_id")
        # timestamp = request.params.get("timestamp")
        params = ast.literal_eval(request.get_data(as_text=True)) or '(empty params)'
        log.info(f"Params: {params}")

        salesforce_id = params.get("salesforce_id")
        timestamp = params.get("timestamp")


        log.info(f"V2 - Enter: salesforce_id: {salesforce_id}")

        #  confirm params exist
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

        log.info(f"V2 - Found Payload: {payload}")

        #  Simple Salesforce Initialization
        ss = Salesforce(
                username=SALESFORCE_USERNAME,
                password=SALESFORCE_PASSWORD,
                security_token=SALESFORCE_TOKEN
            )

        log.info(f"V2 - leadStatus: Pending, sfLoginResult: {ss}")

        # Required Field Check
        if not required_fields_check(requires=self.required_fields, payload=payload):
            raise ItemNotFoundError

        # Inject Fields
        payload["Company"] = payload["REDACTED"]
        payload['REDACTED'] = golden_ticket()
        payload["REDACTED"] = payload.get("REDACTED", "V2 Sales")
        payload["REDACTED"] = payload.get("REDACTED", "v2")
        payload["REDACTED"] = payload.get("REDACTED", '01270000000Q4tB')
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
        result = ss.Lead.create(lead, {"AssignmentRuleHeader": "01Q70000000Ux1I"})

        if not result.success:
            log.error(f"V2 Lead Status: Attempted, sfResponseObj: {result}")
            raise BadRequestError
        
        return make_resp(msg="OK", status_code=200)
