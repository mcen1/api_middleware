from fastapi import HTTPException, status
from internals.k8s_secret import k8s_secret
from requests import post, packages
from json import loads, dumps
from urllib.parse import quote
from internals.log import log

packages.urllib3.disable_warnings() 

class AWX():
    def __init__(self):
        self._awx_access_token = None
        self._awx_host = None
        self.awx_instance = None

    def launch_awx_job(self, request, endpoint: str, payload = {}):
    
        #get infrastructure secret from k8s
        self._awx_access_token = k8s_secret.get_awx_access_token()
        self._awx_host = k8s_secret.get_awx_host_data()[0]
        self.awx_instance = k8s_secret.get_awx_host_data()[1]
        if not self._awx_access_token or not self._awx_host or not self.awx_instance :
            log.critical(
                f'{{'
                f'"module":"/internals/awx",'
                f'"action":"launch_awx_job",'
                f'"message":"The required k8s secret variables `awx_access_token`, `awx_host` or `awx_instance` could not be found thus the request was aborted."'
                f'}}'
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = ( 
                    f"The required k8s secret variables could not be found thus the request was aborted."
                    f"Please contact the ITOA team for assistance."
                )
            )
        client_host = request.client.host
        log.info(
            f'{{'
            f'"module":"/internals/awx",'
            f'"action":"launch_awx_job",'
            f'"call_to":"/{ endpoint }/launch/",'
            f'"call_from":"{ client_host }"'
            f'}}'
        )
        job_template = quote(endpoint)
        headers = { 'Authorization': f'Bearer { str(self._awx_access_token) }', 'Content-type': 'application/json' }
        url = f"https://{ str(self._awx_host) }/api/v2/job_templates/{ job_template }/launch/"
        try:
            if payload:
                request = post(url, headers=headers, verify=False, data=dumps(payload))
            else:
                request = post(url, headers=headers, verify=False)
        except exception as exception:
            log.critical(
                f'{{'
                f'"module":"/internals/awx",'
                f'"action":"launch_awx_job",'
                f'"call_to":"{ url }",'
                f'"call_from":"/{ endpoint }/launch/",'
                f'"message":"An error occurred when trying to launch the AWX job thus the request was aborted. Exception: `{ exception }`."'
                f'}}'
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = ( 
                    f"An error occurred when trying to launch the AWX job thus the request was aborted. "
                    f"Please contact the ITOA team for assistance."
                )
            )
        if request.status_code not in [200, 201]:
            log.critical(
                f'{{'
                f'"module":"/internals/awx",'
                f'"action":"awx_job_launch_result",'
                f'"call_to":"{ url }",'
                f'"call_from":"/{ endpoint }/launch/",'
                f'"message":"Status code: `{ request.status_code }` with payload: `{ loads(request.content) }`."'
                f'}}'
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = ( 
                    f"An error occurred when trying to launch the AWX job as the incorrect status code was received from AWX thus the request was aborted."
                    f"Please contact the ITOA team for assistance."
                )
            )
        response_payload = loads(request.content)
        job_id = response_payload.get('id')
        job_status = response_payload.get('status')
        log.info(
            f'{{'
            f'"module":"/internals/awx",'
            f'"action":"awx_job_launch_result",'
            f'"call_to":"{ url }",'
            f'"call_from":"/{ endpoint }/launch/",'
            f'"message":"AWX job started id: { job_id }. AWX response status code: `{ request.status_code }`."'
            f'}}'
        )
        return { "job_template":f"{ job_template }", "job_id":f"{ job_id }", "job_status":f"{ job_status }"}
            


    #Ensures payload going to AWX matched the job templates required payload
    def construct_awx_payload(self, data, required_keys: list):
        payload = {}
        if data:
            extra_vars = data.get('extra_vars')
            if extra_vars:
                #check if correct keys exist in the request body
                payload = {
                    "extra_vars": {}
                }
                for key,value in extra_vars.items():
                    if key in required_keys:
                        payload['extra_vars'][str(key)] = str(value)
        return payload


#Create/Get AWX object
awx = AWX()
