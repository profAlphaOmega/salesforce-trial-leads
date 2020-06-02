"""This module contains the flask api routing"""
from flask import Blueprint
from flask_cors import CORS
from src.leads.v1 import LeadsV1
from src.leads.v2 import LeadsV2
from src.leads.v2_update import LeadsUpdateV2

# Setup Blueprint and run through CORS
api = Blueprint('api', __name__, url_prefix='/')
CORS(api)

# Instantiate Leads classes
leadsv1 = LeadsV1()
leadsv2 = LeadsV2()
leadsUpdateV2 = LeadsUpdateV2()


# Leads Routes
@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def create_v1_lead():
    return leadsv1.create()

@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def create_v2_lead():
    return leadsv2.create()

@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def update_v2_lead():
    return leadsUpdateV2.update()

# Task Routes
@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def handle_v1_lead():
    return leadsv1.handler()

@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def handle_v2_lead():
    return leadsv2.handler()

@api.route('/redacted/path/salesforce', methods=['OPTIONS', 'POST'])
def handle_v2_lead_update():
    return leadsUpdateV2.handler()

