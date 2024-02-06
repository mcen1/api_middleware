from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Request
from internals.suppress_alerts import suppress_alerts_job
from validators import ipv4
from pydantic import BaseModel
import re
import datetime

router = APIRouter()


class awx_job_class(BaseModel):
    job_name: str
    job_params: dict = {}


@router.post("/suppress_alerts", tags=["Automation - Launch Suppress Alerts AWX job"])
async def suppress_alerts(awx_job_info: awx_job_class, request_info: Request, apikey: str = ''):
    """
    validates payload data and launches AWX job
    :param awx_job_info: adds payload variables to awx_job_class
    :param request_info: used to validate request header apikey
    :param apikey: used to validate apikey
    :return: CHG information from the request.
    """
    targets = awx_job_info.job_params
    api_key = apikey

    now = datetime.datetime.now()
    print(f"{now} Launching {awx_job_info.job_name} job with params of {awx_job_info.job_params}...")

    # checks header for API key
    if request_info.headers.get('apikey'):
        api_key = request_info.headers.get('apikey')

    # Returns error if API key is from wrong service
    if not api_key.startswith('servicenow') and not api_key.startswith('team'):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid API Key specified.")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content="Invalid API Key specified.")

    # If we have missing node list, change number, start time, end time, ip address, then kick it back.
    if not targets.get('node_list') or not targets.get('change_number') or not targets.get('start_time') or \
            not targets.get('end_time') or not targets['node_list'][0].get('ip_address'):
        print(f"{now} Validation error for {awx_job_info.job_name}: The data is not complete.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="The data is not complete.  "
                                                                             "Please ensure the following are "
                                                                             "included:  Change Number, Start Time, "
                                                                             "End Time, Node List, and IP Address.")

    # If change number is not valid.
    if not re.match('^CHG\d{7,8}$', targets.get('change_number')):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid Change Number.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid Change Number. "
                                                                             "Please submit a valid Change Number.")

    # If action type is not valid.
    if not targets.get('action_type'):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid Action Type.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid Action Type. "
                                                                            "Please submit a valid Action Type.")
    else:
        if not re.search("suppress", targets.get('action_type'), re.IGNORECASE) and \
                not re.search("resume", targets.get('action_type'), re.IGNORECASE):
            print(f"{now} Validation error for {awx_job_info.job_name}: Invalid Action Type.")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid Action Type. "
                                                                                "Please submit a valid Action Type.")

    # If IP is not valid
    if not ipv4(targets['node_list'][0]['ip_address']):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid IP address.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid IP address. "
                                                                             "Please submit a valid IP address.")

    # If Start Time is not valid
    if not re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', targets.get('start_time')):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid Start Time.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid Start Time. "
                                                                             "Please submit a valid Start Time.")

    # If End Time is not valid
    if not re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', targets.get('end_time')):
        print(f"{now} Validation error for {awx_job_info.job_name}: Invalid End Time.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid End Time. "
                                                                             "Please submit a valid End Time.")

    # Try to suppress alerts within SolarWinds using ansible_util.py
    res = suppress_alerts_job(job_name=awx_job_info.job_name, change_number=targets['change_number'],
                              action_type=targets['action_type'], start_time=targets['start_time'], 
                              end_time=targets['end_time'], node_list=targets['node_list'])

    if res.get('error_code'):  # If error, send it back with error code to be processed.
        return JSONResponse(status_code=res['error_code'], content=res)

    return JSONResponse(status_code=201, content=f"SolarWinds Suppress Alerts job started: {res.get('job_id')}")
